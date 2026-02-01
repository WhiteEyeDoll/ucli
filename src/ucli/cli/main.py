from typing import Annotated
from uuid import UUID

import typer

from ucli.cli.commands import networks, sites
from ucli.cli.options import CLIOptionsModel, GlobalOptionsModel
from ucli.client.models.options import ClientOptionsModel

app = typer.Typer()


@app.callback()
def main(
    *,
    ctx: typer.Context,
    token: Annotated[
        str, typer.Option(envvar="UCLI_API_TOKEN", help="Unifi console API token")
    ],
    base_url: Annotated[
        str, typer.Option(envvar="UCLI_BASE_URL", help="Base URL of the Unifi console")
    ],
    site_id: Annotated[UUID, typer.Option(envvar="UCLI_SITE_ID", help="Site ID")],
    verify: Annotated[
        bool,
        typer.Option(
            "--verify/--no-verify",
            envvar="UCLI_VERIFY_TLS",
            help="Set TLS certificate verification",
        ),
    ] = True,
    output_format: Annotated[
        str, typer.Option(envvar="UCLI_OUTPUT_FORMAT", help="Console output format")
    ] = "json",
):
    """
    Global options
    """

    ctx.obj = GlobalOptionsModel(
        client=ClientOptionsModel(
            base_url=base_url, api_token=token, tls_verify=verify
        ),
        cli=CLIOptionsModel(site_id=site_id, output_format=output_format),
    )


app.add_typer(sites.app, name="sites")
app.add_typer(networks.app, name="networks")

if __name__ == "__main__":
    app()
