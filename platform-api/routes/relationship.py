
from fastapi import APIRouter, Response, status
import json
from ..services.business import BusinessService
from ..dtos.business import DeleteRelationshipOutputDto

router = APIRouter(prefix="/relationships", tags=["relationships"])

@router.delete("/{relationship_id}")
async def delete_relationship(relationship_id: str) -> DeleteRelationshipOutputDto | dict:
    result = await BusinessService.delete_relationship(relationship_id)
    if not result:
        return Response(
            content=json.dumps({"error": "Could not delete relationship"}),
            media_type="application/json",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    return DeleteRelationshipOutputDto(done=True)