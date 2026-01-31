from pydantic import BaseModel


class SiteModel(BaseModel):
    name: str
    id: str
    internalReference: str
