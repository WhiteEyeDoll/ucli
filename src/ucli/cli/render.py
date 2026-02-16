import json
from collections.abc import Sequence
from typing import Any

import yaml
from pydantic import BaseModel
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from ucli.cli.console import console as default_console
from ucli.cli.types import OutputFormat

RenderData = BaseModel | Sequence[BaseModel]


def _coerce_models(data: RenderData) -> tuple[list[BaseModel], bool]:
    if isinstance(data, BaseModel):
        return [data], True

    if isinstance(data, Sequence) and not isinstance(data, (str, bytes)):
        if not all(isinstance(item, BaseModel) for item in data):
            raise TypeError(
                "All items in the Sequence must be instances of Pydantic BaseModel"
            )
        return list(data), False

    raise TypeError(f"Expected BaseModel or Sequence[BaseModel], got {type(data)}")


def _stringify_nested(val: Any, depth: int = 0, max_depth: int = 3) -> str:
    if depth > max_depth:
        return "…"

    if isinstance(val, dict):
        lines = []
        for k, v in val.items():
            sub = _stringify_nested(v, depth + 1, max_depth)
            if isinstance(v, (dict, list)):
                lines.append(f"{k}:\n  {sub.replace('\n', '\n  ')}")
            else:
                lines.append(f"{k}: {v}")
        return "\n".join(lines)

    if isinstance(val, list):
        return "\n".join(_stringify_nested(v, depth + 1, max_depth) for v in val)

    return str(val)


def render_json(data: RenderData, console: Console):
    models, is_single = _coerce_models(data)

    serialized_items = [
        item.model_dump(mode="json", exclude_none=True) for item in models
    ]

    payload = serialized_items[0] if is_single else serialized_items

    console.print_json(data=payload)


def render_yaml(data: RenderData, console: Console):
    models, is_single = _coerce_models(data)

    serialized_items = [
        item.model_dump(mode="json", exclude_none=True) for item in models
    ]

    payload = serialized_items[0] if is_single else serialized_items

    yaml_text = yaml.safe_dump(
        payload,
        sort_keys=False,
        default_flow_style=False,
    )

    console.print(Syntax(code=yaml_text, lexer="yaml", background_color="default"))


def render_table(data: RenderData, console: Console, max_depth: int = 3):
    models, _ = _coerce_models(data)

    if not models:
        console.print("No results.")
        return

    rows = [item.model_dump(mode="json", exclude_none=True) for item in models]
    columns = list(dict.fromkeys(key for row in rows for key in row.keys()))

    table = Table(show_header=True, header_style="bold magenta", expand=True)

    for col in columns:
        table.add_column(col, no_wrap=False)

    for item_serialized in rows:
        table.add_row(
            *(
                (
                    ""
                    if col not in item_serialized
                    else _stringify_nested(item_serialized[col], max_depth=max_depth)
                )
                for col in columns
            )
        )

    console.print(table)


def render(
    data: RenderData,
    output_format: OutputFormat,
    console: Console = default_console,
    max_depth: int = 3,
):
    match output_format:

        case "json":
            render_json(data, console)
        case "yaml":
            render_yaml(data, console)
        case "table":
            render_table(data, console, max_depth)
        case _:
            raise ValueError(f"Unknown format: {output_format}")
