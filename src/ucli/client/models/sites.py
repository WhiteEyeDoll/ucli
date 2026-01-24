from pydantic import BaseModel

class Site(BaseModel):
    id: str
    internalReference: str
    name: str