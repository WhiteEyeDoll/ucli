from uuid import UUID

import typer


def site_scoped_app() -> typer.Typer:
    """
    Creates a Typer sub-app for commands that require a site_id.
    Automatically injects site_id into ctx.obj.
    """
    app = typer.Typer()

    @app.callback()
    def _callback(
        ctx: typer.Context,
        site_id: UUID = typer.Option(envvar="UCLI_SITE_ID", help="Site ID"),
    ):

        if ctx.obj is None:
            ctx.obj = {}

        ctx.obj["site_id"] = site_id

    return app
