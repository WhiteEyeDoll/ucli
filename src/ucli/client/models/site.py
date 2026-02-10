from uuid import UUID

from pydantic import BaseModel


class Site(BaseModel):
    name: str
    id: UUID
    internalReference: str
