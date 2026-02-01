from uuid import UUID

from pydantic import BaseModel

from ucli.client.models.options import ClientOptionsModel


class CLIOptionsModel(BaseModel):
    site_id: UUID
    output_format: str


class GlobalOptionsModel(BaseModel):
    cli_options: CLIOptionsModel
    client_options: ClientOptionsModel
