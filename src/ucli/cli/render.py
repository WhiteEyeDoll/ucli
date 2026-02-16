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
SerializedItem = dict[str, Any]
RenderPayload = SerializedItem | list[SerializedItem]


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


def _sort_models(models: Sequence[BaseModel], sort_by: str) -> list[BaseModel]:
    model_type = type(models[0]) if models else None
    if model_type and sort_by not in model_type.model_fields:
        raise ValueError(f"Unknown sort field: {sort_by}")

    def key(model: BaseModel):
        value = getattr(model, sort_by, None)
        if isinstance(value, str):
            value = value.casefold()
        return (value is None, value)  # None values last

    return sorted(models, key=key)


def _prepare_payload(data: RenderData, sort_by: str | None = None) -> RenderPayload:
    models, is_single = _coerce_models(data)

    if sort_by and len(models) > 1:
        models = _sort_models(models, sort_by)

    items = [model.model_dump(mode="json", exclude_none=True) for model in models]
    return items[0] if is_single else items


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


def render_json(payload: RenderPayload, console: Console):

    console.print_json(data=payload)


def render_yaml(payload: RenderPayload, console: Console):

    yaml_text = yaml.safe_dump(
        payload,
        sort_keys=False,
        default_flow_style=False,
    )

    console.print(Syntax(code=yaml_text, lexer="yaml", background_color="default"))


def render_table(rows: Sequence[SerializedItem], console: Console):

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
                    else _stringify_nested(item_serialized[col], max_depth=3)
                )
                for col in columns
            )
        )

    console.print(table)


def render(
    data: RenderData,
    output_format: OutputFormat,
    sort_by: str | None = None,
    console: Console = default_console,
):
    models, is_single = _coerce_models(data)

    if sort_by and len(models) > 1:
        models = _sort_models(models, sort_by)

    match output_format:

        case "json":
            items = [m.model_dump(mode="json", exclude_none=True) for m in models]
            payload = items[0] if is_single else items
            render_json(payload, console)
        case "yaml":
            items = [m.model_dump(mode="json", exclude_none=True) for m in models]
            payload = items[0] if is_single else items
            render_yaml(payload, console)
        case "table":
            rows = [m.model_dump(mode="json", exclude_none=True) for m in models]
            render_table(rows, console)
        case _:
            raise ValueError(f"Unknown format: {output_format}")
