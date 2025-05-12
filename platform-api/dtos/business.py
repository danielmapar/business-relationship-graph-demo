from pydantic import BaseModel

class CreateBusinessInputDto(BaseModel):
    name: str
    category: str

class CreateBusinessOutputDto(BaseModel):
    business: bool = None
    error: str = None