import os
import psycopg2
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


origins = [
    "https://bi-dashboard-frontend-6c4eeitul-venkatavvari3s-projects.vercel.app",  # <- your new frontend URL
    "https://bi-dashboard-frontend.vercel.app", 
    "https://bi-dashboard-frontend-git-main-venkatavvari3s-projects.vercel.app"                                   # any other frontend URLs you use
    "http://localhost:3000",                                                       # for local development (optional)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Or use ["*"] for all (not recommended for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET = os.getenv("SECRET", "CHANGE_ME")
DATABASE_URL = os.getenv("DATABASE_URL")

class User(BaseModel):
    username: str
    password: str

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

@app.post("/api/login")
def login(user: User):
    if user.username == "admin" and user.password == "password":
        token = jwt.encode({"sub": user.username}, SECRET, algorithm="HS256")
        return {"access_token": token}
    raise HTTPException(status_code=401, detail="Auth failed")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/api/data")
def get_data(db=Depends(get_db)):
    cur = db.cursor()
    # Example: Aggregate sales by product and date (customize as needed)
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
    return JSONResponse(content=data)

# Optional: Endpoint for dimension table lists (e.g., for filters)
@app.get("/api/products")
def get_products(db=Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT product_id, product_name, category, brand FROM dim_product ORDER BY product_name")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    data = [dict(zip(columns, row)) for row in rows]
    cur.close()
    return JSONResponse(content=data)

@app.get("/api/stores")
def get_stores(db=Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT store_id, store_name, city, state FROM dim_store ORDER BY store_name")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    data = [dict(zip(columns, row)) for row in rows]
    cur.close()
    return JSONResponse(content=data)