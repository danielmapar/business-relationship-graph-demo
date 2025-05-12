# routes/business.py
from fastapi import APIRouter
from ..services.business import BusinessService
from ..dtos.business import CreateBusinessInputDto, CreateBusinessOutputDto
router = APIRouter(prefix="/businesses", tags=["businesses"])

@router.post("")
async def create_business(input: CreateBusinessInputDto) -> CreateBusinessOutputDto:
    return await BusinessService.create(input)

@router.get("/{business_id}")
async def get_business(business_id: str):
    # Implementation
    return {"id": business_id}