import typer
import json
from ucli.client.client import get_client

from ucli.cmd.console import console

app = typer.Typer()

@app.command()
def list():

    client = get_client()

    site_id = client.sites.get_id("Default")
    networks = client.networks(site_id).list()

    console.print(json.dumps(networks))
