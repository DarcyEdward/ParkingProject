from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

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

###################


@app.post("/register")
def register(username: str = Form(...), password: str = Form(...), password2: str = Form(...)):

    if password != password2:
        raise HTTPException(status_code=303, detail="Passwords did not match.")

    if len(username) < 5 or len(password) < 5:
        raise HTTPException(status_code=304, detail="All inputs are not 5 characters or more.")











    return {"success": True}

