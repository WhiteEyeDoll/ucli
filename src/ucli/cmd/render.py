import json
import yaml
from typing import Any, Iterable
from rich.console import Console
from rich.table import Table
from pydantic import BaseModel


def _stringify_nested(val: Any, depth: int = 0, max_depth: int = 3) -> str:
    if depth > max_depth:
        return "…"

    elif isinstance(val, dict):
        lines = []
        for k, v in val.items():
            sub = _stringify_nested(v, depth + 1, max_depth)
            if isinstance(v, (dict, list)):
                lines.append(f"{k}:\n  {sub.replace("\n", "\n  ")}")
            else:
                lines.append(f"{k}: {v}")
        return "\n".join(lines)

    elif isinstance(val, list):
        return "\n".join(_stringify_nested(v, depth + 1, max_depth) for v in val)

    else:
        return str(val)


def render_json(data: BaseModel | list[BaseModel], console: Console):

    if isinstance(data, BaseModel):
        serialized = data.model_dump(exclude_none=True)
    elif isinstance(data, list):
        serialized = [item.model_dump(exclude_none=True) for item in data]

    output = json.dumps(serialized)

    console.print_json(output)


def render_yaml(data: BaseModel | list[BaseModel], console: Console):

    if isinstance(data, BaseModel):
        serialized = data.model_dump(exclude_none=True)
    elif isinstance(data, list):
        serialized = [item.model_dump(exclude_none=True) for item in data]

    output = yaml.safe_dump(
        serialized,
        sort_keys=False,
        default_flow_style=False,
    )

    console.print(output)


def render_table(
    data: BaseModel | list[BaseModel], console: Console, max_depth: int = 3
):

    if isinstance(data, BaseModel):
        data_list = [data]
    elif isinstance(data, list):
        data_list = data

    if not data_list:
        console.print("No data")
        return

    columns = list(data_list[0].model_dump(exclude_none=True).keys())

    table = Table(show_header=True, header_style="bold magenta", expand=True)

    for col in columns:
        table.add_column(col, no_wrap=False)

    for item in data_list:
        item_serialized = item.model_dump(exclude_none=True)
        table.add_row(
            *(
                _stringify_nested(item_serialized.get(col), max_depth=max_depth)
                for col in columns
            )
        )

    console.print(table)


def render(
    data: BaseModel | list[BaseModel],
    format: str,
    console: Console = None,
    max_depth: int = 3,
):

    if console is None:
        from ucli.cmd.console import console

    match format:

        case "json":
            render_json(data, console)
        case "yaml":
            render_yaml(data, console)
        case "table":
            render_table(data, console, max_depth)
        case _:
            raise ValueError(f"Unknown format: {format}")
