# routes/business.py
from fastapi import APIRouter, Response, status, Query
import json
from ..services.business import BusinessService
from ..dtos.business import CreateBusinessInputDto, CreateBusinessOutputDto, GetBusinessOutputDto, DeleteRelationshipOutputDto, CreateRelationshipInputDto, CreateRelationshipOutputDto, GetRelationshipsOutputDto, GetRelationshipOutputDto

router = APIRouter(prefix="/businesses", tags=["businesses"])

@router.get("")
async def get(
    # FastAPI, using ... as the default value means the parameter is required. 
    name: str = Query(..., description="Filter businesses by name"),
    category: str = Query(..., description="Filter businesses by category")
) -> GetBusinessOutputDto | dict:
    result = await BusinessService.get_by_name_and_category(name=name, category=category)
    if not result:
        return Response(
            content=json.dumps({"error": "No businesses found"}),
            media_type="application/json",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return result

@router.post("")
async def create(input: CreateBusinessInputDto) -> CreateBusinessOutputDto | dict:
    result = await BusinessService.create(input)
    if not result:
        # Return with a specific status code
        return Response(
            content=json.dumps({"error": "Failed to create business"}),
            media_type="application/json",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    return CreateBusinessOutputDto(**result)

@router.get("/{business_id}")
async def get(business_id: str) -> GetBusinessOutputDto | dict:
    result = await BusinessService.get(business_id)
    if not result:
        return Response(
            content=json.dumps({"error": "Business not found"}),
            media_type="application/json",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return GetBusinessOutputDto(**result)

@router.post("/{business_id}/relationships")
async def create_relationship(business_id: str, input: CreateRelationshipInputDto) -> CreateRelationshipOutputDto | dict:
    result = await BusinessService.create_relationship(business_id, input)
    if not result:
        return Response(
            content=json.dumps({"error": "Could not create relationship"}),
            media_type="application/json",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    return CreateRelationshipOutputDto(**result)

@router.get("/{business_id}/relationships")
async def get_relationships(business_id: str) -> GetRelationshipsOutputDto | dict:
    result = await BusinessService.get_relationships(business_id)
    if not result:
        return Response(
            content=json.dumps({"error": "No relationships found"}),
            media_type="application/json",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    return GetRelationshipsOutputDto(**result)

@router.get("/{business_id}/relationships/{other_business_id}")
async def get_relationship(business_id: str, other_business_id: str) -> GetRelationshipOutputDto | dict:
    result = await BusinessService.get_relationship(business_id, other_business_id)
    if not result:
        return Response(
            content=json.dumps({"error": "Could not get relationship"}),
            media_type="application/json",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    return GetRelationshipOutputDto(**result)

