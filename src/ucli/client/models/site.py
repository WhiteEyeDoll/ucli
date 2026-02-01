from uuid import UUID

from pydantic import BaseModel


class SiteModel(BaseModel):
    name: str
    id: UUID
    internalReference: str
