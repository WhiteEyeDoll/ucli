from pydantic import BaseModel
from uuid import UUID


class SiteModel(BaseModel):
    name: str
    id: UUID
    internalReference: str
