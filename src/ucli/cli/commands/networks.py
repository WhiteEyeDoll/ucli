from typing import Annotated
from uuid import UUID

import typer

from ucli.cli.render import render
from ucli.cli.site_scoped import site_scoped_app
from ucli.client.client import APIClientV1

app = site_scoped_app()


@app.command("list")
def networks_list(ctx: typer.Context):

    with APIClientV1(ctx.obj["client_options"]) as client:
        site = client.sites.get(ctx.obj["site_id"])

        data = site.networks.list()

        render(data, output_format=ctx.obj["output_format"])


@app.command("get")
def networks_get(
    ctx: typer.Context,
    network_id: Annotated[UUID, typer.Option("--id", help="Network ID")],
):

    with APIClientV1(ctx.obj["client_options"]) as client:
        site = client.sites.get(ctx.obj["site_id"])

        data = site.networks.get(network_id)

        render(data, output_format=ctx.obj["output_format"])
