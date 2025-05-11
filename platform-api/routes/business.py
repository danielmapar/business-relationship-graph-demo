# routes/business.py
from fastapi import APIRouter
from ..services.business import BusinessService

router = APIRouter(prefix="/businesses", tags=["businesses"])

@router.post("")
async def create_business():
    return await BusinessService.create()

@router.get("/{business_id}")
async def get_business(business_id: str):
    # Implementation
    return {"id": business_id}