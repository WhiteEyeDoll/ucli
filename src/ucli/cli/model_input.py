import json
from copy import deepcopy
from pathlib import Path
from types import NoneType, UnionType
from typing import Annotated, Any, Literal, Union, get_args, get_origin

import typer
import yaml
from pydantic import BaseModel, ValidationError
from pydantic import TypeAdapter
from pydantic_core import PydanticUndefined

_MISSING = object()


def load_payload_from_file(configuration_file: Path) -> dict[str, Any]:
    raw_text = configuration_file.read_text(encoding="utf-8")
    suffix = configuration_file.suffix.casefold()

    try:
        if suffix in {".yaml", ".yml"}:
            payload = yaml.safe_load(raw_text)
        else:
            payload = json.loads(raw_text)
    except (yaml.YAMLError, json.JSONDecodeError) as error:
        raise typer.BadParameter(
            f"Invalid configuration file format: {error}"
        ) from error

    if payload is None:
        raise typer.BadParameter("Configuration file is empty.")

    if not isinstance(payload, dict):
        raise typer.BadParameter("Configuration file must contain a JSON/YAML object.")

    return payload


def _schema_name(schema: Any) -> str:
    name = getattr(schema, "__name__", "")
    if isinstance(name, str) and name:
        return name
    return str(schema)


def validate_model_payload(model: Any, payload: dict[str, Any]) -> Any:
    try:
        adapter = TypeAdapter(model)
        return adapter.validate_python(payload)
    except ValidationError as error:
        raise typer.BadParameter(
            f"Invalid {_schema_name(model)} payload:\n{error}"
        ) from error


def edit_payload_in_editor(
    initial_payload: dict[str, Any], *, extension: str = ".yaml"
) -> dict[str, Any]:
    serialized_payload = yaml.safe_dump(
        initial_payload,
        sort_keys=False,
        default_flow_style=False,
    )
    edited_payload = typer.edit(serialized_payload, extension=extension)
    if edited_payload is None:
        raise typer.Abort()

    try:
        payload = yaml.safe_load(edited_payload)
    except yaml.YAMLError as error:
        raise typer.BadParameter(f"Invalid edited payload format: {error}") from error

    if payload is None:
        raise typer.BadParameter("Edited payload is empty.")

    if not isinstance(payload, dict):
        raise typer.BadParameter("Edited payload must contain a JSON/YAML object.")

    return payload


def merge_payload(
    base_payload: dict[str, Any], patch_payload: dict[str, Any]
) -> dict[str, Any]:
    merged_payload: dict[str, Any] = deepcopy(base_payload)
    for key, patch_value in patch_payload.items():
        base_value = merged_payload.get(key)
        if isinstance(base_value, dict) and isinstance(patch_value, dict):
            merged_payload[key] = merge_payload(base_value, patch_value)
        else:
            merged_payload[key] = deepcopy(patch_value)

    return merged_payload


def _unwrap_optional_annotation(annotation: Any) -> Any:
    args = get_args(annotation)
    if args and NoneType in args:
        non_none_args = [arg for arg in args if arg is not NoneType]
        if len(non_none_args) == 1:
            return non_none_args[0]
    return annotation


def _is_optional_annotation(annotation: Any) -> bool:
    args = get_args(annotation)
    return bool(args and NoneType in args)


def _is_model_annotation(annotation: Any) -> bool:
    return isinstance(annotation, type) and issubclass(annotation, BaseModel)


def _get_nested_value(payload: dict[str, Any], field_path: str) -> Any:
    value: Any = payload
    for segment in field_path.split("."):
        if not isinstance(value, dict):
            return _MISSING
        value = value.get(segment, _MISSING)
        if value is _MISSING:
            return _MISSING
    return value


def _should_prompt_field(field_info: Any, payload: dict[str, Any]) -> bool:
    extra = field_info.json_schema_extra or {}
    prompt_if = extra.get("prompt_if")
    if not prompt_if:
        return True

    if not isinstance(prompt_if, dict):
        raise typer.BadParameter("prompt_if metadata must be a dictionary.")

    reference_field = prompt_if.get("field")
    if not isinstance(reference_field, str) or reference_field.strip() == "":
        raise typer.BadParameter("prompt_if.field must be a non-empty string.")

    current_value = _get_nested_value(payload, reference_field)
    if current_value is _MISSING:
        return False

    if "equals" in prompt_if:
        return current_value == prompt_if["equals"]
    if "not_equals" in prompt_if:
        return current_value != prompt_if["not_equals"]
    if "in" in prompt_if:
        allowed_values = prompt_if["in"]
        if not isinstance(allowed_values, list):
            raise typer.BadParameter("prompt_if.in must be a list.")
        return current_value in allowed_values

    raise typer.BadParameter(
        "prompt_if requires one of: equals, not_equals, in."
    )


def _is_list_annotation(annotation: Any) -> bool:
    return get_origin(annotation) is list


def _is_union_origin(origin: Any) -> bool:
    return origin in (Union, UnionType)


def _extract_discriminated_union_schema(
    annotation: Any,
) -> tuple[str, dict[str, type[BaseModel]]] | None:
    if get_origin(annotation) is not Annotated:
        return None

    args = get_args(annotation)
    if len(args) < 2:
        return None

    union_annotation = args[0]
    union_origin = get_origin(union_annotation)
    if not _is_union_origin(union_origin):
        return None

    discriminator: str | None = None
    for metadata in args[1:]:
        candidate = getattr(metadata, "discriminator", None)
        if isinstance(candidate, str) and candidate.strip():
            discriminator = candidate
            break
    if discriminator is None:
        return None

    choice_to_model: dict[str, type[BaseModel]] = {}
    for variant in get_args(union_annotation):
        if not _is_model_annotation(variant):
            raise typer.BadParameter(
                "Discriminated union interactive prompting only supports "
                "BaseModel variants."
            )
        field_info = variant.model_fields.get(discriminator)
        if field_info is None:
            raise typer.BadParameter(
                f"Missing discriminator field '{discriminator}' in {variant.__name__}."
            )
        discriminator_annotation = field_info.annotation
        if get_origin(discriminator_annotation) is not Literal:
            raise typer.BadParameter(
                f"Discriminator field '{discriminator}' in {variant.__name__} "
                "must use Literal values."
            )
        for literal_value in get_args(discriminator_annotation):
            if not isinstance(literal_value, str):
                raise typer.BadParameter(
                    f"Unsupported discriminator value {literal_value!r} "
                    f"in {variant.__name__}; only string literals are supported."
                )
            choice_to_model[literal_value] = variant

    return discriminator, choice_to_model


def _field_prompt_label(field_name: str, is_optional: bool) -> str:
    return f"{field_name} (optional)" if is_optional else field_name


def _coerce_section_default_payload(default_value: Any) -> dict[str, Any] | None:
    if default_value in (_MISSING, None):
        return None

    if isinstance(default_value, BaseModel):
        return default_value.model_dump(mode="json", exclude_none=True)

    if isinstance(default_value, dict):
        return dict(default_value)

    return None


def _parse_bool_value(raw_value: str) -> bool:
    normalized = raw_value.strip().casefold()
    if normalized in {"true", "1", "yes", "y", "on"}:
        return True
    if normalized in {"false", "0", "no", "n", "off"}:
        return False
    raise ValueError(f"Invalid boolean value: {raw_value}")


def _coerce_list_item(field_name: str, item_annotation: Any, raw_value: str) -> Any:
    if get_origin(item_annotation) is Literal:
        choices = [
            value for value in get_args(item_annotation) if isinstance(value, str)
        ]
        canonical = {choice.casefold(): choice for choice in choices}
        normalized = raw_value.casefold()
        if normalized in canonical:
            return canonical[normalized]
        raise typer.BadParameter(
            f"Invalid value for '{field_name}' list item: {raw_value!r}. "
            f"Expected one of: {', '.join(choices)}."
        )

    if item_annotation is str:
        return raw_value

    if item_annotation is int:
        try:
            return int(raw_value)
        except ValueError as error:
            raise typer.BadParameter(
                f"Invalid integer in '{field_name}': {raw_value!r}."
            ) from error

    if item_annotation is float:
        try:
            return float(raw_value)
        except ValueError as error:
            raise typer.BadParameter(
                f"Invalid float in '{field_name}': {raw_value!r}."
            ) from error

    if item_annotation is bool:
        try:
            return _parse_bool_value(raw_value)
        except ValueError as error:
            raise typer.BadParameter(
                f"Invalid bool in '{field_name}': {raw_value!r}."
            ) from error

    return raw_value


# pylint: disable=too-many-locals,too-many-branches
def _prompt_list_field(
    field_name: str,
    prompt_label: str,
    annotation: Any,
    default_value: Any = _MISSING,
    *,
    allow_none: bool = False,
    required: bool = False,
) -> list[Any] | None:
    item_annotation = Any
    item_args = get_args(annotation)
    if item_args:
        item_annotation = _unwrap_optional_annotation(item_args[0])

    if _is_model_annotation(item_annotation) or (
        _extract_discriminated_union_schema(item_annotation) is not None
    ):
        items: list[Any] = []
        default_items = default_value if isinstance(default_value, list) else []
        if allow_none and not default_items:
            configure_field = typer.confirm(f"Configure {field_name}?", default=False)
            if not configure_field:
                return None

        for index, default_item in enumerate(default_items, start=1):
            typer.echo(f"\n[{field_name} item {index}]")
            section_default = _coerce_section_default_payload(default_item)
            items.append(_prompt_payload_for_schema(item_annotation, section_default))

        while True:
            add_more = typer.prompt(
                f"{prompt_label}: press Enter to finish, type any value to add item",
                default="",
                show_default=False,
            ).strip()
            if add_more == "":
                break

            typer.echo(f"\n[{field_name} item {len(items) + 1}]")
            items.append(_prompt_payload_for_schema(item_annotation))

        if required and not items:
            typer.echo(f"{field_name} requires at least one item.")
            typer.echo(f"\n[{field_name} item 1]")
            items.append(_prompt_payload_for_schema(item_annotation))

        return items

    default_text = ""
    if isinstance(default_value, list) and default_value:
        default_text = ", ".join(str(item) for item in default_value)

    while True:
        raw_values = typer.prompt(
            f"{prompt_label} (comma-separated)",
            default=default_text,
            show_default=default_text != "",
        ).strip()
        if raw_values == "":
            if allow_none:
                return None
            if required:
                typer.echo(f"{field_name} is required.")
                continue
            return []

        parsed_values = [
            _coerce_list_item(field_name, item_annotation, raw_item)
            for raw_item in (item.strip() for item in raw_values.split(","))
            if raw_item != ""
        ]
        if required and not parsed_values:
            typer.echo(f"{field_name} is required.")
            continue

        return parsed_values


# pylint: enable=too-many-locals,too-many-branches


def _prompt_literal_field(
    field_name: str,
    prompt_label: str,
    annotation: Any,
    default_value: Any = _MISSING,
    *,
    allow_none: bool = False,
) -> str | None:
    choices = [value for value in get_args(annotation) if isinstance(value, str)]
    if not choices:
        raise typer.BadParameter(
            f"Unsupported Literal values for '{field_name}'. Use --file."
        )

    prompt_text = f"{prompt_label} ({', '.join(choices)})"
    canonical = {choice.casefold(): choice for choice in choices}
    has_default = (
        default_value is not _MISSING
        and isinstance(default_value, str)
        and default_value.casefold() in canonical
    )
    while True:
        if allow_none and default_value in (_MISSING, None):
            selected = typer.prompt(prompt_text, default="", show_default=False).strip()
            if selected == "":
                return None
        elif has_default:
            selected = typer.prompt(
                prompt_text, default=canonical[default_value.casefold()]
            )
        else:
            selected = typer.prompt(prompt_text)

        selected = selected.strip()
        if selected == "":
            typer.echo(f"{field_name} is required.")
            continue
        if selected.casefold() in canonical:
            return canonical[selected.casefold()]

    raise typer.BadParameter(
        f"Invalid value for '{field_name}'. Expected one of: {', '.join(choices)}."
    )


def _prompt_discriminator_value(
    field_name: str, choices: list[str], default_value: Any = _MISSING
) -> str:
    prompt_text = f"{field_name} ({', '.join(choices)})"
    canonical = {choice.casefold(): choice for choice in choices}
    has_default = (
        isinstance(default_value, str) and default_value.casefold() in canonical
    )

    while True:
        if has_default:
            selected = typer.prompt(
                prompt_text, default=canonical[default_value.casefold()]
            )
        else:
            selected = typer.prompt(prompt_text)

        normalized = selected.strip().casefold()
        if normalized == "":
            typer.echo(f"{field_name} is required.")
            continue
        if normalized in canonical:
            return canonical[normalized]
        raise typer.BadParameter(
            f"Invalid value for '{field_name}'. Expected one of: {', '.join(choices)}."
        )


def _prompt_required_field(  # pylint: disable=too-many-branches,too-many-statements,too-many-return-statements
    field_name: str, annotation: Any, default_value: Any = _MISSING
) -> Any:
    is_optional = _is_optional_annotation(annotation)
    resolved_annotation = _unwrap_optional_annotation(annotation)
    prompt_label = _field_prompt_label(field_name, is_optional)

    prompt_value: Any
    if get_origin(resolved_annotation) is Literal:
        prompt_value = _prompt_literal_field(
            field_name,
            prompt_label,
            resolved_annotation,
            default_value=default_value,
            allow_none=is_optional,
        )
    elif _extract_discriminated_union_schema(resolved_annotation) is not None:
        if is_optional and default_value in (_MISSING, None):
            configure_field = typer.confirm(f"Configure {prompt_label}?", default=False)
            if not configure_field:
                return None
        typer.echo(f"\n[{prompt_label}]")
        section_default_payload = _coerce_section_default_payload(default_value)
        prompt_value = _prompt_payload_for_schema(
            resolved_annotation, section_default_payload
        )
    elif _is_model_annotation(resolved_annotation):
        if is_optional and default_value in (_MISSING, None):
            configure_field = typer.confirm(f"Configure {prompt_label}?", default=False)
            if not configure_field:
                return None
        typer.echo(f"\n[{prompt_label}]")
        section_default_payload = _coerce_section_default_payload(default_value)
        prompt_value = _prompt_payload_for_model(
            resolved_annotation, section_default_payload
        )
    elif resolved_annotation is bool:
        if is_optional and default_value in (_MISSING, None):
            set_field = typer.confirm(f"Set {prompt_label}?", default=False)
            if not set_field:
                return None
            prompt_value = typer.confirm(prompt_label, default=False)
        else:
            prompt_default = default_value if isinstance(default_value, bool) else True
            prompt_value = typer.confirm(prompt_label, default=prompt_default)
    elif resolved_annotation in (str, int, float):
        if resolved_annotation is str:
            if is_optional and default_value in (_MISSING, None):
                raw_string = typer.prompt(
                    prompt_label,
                    default="",
                    show_default=False,
                ).strip()
                if raw_string == "":
                    return None
                prompt_value = raw_string
            elif default_value is _MISSING:
                while True:
                    raw_string = typer.prompt(
                        prompt_label,
                        default="",
                        show_default=False,
                    ).strip()
                    if raw_string != "":
                        prompt_value = raw_string
                        break
                    typer.echo(f"{field_name} is required.")
            else:
                prompt_value = typer.prompt(
                    prompt_label, type=resolved_annotation, default=default_value
                )
        elif is_optional and default_value in (_MISSING, None):
            raw_scalar_value = typer.prompt(
                prompt_label,
                default="",
                show_default=False,
            ).strip()
            if raw_scalar_value == "":
                return None
            try:
                prompt_value = resolved_annotation(raw_scalar_value)
            except (TypeError, ValueError) as error:
                raise typer.BadParameter(
                    f"Invalid value for '{field_name}': {raw_scalar_value!r}."
                ) from error
        elif default_value is _MISSING:
            prompt_value = typer.prompt(prompt_label, type=resolved_annotation)
        else:
            prompt_value = typer.prompt(
                prompt_label, type=resolved_annotation, default=default_value
            )
    elif _is_list_annotation(resolved_annotation):
        prompt_value = _prompt_list_field(
            field_name,
            prompt_label,
            resolved_annotation,
            default_value=default_value,
            allow_none=is_optional,
            required=not is_optional,
        )
    elif get_origin(resolved_annotation) in (dict, tuple, set):
        raise typer.BadParameter(
            f"Unsupported interactive field type for '{field_name}'. Use --file."
        )
    elif is_optional and default_value in (_MISSING, None):
        prompt_value = typer.prompt(
            prompt_label, default="", show_default=False
        ).strip()
        if prompt_value == "":
            return None
    elif default_value is _MISSING:
        while True:
            prompt_value = typer.prompt(
                prompt_label, default="", show_default=False
            ).strip()
            if prompt_value != "":
                break
            typer.echo(f"{field_name} is required.")
    else:
        prompt_value = typer.prompt(prompt_label, default=str(default_value))

    return prompt_value


def _prompt_payload_for_model(
    model: type[BaseModel],
    base_payload: dict[str, Any] | None = None,
    *,
    skip_fields: set[str] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {} if base_payload is None else dict(base_payload)
    ignored_fields = skip_fields or set()
    for field_name, field_info in model.model_fields.items():
        if field_name in ignored_fields:
            continue
        if not _should_prompt_field(field_info, payload):
            continue

        default_value = payload.get(field_name, _MISSING)

        if default_value is _MISSING:
            model_default = field_info.get_default(call_default_factory=True)
            if model_default is not PydanticUndefined:
                default_value = model_default

        payload[field_name] = _prompt_required_field(
            field_name, field_info.annotation, default_value=default_value
        )

    return payload


def _prompt_payload_for_schema(
    schema: Any, base_payload: dict[str, Any] | None = None
) -> dict[str, Any]:
    if _is_model_annotation(schema):
        return _prompt_payload_for_model(schema, base_payload)

    discriminated_union = _extract_discriminated_union_schema(schema)
    if discriminated_union is None:
        raise typer.BadParameter(
            "Interactive mode supports BaseModel or discriminated union schemas."
        )

    discriminator, choice_to_model = discriminated_union
    payload: dict[str, Any] = {} if base_payload is None else dict(base_payload)
    choices = list(choice_to_model.keys())
    selected_choice = _prompt_discriminator_value(
        discriminator,
        choices,
        default_value=payload.get(discriminator, _MISSING),
    )

    payload[discriminator] = selected_choice
    selected_model = choice_to_model[selected_choice]
    return _prompt_payload_for_model(
        selected_model, payload, skip_fields={discriminator}
    )


def resolve_model_input(
    model: Any,
    *,
    interactive: bool,
    configuration_file: Path | None,
) -> Any:
    if interactive:
        payload = (
            load_payload_from_file(configuration_file)
            if configuration_file is not None
            else {}
        )
        payload = _prompt_payload_for_schema(model, payload)
    else:
        if configuration_file is None:
            raise typer.BadParameter("Provide --interactive or --file.")
        payload = load_payload_from_file(configuration_file)

    return validate_model_payload(model, payload)
