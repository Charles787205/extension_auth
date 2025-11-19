from fastapi import FastAPI, Request, Form, HTTPException, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import secrets
from pathlib import Path
import os

# Try to import database, fall back to in-memory if it fails
try:
    from database import get_database
    USE_MONGODB = True
except Exception as e:
    print(f"MongoDB not available: {e}")
    USE_MONGODB = False

# Create FastAPI app - simple, no complex lifespan
app = FastAPI()

# Setup templates directory
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# In-memory fallback storage
CREDENTIALS = {"admin": "password"}
sessions = {}
# Don't initialize api_state here - always fetch from MongoDB first
api_state = None

async def get_or_init_api_state():
    """Get API state from MongoDB or initialize in-memory"""
    global api_state
    
    if USE_MONGODB:
        try:
            api_state_col = await get_api_state_collection()
            if api_state_col is not None:
                state = await api_state_col.find_one({"_id": "current_state"})
                if state:
                    return state
                # If no state in MongoDB, initialize it
                default_state = {
                    "_id": "current_state",
                    "status": "off",
                    "message": "API is currently disabled"
                }
                await api_state_col.insert_one(default_state)
                return default_state
        except Exception as e:
            print(f"MongoDB error: {e}")
    
    # Fallback to in-memory
    if api_state is None:
        api_state = {"status": "off", "message": "API is currently disabled"}
    return api_state

async def get_credentials_collection():
    """Get credentials collection from MongoDB"""
    if USE_MONGODB:
        db = await get_database()
        return db.credentials
    return None

async def get_api_state_collection():
    """Get API state collection from MongoDB"""
    if USE_MONGODB:
        db = await get_database()
        return db.api_state
    return None

def verify_session(session_id: str = Cookie(None)):
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return session_id

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    # Try MongoDB first, fall back to in-memory
    if USE_MONGODB:
        try:
            credentials_col = await get_credentials_collection()
            if credentials_col is not None:
                user = await credentials_col.find_one({"username": username})
                if user and user.get("password") == password:
                    session_id = secrets.token_urlsafe(32)
                    sessions[session_id] = username
                    response = RedirectResponse(url="/main", status_code=303)
                    response.set_cookie(key="session_id", value=session_id, httponly=True)
                    return response
        except Exception as e:
            print(f"MongoDB error, falling back to in-memory: {e}")
    
    # Fallback to in-memory
    if username in CREDENTIALS and CREDENTIALS[username] == password:
        session_id = secrets.token_urlsafe(32)
        sessions[session_id] = username
        response = RedirectResponse(url="/main", status_code=303)
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        return response
    
    return templates.TemplateResponse("login.html", {
        "request": request, 
        "error": "Invalid credentials"
    })

@app.get("/main", response_class=HTMLResponse)
async def main_page(request: Request, session_id: str = Cookie(None)):
    verify_session(session_id)
    
    # Always get fresh state from MongoDB (or in-memory fallback)
    state = await get_or_init_api_state()
    
    return templates.TemplateResponse("main.html", {
        "request": request,
        "status": state["status"],
        "message": state["message"]
    })

@app.post("/toggle")
async def toggle_status(request: Request, session_id: str = Cookie(None)):
    verify_session(session_id)
    data = await request.json()
    
    # Try MongoDB first
    if USE_MONGODB:
        try:
            api_state_col = await get_api_state_collection()
            if api_state_col is not None:
                await api_state_col.update_one(
                    {"_id": "current_state"},
                    {"$set": {"status": data["status"]}},
                    upsert=True
                )
                return {"success": True}
        except Exception as e:
            print(f"MongoDB error, using in-memory: {e}")
    
    # Fallback to in-memory
    api_state["status"] = data["status"]
    return {"success": True}

@app.post("/update-message")
async def update_message(request: Request, session_id: str = Cookie(None)):
    verify_session(session_id)
    data = await request.json()
    
    # Try MongoDB first
    if USE_MONGODB:
        try:
            api_state_col = await get_api_state_collection()
            if api_state_col is not None:
                await api_state_col.update_one(
                    {"_id": "current_state"},
                    {"$set": {"message": data["message"]}},
                    upsert=True
                )
                return {"success": True}
        except Exception as e:
            print(f"MongoDB error, using in-memory: {e}")
    
    # Fallback to in-memory
    api_state["message"] = data["message"]
    return {"success": True}

@app.post("/logout")
async def logout(session_id: str = Cookie(None)):
    if session_id in sessions:
        del sessions[session_id]
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="session_id")
    return response

@app.get("/api/status")
async def api_status():
    # Always get fresh state from MongoDB (or in-memory fallback)
    state = await get_or_init_api_state()
    
    return {
        "status": state["status"],
        "message": state["message"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
