# render.py
from typing import Any
from rich.console import Console
from rich.table import Table
from pydantic import BaseModel
import json

def _stringify_nested(val: Any, depth: int = 0, max_depth: int = 3) -> str:
    if depth > max_depth:
        return "…"

    elif isinstance(val, dict):
        lines = []
        for k, v in val.items():
            sub = _stringify_nested(v, depth + 1, max_depth)
            if isinstance(v, (dict, list)):
                lines.append(f"{k}:\n  {sub.replace(chr(10), chr(10)+'  ')}")
            else:
                lines.append(f"{k}: {v}")
        return "\n".join(lines)

    elif isinstance(val, list):
        return "\n".join(_stringify_nested(v, depth + 1, max_depth) for v in val)

    else:
        return str(val)

def render_json(data: Any, console: Console):
    data_list = [data] if isinstance(data, BaseModel) else list(data)
    serialized = [d.model_dump(exclude_none=True) for d in data_list]
    console.print_json(json.dumps(serialized))


def render_table(data: Any, console: Console, max_depth: int = 3):
    data_list = [data] if isinstance(data, BaseModel) else list(data)
    if not data_list:
        console.print("No data")
        return

    first_row = data_list[0].model_dump(exclude_none=True)
    columns = list(first_row.keys())

    table = Table(show_header=True, header_style="bold magenta", expand=True)
    for col in columns:
        table.add_column(col, no_wrap=False)

    for row in data_list:
        row_dict = row.model_dump(exclude_none=True)
        table.add_row(*(_stringify_nested(row_dict.get(col), max_depth=max_depth) for col in columns))

    console.print(table)


def render_text(data: Any, console: Console, max_depth: int = 3):

    data_list = [data] if isinstance(data, BaseModel) else list(data)
    if not data_list:
        console.print("No data")
        return

    for row in data_list:
        row_dict = row.model_dump(exclude_none=True)
        for k, v in row_dict.items():
            console.print(_stringify_nested({k: v}, max_depth=max_depth))
        console.print("-" * 40)


def render(data: Any, format: str, console: Console = None, max_depth: int = 3):

    if console is None:
        from ucli.cmd.console import console


    if format == "json":
        render_json(data, console)
    elif format == "table":
        render_table(data, console, max_depth)
    elif format == "text":
        render_text(data, console, max_depth)
    else:
        raise ValueError(f"Unknown format: {format}")
