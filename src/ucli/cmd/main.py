import typer
from pydantic import BaseModel
from typing import Optional, Annotated
from ucli.client.models.config import ClientOptionsModel
from ucli.cmd.commands import sites
from ucli.cmd.commands import networks
from ucli.client.factory import get_client


class CLIOptionsModel(BaseModel):
    site_id: Optional[str] = None
    format: str


class GlobalOptionsModel(BaseModel):
    cli: CLIOptionsModel
    client: ClientOptionsModel


app = typer.Typer()


@app.callback()
def main(
    ctx: typer.Context,
    token: Annotated[
        str, typer.Option(envvar="UCLI_API_TOKEN", help="Unifi console API token")
    ],
    base_url: Annotated[
        str, typer.Option(envvar="UCLI_BASE_URL", help="Base URL of the Unifi console")
    ],
    verify: bool = typer.Option(
        True,
        "--verify/--no-verify",
        envvar="UCLI_VERIFY_TLS",
        help="Set TLS certificate verification",
    ),
    siteid: Annotated[
        Optional[str], typer.Option(envvar="UCLI_SITE_ID", help="Site ID")
    ] = None,
    format: Annotated[
        Optional[str], typer.Option(help="Console output format")
    ] = "json",
):
    """
    Global options
    """

    ctx.obj = GlobalOptionsModel(
        client=ClientOptionsModel(base_url=base_url, api_token=token, tls_verify=verify),
        cli=CLIOptionsModel(site_id=siteid, format=format),
    )


app.add_typer(sites.app, name="sites")
app.add_typer(networks.app, name="networks")

if __name__ == "__main__":
    app()
