from typing import Annotated
from uuid import UUID

import typer

from ucli.cli.options import CLIOptionsModel
from ucli.cli.render import render
from ucli.client.factory import get_client

app = typer.Typer()


@app.command("list")
def networks_list(ctx: typer.Context):

    client = get_client(ctx.obj.client)

    global_options: CLIOptionsModel = ctx.obj.cli

    site = client.sites.get(global_options.site_id)

    data = site.networks.list()

    render(data, output_format=global_options.format)


@app.command("get")
def networks_get(
    ctx: typer.Context,
    network_id: Annotated[UUID, typer.Option("--id", help="Network ID")] = None,
):

    client = get_client(ctx.obj.client)

    global_options: CLIOptionsModel = ctx.obj.cli

    site = client.sites.get(global_options.site_id)

    data = site.networks.get(network_id)

    render(data, output_format=global_options.format)
