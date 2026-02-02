import typer

from ucli.cli.render import render
from ucli.client.client import APIClientV1

app = typer.Typer()


@app.command("list")
def sites_list(ctx: typer.Context):

    client = APIClientV1.get_client(ctx.obj["client_options"])

    data = client.sites.list()

    render(data, output_format=ctx.obj["output_format"])
