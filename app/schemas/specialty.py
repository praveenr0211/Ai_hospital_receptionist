from pydantic import BaseModel, ConfigDict

class SpecialtyBase(BaseModel):
    name: str
    description: str | None = None
    status: bool = True

class SpecialtyResponse(SpecialtyBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class SpecialtyListResponse(BaseModel):
    items: list[SpecialtyResponse]
    total: int
