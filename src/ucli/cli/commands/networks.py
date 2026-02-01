from typing import Annotated
from uuid import UUID

import typer

from ucli.cli.options import CLIOptionsModel
from ucli.cli.render import render
from ucli.client.client import APIClientV1
from ucli.client.resources.site import SiteResource

app = typer.Typer()


@app.command("list")
def networks_list(ctx: typer.Context):

    client = APIClientV1.get_client(ctx.obj.client_options)

    global_options: CLIOptionsModel = ctx.obj.cli_options

    site: SiteResource = client.sites.get(global_options.site_id)

    data = site.networks.list()

    render(data, output_format=global_options.output_format)


@app.command("get")
def networks_get(
    ctx: typer.Context,
    network_id: Annotated[UUID, typer.Option("--id", help="Network ID")],
):

    client = APIClientV1.get_client(ctx.obj.client_options)

    global_options: CLIOptionsModel = ctx.obj.cli_options

    site = client.sites.get(global_options.site_id)

    data = site.networks.get(network_id)

    render(data, output_format=global_options.output_format)
