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
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()

            cursor.execute("SELECT * FROM cars WHERE user_id = %s", (user_id,))
            cars_data = cursor.fetchall()

            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                               SELECT
                                    permits.*,
                                    parking_lots.name AS lot_name,
                                    cars.make as car_make,
                                    cars.model as car_model,
                                    cars.plate as car_plate
                                FROM permits
                                JOIN parking_lots
                                    ON permits.parking_lot_id = parking_lots.id
                                JOIN cars
                                   on permits.car_id = cars.id
                                WHERE permits.user_id = %s
                                    AND permits.end_time > NOW()
                               """, (user_id,))

                user_permits = cursor.fetchall()

    #send the data to the frontend!

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user_data,
            "cars": cars_data,
            "permits": user_permits
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








##################

#EDIT CARS!!

##################

@app.get("/cars/edit", response_class=HTMLResponse)
def editCar(request: Request, id: int):
    try:
        user_id = get_current_user(request)

    # If it's not a valid login, it sends the user back to the home page...
    except HTTPException:
        return RedirectResponse("/")

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM cars WHERE id = %s AND user_id = %s", (id,user_id))
            user_cars = cursor.fetchone()

    #Making sure the user actually owns the car.
    if user_cars is None:
        return RedirectResponse("/")

    return templates.TemplateResponse(
        "cars/edit.html",
        {
            "request": request,
            "car": user_cars
        }
    )


@app.post("/updateCar")
def updateCar(request: Request, make: str = Form(...), model: str = Form(...), year: int = Form(...), plate: str = Form(...), color: str = Form(...), car_id: int = Form(...)):
    print("update car")

    try:
        user_id = get_current_user(request)
    except:
        return RedirectResponse("/")

    if int(year) > 2030 or int(year) < 1900:
        return {"success": False, "message": "Year should be between 1900-2030!" }

    if len(make) > 50 or len(model) > 50 or len(color) > 30 or len(plate) > 15:
        return {"success": False, "message": "Please put the appropriate information!" }

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """UPDATE cars
                SET
                    make = %s,
                    model = %s,
                    year = %s,
                    plate = %s,
                    color = %s
                WHERE id = %s AND user_id = %s""",
                (make, model, year, plate, color, car_id, user_id))

            conn.commit()

    if cursor.rowcount == 0:
        return {"success": False, "message": "Update failed, because you changed nothing!"}

    return {"success": True, "message": "Car was updated successfully!" }

@app.post("/deleteCar")
def updateCar(request: Request, car_id: int = Form(...)):
    try:
        user_id = get_current_user(request)
    except:
        return RedirectResponse("/")

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM cars WHERE id = %s AND user_id = %s", (car_id, user_id))

            conn.commit()

    if cursor.rowcount == 0:
        return {"success": False, "message": "Update failed, because you changed nothing!"}

    return {"success": True, "message": "Car was updated successfully!" }

@app.post("/addCar")
def addCar(request: Request):
    try:
        user_id = get_current_user(request)
    except:
        return RedirectResponse("/")

    with get_db() as conn:
        with conn.cursor() as cursor:
            #Grab all users cars..
            cursor.execute("SELECT * FROM cars WHERE user_id = %s", (user_id,))
            user_cars = cursor.fetchall()

            if len(user_cars) > 9:
                return {"success": False, "message": "You may only have 10 cars!" }

            #Adds the car with default inputs.
            cursor.execute("INSERT INTO cars (user_id, make, model, plate, year)"
                           "VALUES (%s, %s, %s, CONCAT('TEMP',UNIX_TIMESTAMP()), 2000);", (user_id, "New", "Car"))

            conn.commit()

    if cursor.rowcount == 0:
        return {"success": False, "message": "Update failed, because you changed nothing!"}

    return {"success": True, "message": "Car was updated successfully!" }

@app.get("/api/spots")
def get_spots(request: Request):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM parking_lots")
            rows = cursor.fetchall()

    return [
        {"name": r[1], "lat": r[2], "lng": r[3], "cost_hr": r[4], "cost_day": r[4]*3, "cost_month": r[5], "id": r[0]}
        for r in rows
    ]



############################

# PARKING LOT

############################

@app.get("/cars/parking_lot", response_class=HTMLResponse)
def parking_lot(request: Request, id: int):

    try:
        user_id = get_current_user(request)
    except HTTPException:
        return RedirectResponse("/")

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM parking_lots WHERE id = %s", (id,))
            parking_lot = cursor.fetchone()
            cursor.execute("SELECT * FROM cars WHERE user_id = %s", (user_id,))
            user_cars = cursor.fetchall()

    if (parking_lot is None):
        return RedirectResponse("/")

    return templates.TemplateResponse(
        "cars/parking_lot.html",
        {
            "request": request,
            "parking_lot": parking_lot,
            "user_cars": user_cars
        }
    )


@app.post("/pay")
def pay_lot(request: Request, lot_id: int = Form(...), car: int = Form(...), pass_type: str = Form(...), hours: float = Form(...), days: int = Form(...), months: int = Form(...)):
    try:
        user_id = get_current_user(request)
    except HTTPException:
        return RedirectResponse("/")

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM cars WHERE user_id = %s and id = %s", (user_id,car))
            rows = cursor.fetchone()
            cursor.execute("SELECT cost_hr, cost_month FROM parking_lots WHERE id = %s", (lot_id,))
            prices = cursor.fetchone()

            if rows is not None:
                if pass_type == "hour":
                    if hours >= 0.5:
                        price = prices[0] * hours
                        hours = hours * 60 * 60

                        successful_payment(user_id, car, lot_id, hours, "hourly", price)
                        return {"success": True, "message": "Payment was successful!" }

                if pass_type == "daily":
                    if days > 0:
                        price = (prices[0] * 3) * days
                        days = days * 24 * 60 * 60

                        successful_payment(user_id, car, lot_id, days, "daily", price)
                        return {"success": True, "message": "Payment was successful!"}

                if pass_type == "month":
                    if months > 0:
                        price = prices[1] * months
                        months = months * 30 * 24 * 60 * 60

                        successful_payment(user_id, car, lot_id, months, "monthly", price)
                        return {"success": True, "message": "Payment was successful!"}



    return {"success": False, "message": "Error...." }

def successful_payment(user_id: int, car: int, lot_id: int, seconds: float, pass_type: str, price: float):

    price = (price * 1.04) + 0.25

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO permits (user_id, car_id, parking_lot_id, permit_type, end_time, price) "
                "VALUES (%s, %s, %s, %s, DATE_ADD(NOW(), INTERVAL %s SECOND), %s);", (user_id, car, lot_id, pass_type, seconds, price,))

            conn.commit()




