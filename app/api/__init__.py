from fastapi import APIRouter
from app.api.routes import auth, invoices, vendors, checks

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(invoices.router)
api_router.include_router(vendors.router)
api_router.include_router(checks.router)
