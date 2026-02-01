import typer

from ucli.cli.options import CLIOptionsModel
from ucli.cli.render import render
from ucli.client.factory import get_client

app = typer.Typer()


@app.command("list")
def sites_list(ctx: typer.Context):

    client = get_client(ctx.obj.client)

    global_options: CLIOptionsModel = ctx.obj.cli

    data = client.sites.list()

    render(data, output_format=global_options.output_format)
