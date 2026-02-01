from uuid import UUID

from pydantic import BaseModel

from ucli.client.models.options import ClientOptionsModel


class CLIOptionsModel(BaseModel):
    site_id: UUID
    format: str


class GlobalOptionsModel(BaseModel):
    cli: CLIOptionsModel
    client: ClientOptionsModel
