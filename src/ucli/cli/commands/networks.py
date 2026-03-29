from pathlib import Path
from typing import Annotated, cast
from uuid import UUID

import typer
from pydantic import BaseModel

from ucli.cli.console import console
from ucli.cli.model_input import (
    edit_payload_in_editor,
    load_payload_from_file,
    merge_payload,
    resolve_model_input,
    validate_model_payload,
)
from ucli.cli.render import render
from ucli.cli.site_scoped import site_scoped_app
from ucli.client.client import APIClientV1
from ucli.client.models.network import NetworkWrite

app = site_scoped_app()


@app.command("list")
def networks_list(
    ctx: typer.Context,
    sort_by: Annotated[
        str | None,
        typer.Option(
            help="Sort results by field path (for example: vlanId or metadata.origin)."
        ),
    ] = None,
):

    with APIClientV1(ctx.obj["client_options"]) as client:
        site = client.sites.get(ctx.obj["site_id"])

        network_list = site.networks.list()

        render(
            data=network_list, sort_by=sort_by, output_format=ctx.obj["output_format"]
        )


@app.command("get")
def networks_get(
    ctx: typer.Context,
    network_id: Annotated[UUID, typer.Argument(help="Network ID")],
):

    with APIClientV1(ctx.obj["client_options"]) as client:
        site = client.sites.get(ctx.obj["site_id"])

        network = site.networks.get(network_id)

        render(network, output_format=ctx.obj["output_format"])


@app.command("create")
def networks_create(
    ctx: typer.Context,
    interactive: Annotated[
        bool,
        typer.Option(
            "--interactive",
            "-i",
            help="Create network by entering values interactively.",
        ),
    ] = False,
    configuration_file: Annotated[
        Path | None,
        typer.Option(
            "--file",
            "-f",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help=(
                "Path to network configuration file (JSON or YAML). "
                "In interactive mode, this is used as the base payload."
            ),
        ),
    ] = None,
):
    network_configuration = resolve_model_input(
        NetworkWrite,
        interactive=interactive,
        configuration_file=configuration_file,
    )

    with APIClientV1(ctx.obj["client_options"]) as client:
        site = client.sites.get(ctx.obj["site_id"])

        network = site.networks.create(network_configuration)

        render(network, output_format=ctx.obj["output_format"])


@app.command("edit")
def networks_edit(
    ctx: typer.Context,
    network_id: Annotated[UUID, typer.Argument(help="Network ID")],
    configuration_file: Annotated[
        Path | None,
        typer.Option(
            "--file",
            "-f",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help=(
                "Update payload file (JSON or YAML). "
                "With --editor, merged as patch into current payload."
            ),
        ),
    ] = None,
    editor_mode: Annotated[
        bool,
        typer.Option(
            "--editor",
            "-e",
            help="Open the current network payload in the editor and update from it.",
        ),
    ] = False,
):
    with APIClientV1(ctx.obj["client_options"]) as client:
        site = client.sites.get(ctx.obj["site_id"])

        if editor_mode:
            current_network = site.networks.get(network_id)
            current_write_model = validate_model_payload(
                NetworkWrite,
                current_network.model_dump(mode="json"),
            )
            current_payload = cast(BaseModel, current_write_model).model_dump(
                mode="json", exclude_none=True
            )

            if configuration_file is not None:
                patch_payload = load_payload_from_file(configuration_file)
                current_payload = merge_payload(current_payload, patch_payload)

            payload = edit_payload_in_editor(current_payload)
        else:
            if configuration_file is None:
                raise typer.BadParameter("Provide --editor or --file.")
            payload = load_payload_from_file(configuration_file)

        network_configuration = validate_model_payload(NetworkWrite, payload)
        network = site.networks.update(network_id, network_configuration)

        render(network, output_format=ctx.obj["output_format"])


@app.command("delete")
def networks_delete(
    ctx: typer.Context,
    network_id: Annotated[UUID, typer.Argument(help="Network ID")],
):

    with APIClientV1(ctx.obj["client_options"]) as client:
        site = client.sites.get(ctx.obj["site_id"])

        network = site.networks.get(network_id)

        render(network, output_format=ctx.obj["output_format"])

        delete = typer.confirm("Delete this network?")
        if not delete:
            raise typer.Abort()
        console.print("Deleting network...")
        site.networks.delete(network_id)
        console.print("Done.")


@app.command("references")
def networks_get_references(
    ctx: typer.Context,
    network_id: Annotated[UUID, typer.Argument(help="Network ID")],
):

    with APIClientV1(ctx.obj["client_options"]) as client:
        site = client.sites.get(ctx.obj["site_id"])

        network_references = site.networks.get_references(network_id)

        render(network_references, output_format=ctx.obj["output_format"])
