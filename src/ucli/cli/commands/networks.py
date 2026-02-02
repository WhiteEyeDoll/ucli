from typing import Annotated
from uuid import UUID

import typer

from ucli.cli.render import render
from ucli.cli.site_scoped import site_scoped_app
from ucli.client.client import APIClientV1
from ucli.client.resources.site import SiteResource

app = site_scoped_app()


@app.command("list")
def networks_list(ctx: typer.Context):

    client = APIClientV1.get_client(ctx.obj["client_options"])

    site: SiteResource = client.sites.get(ctx.obj["site_id"])

    data = site.networks.list()

    render(data, output_format=ctx.obj["output_format"])


@app.command("get")
def networks_get(
    ctx: typer.Context,
    network_id: Annotated[UUID, typer.Option("--id", help="Network ID")],
):

    client = APIClientV1.get_client(ctx.obj["client_options"])

    site = client.sites.get(ctx.obj["site_id"])

    data = site.networks.get(network_id)

    render(data, output_format=ctx.obj["output_format"])
