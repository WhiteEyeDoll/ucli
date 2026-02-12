import json
from collections.abc import Sequence
from typing import Any

import yaml
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table

from ucli.cli.console import console as default_console
from ucli.cli.types import OutputFormat


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


def render_json(data: BaseModel | Sequence[BaseModel], console: Console):

    if isinstance(data, BaseModel):

        serialized = data.model_dump(mode="json", exclude_none=True)

    elif isinstance(data, Sequence) and not isinstance(data, (str, bytes)):

        if not all(isinstance(item, BaseModel) for item in data):

            raise TypeError(
                "All items in the Sequence must be instances of Pydantic BaseModel"
            )

        serialized = [item.model_dump(mode="json", exclude_none=True) for item in data]
    else:
        raise TypeError(f"Expected BaseModel or Sequence[BaseModel], got {type(data)}")

    output = json.dumps(serialized)

    console.print_json(output)


def render_yaml(data: BaseModel | Sequence[BaseModel], console: Console):

    if isinstance(data, BaseModel):

        serialized = data.model_dump(mode="json", exclude_none=True)

    elif isinstance(data, Sequence) and not isinstance(data, (str, bytes)):

        data_list = list(data)

        if not all(isinstance(item, BaseModel) for item in data_list):
            raise TypeError(
                "All items in the Sequence must be instances of Pydantic BaseModel"
            )

        serialized = [
            item.model_dump(mode="json", exclude_none=True) for item in data_list
        ]
    else:
        raise TypeError(f"Expected BaseModel or Sequence[BaseModel], got {type(data)}")

    output = yaml.safe_dump(
        serialized,
        sort_keys=False,
        default_flow_style=False,
    )

    console.print(output)


def render_table(
    data: BaseModel | Sequence[BaseModel], console: Console, max_depth: int = 3
):

    if isinstance(data, BaseModel):

        data_list = [data]

    elif isinstance(data, Sequence) and not isinstance(data, (str, bytes)):

        data_list = list(data)

        if not all(isinstance(item, BaseModel) for item in data_list):

            raise TypeError(
                "All items in the Sequence must be instances of Pydantic BaseModel"
            )
    else:
        raise TypeError(f"Expected BaseModel or Sequence[BaseModel], got {type(data)}")

    if not data_list:
        console.print("No results.")
        return

    columns = list(data_list[0].model_dump(mode="json", exclude_none=True).keys())

    table = Table(show_header=True, header_style="bold magenta", expand=True)

    for col in columns:
        table.add_column(col, no_wrap=False)

    for item in data_list:
        item_serialized = item.model_dump(mode="json", exclude_none=True)
        table.add_row(
            *(
                _stringify_nested(item_serialized.get(col), max_depth=max_depth)
                for col in columns
            )
        )

    console.print(table)


def render(
    data: BaseModel | Sequence[BaseModel],
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
