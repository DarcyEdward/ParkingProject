import mysql.connector
from mysql.connector import Error
import re
import bcrypt
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path



app = FastAPI()

#STARTING SERVER
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

#Send everyone to index.html
@app.get("/", response_class=HTMLResponse)
def index():
    with open(FRONTEND_DIR / "index.html") as f:
        return f.read()



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

    # Encrypt the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


    #Login into the SQL

    with get_db() as conn:
        with conn.cursor() as cursor:
            query = "INSERT INTO users (email, password_hash) VALUES (%s, %s)"
            cursor.execute(query, (email, hashed_password))
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
        return {"success": True, "message": "Successfully logged in!" }

    return {"success": False, "message": "Login credentials are invalid. Forgot password?" }
