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

# For Google token verification
import requests

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

origins = [
    "https://bi-dashboard-frontend-git-main-venkatavvari3s-projects.vercel.app",
    "https://bi-dashboard-frontend.vercel.app",
    "https://bi-dashboard-frontend-60jd5b03f-venkatavvari3s-projects.vercel.app",
    "https://bi-dashboard-frontend-venkatavvari3s-projects.vercel.app",
    "http://localhost:3000",
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
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")  # Set this in your Render env variables

class User(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    credential: Optional[str] = None  # For Google OAuth

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def verify_google_token(token: str) -> Optional[str]:
    """
    Verifies the Google ID token and returns the email if valid.
    """
    try:
        # Google's tokeninfo endpoint (alternative to using google-auth library)
        response = requests.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": token})
        data = response.json()
        # Check audience and other claims
        if response.status_code == 200 and data.get("aud") == GOOGLE_CLIENT_ID:
            return data.get("email")
    except Exception:
        pass
    return None

@app.post("/api/login")
async def login(user: User):
    # 1. Traditional username/password login
    if user.username and user.password:
        if user.username == "admin" and user.password == "password":
            token = jwt.encode({"sub": user.username}, SECRET, algorithm="HS256")
            return {"access_token": token}
        raise HTTPException(status_code=401, detail="Auth failed")
    # 2. Google OAuth credential login
    if user.credential:
        user_email = verify_google_token(user.credential)
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid Google token")
        # You can add DB user creation/check here if you want
        token = jwt.encode({"sub": user_email}, SECRET, algorithm="HS256")
        return {"access_token": token}
    raise HTTPException(status_code=400, detail="Missing login payload")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/api/data")
def get_data(db=Depends(get_db)):
    cur = db.cursor()
    query = """
        SELECT
            d.date,
            p.product_name,
            p.category,
            s.store_name,
            c.customer_name,
            SUM(f.units_sold) AS units_sold,
            SUM(f.revenue) AS revenue,
            SUM(f.profit) AS profit
        FROM fact_sales f
        JOIN dim_date d ON f.date_id = d.date_id
        JOIN dim_product p ON f.product_id = p.product_id
        JOIN dim_customer c ON f.customer_id = c.customer_id
        JOIN dim_store s ON f.store_id = s.store_id
        GROUP BY d.date, p.product_name, p.category, s.store_name, c.customer_name
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