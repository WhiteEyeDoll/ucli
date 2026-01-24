import typer

app = typer.Typer()


@app.command()
def list(siteId: str):


@app.command()
def get(siteId: str,  networkId: str):


if __name__ == "__main__":
    app()