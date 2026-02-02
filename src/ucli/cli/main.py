from typing import Annotated

import typer
from pydantic import HttpUrl, ValidationError

from ucli.cli.commands import networks, sites
from ucli.cli.types import OutputFormat
from ucli.client.models.options import ClientOptionsModel

app = typer.Typer()


@app.callback()
def main(
    *,
    ctx: typer.Context,
    api_key: Annotated[str, typer.Option(envvar="UCLI_API_KEY", help="Unifi API key")],
    base_url: Annotated[
        str,
        typer.Option(
            envvar="UCLI_BASE_URL",
            help="Base URL of the Unifi API in the form of https://hostname/",
        ),
    ],
    tls_verify: Annotated[
        bool,
        typer.Option(
            "--verify-tls/--no-verify-tls",
            envvar="UCLI_VERIFY_TLS",
            help="Set TLS certificate verification",
        ),
    ] = True,
    output_format: Annotated[
        OutputFormat,
        typer.Option(envvar="UCLI_OUTPUT_FORMAT", help="CLI output format"),
    ] = "json",
):
    """
    Global options
    """

    try:
        client_options = ClientOptionsModel(
            base_url=HttpUrl(base_url),
            api_key=api_key,
            tls_verify=tls_verify,
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
