from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.services.data_service import DataService
from app.services.auth_service import get_current_user
from app.db.database import get_db


router = APIRouter(prefix="/api", tags=["data"])


@router.get("/data")
def get_data(user=Depends(get_current_user), db=Depends(get_db)):
    """Get sales data with persona-based filtering."""
    persona = user.get("persona")
    data = DataService.get_sales_data(persona, db)
    return JSONResponse(content=data)


@router.get("/products")
def get_products(db=Depends(get_db)):
    """Get all products."""
    data = DataService.get_products(db)
    return JSONResponse(content=data)


@router.get("/stores")
def get_stores(db=Depends(get_db)):
    """Get all stores."""
    data = DataService.get_stores(db)
    return JSONResponse(content=data)


@router.get("/ppdata")
def get_pp_data(user=Depends(get_current_user), db=Depends(get_db)):
    """Get PP data with persona-based filtering."""
    persona = user.get("persona")
    data = DataService.get_pp_data(persona, db)
    return JSONResponse(content=data)


@router.get("/ppproducts")
def get_pp_products(db=Depends(get_db)):
    """Get PP products."""
    data = DataService.get_pp_products(db)
    return JSONResponse(content=data)


@router.get("/ppstores")
def get_pp_stores(db=Depends(get_db)):
    """Get PP stores."""
    data = DataService.get_pp_stores(db)
    return JSONResponse(content=data)
