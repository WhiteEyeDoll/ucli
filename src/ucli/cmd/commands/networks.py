import typer
from typing import Optional, Annotated
from ucli.client.factory import get_client
from ucli.cmd.render import render

app = typer.Typer()


@app.command()
def list(ctx: typer.Context):

    client = get_client(ctx.obj.client)

    global_options: CLIOptionsModel = ctx.obj.cli

    site = client.sites.get(global_options.site_id)

    data = site.networks.list()

    render(data, format=global_options.format)


@app.command()
def get(
    ctx: typer.Context,
    id: Annotated[str, typer.Option(help="Network ID")] = None,
):

    client = get_client(ctx.obj.client)

    global_options: CLIOptionsModel = ctx.obj.cli

    site = client.sites.get(global_options.site_id)

    data = site.networks.get(id)

    render(data, format=global_options.format)
