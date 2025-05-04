from fastapi import APIRouter, Query
from app.services.ors_service import get_route
from fastapi.responses import JSONResponse
import openrouteservice
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

@router.get("/")
def ping():
    return {"message": "ok issue"}