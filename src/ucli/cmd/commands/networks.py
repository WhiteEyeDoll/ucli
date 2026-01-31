import typer
import json
from typing import Optional, Annotated
from ucli.client.factory import get_client
from ucli.cmd.console import console
from ucli.cmd.render import render

app = typer.Typer()

@app.command()
def list(
    ctx: typer.Context
):
    
    client = get_client(ctx.obj.client)

    global_options: CLIOptions = ctx.obj.cli

    site_id = client.sites.get_id_by_name(ctx.obj.cli.sitename)

    data = client.networks(site_id).list()

    render(data, format=global_options.format)

@app.command()
def get(
    ctx: typer.Context,
    id: Annotated[Optional[str], typer.Option(help="Network ID")] = None,
    name: Annotated[Optional[str], typer.Option(help="Network name")] = None
):
    
    if (id is None and name is None) or (id is not None and name is not None):
        raise typer.BadParameter("You must provide either --id or --name, but not both.")
    
    client = get_client(ctx.obj.client)

    global_options: CLIOptions = ctx.obj.cli

    site_id = client.sites.get_id_by_name(ctx.obj.cli.sitename)

    if id is None:
        network_id = client.networks(site_id).get_id_by_name(name)
    else:
        network_id = id

    data = client.networks(site_id).get(network_id)

    render(data, format=global_options.format)
