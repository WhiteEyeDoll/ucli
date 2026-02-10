from pydantic import BaseModel


class FieldFilterSpec(BaseModel):
    ops: list[str]
