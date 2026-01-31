import typer
from pydantic import BaseModel
from typing import Optional, Annotated
from ucli.client.models.config import ClientOptions
from ucli.cmd.commands import sites
from ucli.cmd.commands import networks

class CLIOptions(BaseModel):
    sitename: str
    format: str

class GlobalOptions(BaseModel):
    cli: CLIOptions
    client: ClientOptions

app = typer.Typer()

@app.callback()
def main(
    ctx: typer.Context,
    token: Annotated[str, typer.Option(
        envvar="UCLI_API_TOKEN",
        help="Unifi console API token")],
    base_url: Annotated[str, typer.Option(
        envvar="UCLI_BASE_URL",
        help="Base URL of the Unifi console"
    )],
    verify: bool = typer.Option(True,
                               "--verify/--no-verify",
                               envvar="UCLI_VERIFY_TLS",
                               help="Set TLS certificate verification"
                            ),
    sitename: Annotated[str, typer.Option(help="Site name")] = "Default",
    format: Annotated[Optional[str],typer.Option(help="Console output format")] = "json"
):
    """
    Global options
    """

    ctx.obj = GlobalOptions(
        client=ClientOptions(
            base_url=base_url,
            api_token=token,
            tls_verify=verify
        ),
        cli=CLIOptions(
            sitename=sitename,
            format=format
        ),
    )

app.add_typer(sites.app, name="sites")
app.add_typer(networks.app, name="networks")

if __name__ == "__main__":
    app()