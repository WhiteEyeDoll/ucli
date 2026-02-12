import sys
from typing import Annotated

import typer
from pydantic import HttpUrl, ValidationError

from ucli.cli.commands import networks, sites
from ucli.cli.types import OutputFormat
from ucli.client.models.client import ClientOptions

app = typer.Typer()


@app.callback()
def main(
    *,
    ctx: typer.Context,
    api_key: Annotated[
        str | None, typer.Option(envvar="UCLI_API_KEY", help="Unifi API key.")
    ] = None,
    base_url: Annotated[
        str | None,
        typer.Option(
            envvar="UCLI_BASE_URL",
            help="Base URL of the Unifi API in the form of https://hostname/.",
        ),
    ] = None,
    verify_tls: Annotated[
        bool,
        typer.Option(
            envvar="UCLI_VERIFY_TLS",
            help="Set TLS certificate verification.",
        ),
    ] = True,
    output_format: Annotated[
        OutputFormat,
        typer.Option(envvar="UCLI_OUTPUT_FORMAT", help="CLI output format."),
    ] = "json",
    timeout: Annotated[
        float,
        typer.Option(envvar="UCLI_TIMEOUT", help="Request timeout limit in seconds."),
    ] = 10.0,
):

    if ctx.resilient_parsing or any(arg in ("--help", "-h") for arg in sys.argv):
        return

    if api_key is None or base_url is None:
        raise typer.BadParameter("api_key and base_url are required")

    try:
        client_options = ClientOptions(
            base_url=HttpUrl(base_url),
            api_key=api_key,
            verify_tls=verify_tls,
            timeout=timeout,
        )
    except ValidationError as error:
        raise typer.BadParameter(f"Invalid client options:\n{error}") from error

    ctx.obj = {
        "client_options": client_options,
        "output_format": output_format,
    }


app.add_typer(sites.app, name="sites")
app.add_typer(networks.app, name="networks")

if __name__ == "__main__":
    app()
