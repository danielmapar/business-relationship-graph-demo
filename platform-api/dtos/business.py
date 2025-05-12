from pydantic import BaseModel, Field, validator

class CreateBusinessInputDto(BaseModel):
    name: str
    category: str

class CreateBusinessOutputDto(BaseModel):
    id: str

class GetBusinessOutputDto(BaseModel):
    id: str
    name: str
    category: str

class CreateRelationshipInputDto(BaseModel):
    business_id: str = Field(alias="businessId")
    relationship_type: str = Field(alias="relationshipType")
    transaction_volume: int = Field(alias="transactionVolume")

    @validator('relationship_type')
    def validate_relationship_type(cls, value):
        valid_types = ['vendor', 'client']
        if value not in valid_types:
            raise ValueError(f"relationship_type must be one of {valid_types}")
        return value

class CreateRelationshipOutputDto(BaseModel):
    id: str

