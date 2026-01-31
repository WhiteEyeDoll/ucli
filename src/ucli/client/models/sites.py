from pydantic import BaseModel

class Site(BaseModel):
    name: str
    id: str
    internalReference: str
