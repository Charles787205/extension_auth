from fastapi import FastAPI, Request, Form, HTTPException, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import secrets
from pathlib import Path

app = FastAPI()

# Setup templates directory
templates = Jinja2Templates(directory="templates")

# Simple in-memory storage
CREDENTIALS = {"admin": "password"}  # Change these!
sessions = {}
api_state = {"status": "off", "message": "API is currently disabled"}

def verify_session(session_id: str = Cookie(None)):
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return session_id

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
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
    return templates.TemplateResponse("main.html", {
        "request": request,
        "status": api_state["status"],
        "message": api_state["message"]
    })

@app.post("/toggle")
async def toggle_status(request: Request, session_id: str = Cookie(None)):
    verify_session(session_id)
    data = await request.json()
    api_state["status"] = data["status"]
    return {"success": True}

@app.post("/update-message")
async def update_message(request: Request, session_id: str = Cookie(None)):
    verify_session(session_id)
    data = await request.json()
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
    
    return {
        "status": api_state["status"],
        "message": api_state["message"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)