from typing import Annotated
from uuid import UUID

import typer

from ucli.cli.console import console
from ucli.cli.render import render
from ucli.cli.site_scoped import site_scoped_app
from ucli.client.client import APIClientV1

app = site_scoped_app()


@app.command("list")
def networks_list(
    ctx: typer.Context,
    sort_by: Annotated[
        str | None,
        typer.Option(help="Sort results by field name (e.g. vlanId). Case-sensitive."),
    ] = None,
):

    with APIClientV1(ctx.obj["client_options"]) as client:
        site = client.sites.get(ctx.obj["site_id"])

        network_list = site.networks.list()

        render(
            data=network_list, sort_by=sort_by, output_format=ctx.obj["output_format"]
        )


@app.command("get")
def networks_get(
    ctx: typer.Context,
    network_id: Annotated[UUID, typer.Argument(help="Network ID")],
):

    with APIClientV1(ctx.obj["client_options"]) as client:
        site = client.sites.get(ctx.obj["site_id"])

        network = site.networks.get(network_id)

        render(network, output_format=ctx.obj["output_format"])


@app.command("delete")
def networks_delete(
    ctx: typer.Context,
    network_id: Annotated[UUID, typer.Argument(help="Network ID")],
):

    with APIClientV1(ctx.obj["client_options"]) as client:
        site = client.sites.get(ctx.obj["site_id"])

        network = site.networks.get(network_id)

        render(network, output_format=ctx.obj["output_format"])

        delete = typer.confirm("Delete this network?")
        if not delete:
            raise typer.Abort()
        console.print("Deleting network...")
        site.networks.delete(network_id)
        console.print("Done.")


@app.command("references")
def networks_get_references(
    ctx: typer.Context,
    network_id: Annotated[UUID, typer.Argument(help="Network ID")],
):

    with APIClientV1(ctx.obj["client_options"]) as client:
        site = client.sites.get(ctx.obj["site_id"])

        network_references = site.networks.get_references(network_id)

        render(network_references, output_format=ctx.obj["output_format"])
