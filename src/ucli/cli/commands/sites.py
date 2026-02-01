import typer
from ucli.client.factory import get_client
from ucli.cli.render import render
from uuid import UUID
from typing import Annotated

app = typer.Typer()


@app.command()
def list(ctx: typer.Context):

    client = get_client(ctx.obj.client)

    global_options: CLIOptionsModel = ctx.obj.cli

    data = client.sites.list()

    render(data, format=global_options.format)
