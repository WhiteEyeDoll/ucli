import typer

from ucli.cli.options import CLIOptionsModel
from ucli.cli.render import render
from ucli.client.client import APIClientV1

app = typer.Typer()


@app.command("list")
def sites_list(ctx: typer.Context):

    client = APIClientV1.get_client(ctx.obj.client_options)

    global_options: CLIOptionsModel = ctx.obj.cli_options

    data = client.sites.list()

    render(data, output_format=global_options.output_format)
