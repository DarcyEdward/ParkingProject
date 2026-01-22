from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import re

from starlette.responses import RedirectResponse

#STARTING SERVER
app = FastAPI()

# Determine project root
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Serve frontend files
app.mount("/static", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

#Send everyone to index.html
@app.get("/", response_class=HTMLResponse)
def index():
    with open(FRONTEND_DIR / "index.html") as f:
        return f.read()

##################


@app.post("/register")
def register(email: str = Form(...), password: str = Form(...), password2: str = Form(...)):

    #Checking if legit password.
    if password != password2:
        return {"success": False,"message": "Passwords must match!" }
    if len(password) < 5:
        return {"success": False, "message": "Password must be at least 5 characters!" }

    #Checking if it's a legit email.
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return {"success": False, "message": "Email must be a valid email..."}


    #TODO: adding the user to the database here.
    





    return {"success": True,"message": "User created successfully." }

