from pydantic import BaseModel

class Network(BaseModel):
    id: str
    internalReference: str
    name: str