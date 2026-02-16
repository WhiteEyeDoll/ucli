from typing import Annotated

import typer

from ucli.cli.render import render
from ucli.client.client import APIClientV1

app = typer.Typer()


@app.command("list")
def sites_list(
    ctx: typer.Context,
    sort_by: Annotated[
        str | None,
        typer.Option(help="Sort results by field name (e.g. name). Case-sensitive."),
    ] = None,
):

    with APIClientV1(ctx.obj["client_options"]) as client:

        site_list = client.sites.list()

        render(data=site_list, sort_by=sort_by, output_format=ctx.obj["output_format"])
