import typer
from ucli.cmd.commands import sites

app = typer.Typer()

app.add_typer(sites.app, name="sites")
