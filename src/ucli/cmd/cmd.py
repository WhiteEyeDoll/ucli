import typer
from ucli.cmd.commands import sites
from ucli.cmd.commands import networks


app = typer.Typer()

app.add_typer(sites.app, name="sites")
app.add_typer(networks.app, name="networks")

