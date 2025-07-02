from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt
import os

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict this to your frontend domain!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET = os.getenv("SECRET", "CHANGE_ME")  # Set this as an env var in your Render dashboard

USERS = {'admin': 'password'}  # Demo user; replace with DB lookup for production

class User(BaseModel):
    username: str
    password: str

@app.post("/api/login")
def login(user: User):
    if USERS.get(user.username) == user.password:
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
def get_data(user: str = Depends(get_current_user)):
    # Replace this with a real DB query!
    data = [
        {"label": "Sales", "value": 123},
        {"label": "Users", "value": 99},
        {"label": "Revenue", "value": 456}
    ]
    return JSONResponse(content=data)