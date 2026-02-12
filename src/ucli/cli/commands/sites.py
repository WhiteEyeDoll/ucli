import typer

from ucli.cli.render import render
from ucli.client.client import APIClientV1

app = typer.Typer()


@app.command("list")
def sites_list(ctx: typer.Context):

    with APIClientV1(ctx.obj["client_options"]) as client:

        site_list = client.sites.list()

        render(site_list, output_format=ctx.obj["output_format"])
