import mysql.connector
import re
import bcrypt
from fastapi import FastAPI, Form, Depends, Response, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from starlette.responses import JSONResponse

from app.auth import create_access_token, get_current_user



app = FastAPI()
templates = Jinja2Templates(directory="frontend")

#STARTING SERVER
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

#Send everyone to index.html
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    try:
        get_current_user(request)
        return RedirectResponse("/dashboard")
    except HTTPException:
        response = HTMLResponse(
            (FRONTEND_DIR / "index.html").read_text()
        )
        response.delete_cookie("access_token")
        return response

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    try:
        user_id = get_current_user(request)

    #If it's not a valid login, it sends the user back to the home page...
    except HTTPException:
        return RedirectResponse("/")


    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()

            cursor.execute("SELECT * FROM cars WHERE user_id = %s", (user_id,))
            cars_data = cursor.fetchall()

    print(user_data)
    print(cars_data)

    #send the data to the frontend!

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user_data,
            "cars": cars_data
        }
    )


@app.get("/me")
def me(user_id: int = Depends(get_current_user)):
    return {
        "logged_in": True,
        "user_id": user_id
    }

@app.post("/logout")
def me(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/"
    )
    return {"success": True, "message": "Successfully logged out!" }




##################

#SETTING UP MYSQL

##################

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="darcydordoy",
        password="ezParkingPass",
        database="EzParking"
    )


##################

#REGISTRATION FORM

##################


@app.post("/register")
def register(username: str = Form(...), email: str = Form(...), password: str = Form(...), password2: str = Form(...)):


    print(username, email, password, password2)
    #Checking if legit password.
    if password != password2:
        return {"success": False,"message": "Passwords must match!" }
    if len(password) < 5:
        return {"success": False, "message": "Password must be at least 5 characters!" }

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT email FROM users WHERE email = %s", (email,))

            searchEmail = cursor.fetchone()
            if searchEmail is not None:
                conn.commit()
                return {"success": False, "message": "Account with email already exists!" }


    #Checking if it's a legit email.
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return {"success": False, "message": "Email must be a valid email..."}

    # Encrypt the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())



    #Login into the SQL

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", (username, email, hashed_password))
            conn.commit()

            print("The user has been successfully registered!")




    return {"success": True,"message": "User created successfully." }


##################

#LOGIN FORM

##################

@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)):

    #Grab the password hash
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT password_hash FROM users WHERE email = %s", (email,))

            stored_hash = cursor.fetchone()

            if stored_hash is None:
                return {"success": False, "message": "Login credentials are invalid. Forgot password?"}

            if bcrypt.checkpw(password.encode("utf-8"), stored_hash[0].encode("utf-8")):
                #Grab user ID
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                user_id = cursor.fetchone()

                token = create_access_token(user_id[0])

                response = JSONResponse({"success": True, "message": "Successfully logged in!" })
                response.set_cookie(
                    key="access_token",
                    value=token,
                    httponly=True,
                    secure=False,  # True in production (HTTPS)
                    samesite="lax"
                )




                return response

    return {"success": False, "message": "Login credentials are invalid. Forgot password?" }
