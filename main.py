from fastapi import FastAPI, Request, Form, HTTPException, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import secrets
from pathlib import Path
from database import Database, get_database
from contextlib import asynccontextmanager
import os

# Check if running on Vercel
IS_VERCEL = os.getenv('VERCEL') == '1'

if not IS_VERCEL:
    # Use lifespan for local development
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        await Database.connect_db()
        yield
        # Shutdown
        await Database.close_db()
    
    app = FastAPI(lifespan=lifespan)
else:
    # No lifespan for serverless - connection managed per request
    app = FastAPI()

# Setup templates directory - use absolute path for Vercel
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Simple in-memory storage for sessions (you can move this to MongoDB too if needed)
sessions = {}

async def get_credentials_collection():
    """Get credentials collection from MongoDB"""
    db = await get_database()
    return db.credentials

async def get_api_state_collection():
    """Get API state collection from MongoDB"""
    db = await get_database()
    return db.api_state

async def verify_session(session_id: str = Cookie(None)):
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return session_id

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    credentials_col = await get_credentials_collection()
    user = await credentials_col.find_one({"username": username})
    
    if user and user.get("password") == password:
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
    await verify_session(session_id)
    
    api_state_col = await get_api_state_collection()
    state = await api_state_col.find_one({"_id": "current_state"})
    
    if not state:
        # Initialize default state if not exists
        state = {"_id": "current_state", "status": "off", "message": "API is currently disabled"}
        await api_state_col.insert_one(state)
    
    return templates.TemplateResponse("main.html", {
        "request": request,
        "status": state["status"],
        "message": state["message"]
    })

@app.post("/toggle")
async def toggle_status(request: Request, session_id: str = Cookie(None)):
    await verify_session(session_id)
    data = await request.json()
    
    api_state_col = await get_api_state_collection()
    await api_state_col.update_one(
        {"_id": "current_state"},
        {"$set": {"status": data["status"]}},
        upsert=True
    )
    return {"success": True}

@app.post("/update-message")
async def update_message(request: Request, session_id: str = Cookie(None)):
    await verify_session(session_id)
    data = await request.json()
    
    api_state_col = await get_api_state_collection()
    await api_state_col.update_one(
        {"_id": "current_state"},
        {"$set": {"message": data["message"]}},
        upsert=True
    )
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
    api_state_col = await get_api_state_collection()
    state = await api_state_col.find_one({"_id": "current_state"})
    
    if not state:
        # Return default state if not exists
        return {
            "status": "off",
            "message": "API is currently disabled"
        }
    
    return {
        "status": state["status"],
        "message": state["message"]
    }

