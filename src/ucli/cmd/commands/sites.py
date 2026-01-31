import json
import typer
from ucli.client.factory import get_client

from ucli.cmd.console import console

app = typer.Typer()


@app.command()
def list(
    ctx: typer.Context
):

    client = get_client(ctx.obj.client)

    data = client.sites.list()

    console.print(json.dumps(data))
