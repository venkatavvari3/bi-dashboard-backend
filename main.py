import os
import psycopg2
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import jwt
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
import re
import requests

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

origins = [
    "https://bi-dashboard-frontend-git-main-venkatavvari3s-projects.vercel.app",
    "https://bi-dashboard-frontend.vercel.app",
    "https://bi-dashboard-frontend-venkatavvari3s-projects.vercel.app",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET = os.getenv("SECRET", "CHANGE_ME")
DATABASE_URL = os.getenv("DATABASE_URL")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def get_persona_for_username(username: str, db_conn) -> Optional[str]:
    cur = db_conn.cursor()
    cur.execute("SELECT persona FROM persona_users WHERE username = %s", (username.lower(),))
    row = cur.fetchone()
    cur.close()
    if row:
        return row[0]
    return None

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

class EmailRequest(BaseModel):
    to: str
    message: str
    image: Optional[str] = None

@app.post("/api/email_me")
def email_me(request: EmailRequest, user=Depends(get_current_user)):
    recipient_email = request.to
    if not recipient_email or "@" not in recipient_email:
        raise HTTPException(status_code=400, detail="Valid recipient email is required.")

    msg = MIMEMultipart()
    msg["Subject"] = "Message from BI Dashboard"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient_email
    msg.attach(MIMEText(request.message, "plain"))

    if request.image:
        match = re.match(r"data:image/(?P<ext>\w+);base64,(?P<data>.+)", request.image)
        if match:
            ext = match.group("ext")
            data = match.group("data")
            image_data = base64.b64decode(data)
            part = MIMEBase("image", ext)
            part.set_payload(image_data)
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="image.{ext}"')
            msg.attach(part)
        else:
            print("Image field is not a valid data URL")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.sendmail(EMAIL_ADDRESS, [recipient_email], msg.as_string())
    except Exception as e:
        print(f"Email sending failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email.")

    return {"success": True, "message": "Email sent successfully"}

class User(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    credential: Optional[str] = None

def verify_google_token(token: str) -> Optional[str]:
    try:
        response = requests.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": token})
        data = response.json()
        if response.status_code == 200 and data.get("aud") == GOOGLE_CLIENT_ID:
            return data.get("email")
    except Exception:
        pass
    return None

@app.post("/api/login")
async def login(user: User, db=Depends(get_db)):
    # 1. Traditional username/password login
    if user.username and user.password:
        persona = get_persona_for_username(user.username, db)
        if persona and user.password == "password":
            token = jwt.encode({"sub": user.username, "persona": persona}, SECRET, algorithm="HS256")
            return {"access_token": token}
        raise HTTPException(status_code=401, detail="Auth failed")
    # 2. Google OAuth credential login
    if user.credential:
        user_email = verify_google_token(user.credential)
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid Google token")
        persona = None
        # Optionally map persona for Google users (by prefix, domain, etc.)
        persona = get_persona_for_username(user_email.split('@')[0], db)
        token = jwt.encode({"sub": user_email, "persona": persona}, SECRET, algorithm="HS256")
        return {"access_token": token}
    raise HTTPException(status_code=400, detail="Missing login payload")

@app.get("/api/data")
def get_data(user=Depends(get_current_user), db=Depends(get_db)):
    persona = user.get("persona")
    cur = db.cursor()
    persona_filter = ""
    if persona == "Srini":
        persona_filter = "WHERE s.city = 'New York'"
    elif persona == "Venkat":
        persona_filter = "WHERE s.city = 'San Francisco'"
    query = f"""
        SELECT
            d.date,
            p.product_name,
            p.category,
            s.store_name,
            s.city,
            c.customer_name,
            SUM(f.units_sold) AS units_sold,
            SUM(f.revenue) AS revenue,
            SUM(f.profit) AS profit
        FROM fact_sales f
        JOIN dim_date d ON f.date_id = d.date_id
        JOIN dim_product p ON f.product_id = p.product_id
        JOIN dim_customer c ON f.customer_id = c.customer_id
        JOIN dim_store s ON f.store_id = s.store_id
        {persona_filter}
        GROUP BY d.date, p.product_name, p.category, s.store_name, s.city, c.customer_name
        ORDER BY d.date DESC, p.product_name
        LIMIT 100
    """
    cur.execute(query)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    data = [dict(zip(columns, row)) for row in rows]
    cur.close()
    json_compatible_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_data)

@app.get("/api/products")
def get_products(db=Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT product_id, product_name, category, brand FROM dim_product ORDER BY product_name")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    data = [dict(zip(columns, row)) for row in rows]
    cur.close()
    json_compatible_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_data)

@app.get("/api/stores")
def get_stores(db=Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT store_id, store_name, city, state FROM dim_store ORDER BY store_name")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    data = [dict(zip(columns, row)) for row in rows]
    cur.close()
    json_compatible_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_data)

@app.get("/api/ppdata")
def get_data(user=Depends(get_current_user), db=Depends(get_db)):
    persona = user.get("persona")
    cur = db.cursor()
    persona_filter = ""
    if persona == "Srini":
        persona_filter = "WHERE s.state = 'California'"
    elif persona == "Venkat":
        persona_filter = "WHERE s.state = 'Nevada'"
    query = f"""
        SELECT
            o.orderDate AS date,
            p.SKU AS product_id,
            p.Name AS product_name,
            p.Category AS category,
            s.id AS store_name,
            s.city,
            o.customerId AS customer_name,
            COUNT(oi.SKU) AS units_sold,
            SUM(p.Price) AS revenue,
            SUM(p.Price * 0.3) AS profit  -- Assuming 30% profit margin
        FROM orders o
        JOIN order_items oi ON o.id = oi.orderID
        JOIN products p ON oi.SKU = p.SKU
        JOIN stores s ON o.storeId = s.id
        JOIN customers c ON o.customerId = c.id  -- Optional if you want to enrich customer info
        {persona_filter} -- Optional filter placeholder
        GROUP BY o.orderDate, p.SKU, p.Name, p.Category, s.id, s.city, o.customerId
        ORDER BY o.orderDate DESC, p.Name
        LIMIT 100;
    """
    cur.execute(query)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    data = [dict(zip(columns, row)) for row in rows]
    cur.close()
    json_compatible_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_data)

@app.get("/api/ppproducts")
def get_products(db=Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT SKU AS product_id, Name AS product_name, Category, Size as brand FROM products ORDER BY Name")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    data = [dict(zip(columns, row)) for row in rows]
    cur.close()
    json_compatible_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_data)

@app.get("/api/ppstores")
def get_stores(db=Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT id AS store_id, id AS store_name, city, state FROM stores ORDER BY id")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    data = [dict(zip(columns, row)) for row in rows]
    cur.close()
    json_compatible_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_data)
class ScheduleRequest(BaseModel):
    repeatFrequency: str
    scheduledTime: str
    reportFormat: str
    email: str

@app.post("/api/schedule_report")
def schedule_report(request: ScheduleRequest, user=Depends(get_current_user), db=Depends(get_db)):
    email = user.get("sub")
    cur = db.cursor()

    # Ensure the subscriptions table exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id SERIAL PRIMARY KEY,
            email TEXT NOT NULL,
            repeat_frequency TEXT NOT NULL,
            scheduled_time TEXT NOT NULL,
            report_format TEXT NOT NULL
        )
    """)
    db.commit()

    # Check if a matching subscription already exists
    cur.execute("""
        SELECT 1 FROM subscriptions
        WHERE email = %s AND repeat_frequency = %s AND scheduled_time = %s AND report_format = %s
    """, (request.email, request.repeatFrequency, request.scheduledTime, request.reportFormat))

    if cur.fetchone():
        cur.close()
        return {"message": "Subscription already exists."}

    # Insert new subscription
    cur.execute("""
        INSERT INTO subscriptions (email, repeat_frequency, scheduled_time, report_format)
        VALUES (%s, %s, %s, %s)
    """, (request.email, request.repeatFrequency, request.scheduledTime, request.reportFormat))
    db.commit()
    cur.close()

    return {"message": "Subscription created successfully."}
