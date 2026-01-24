import typer
from ucli.client.client import get_client

from ucli.cmd.console import console

app = typer.Typer()


@app.command()
def list():

    client = get_client()
    sites = client.sites.list()

    console.print(sites)
