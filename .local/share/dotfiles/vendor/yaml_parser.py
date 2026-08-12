"""A small YAML subset parser used by the self-contained bootstrap."""

from dataclasses import dataclass
import re
from typing import Any


class YAMLParseError(Exception):
    """Raised when a supported YAML document is malformed."""


@dataclass(frozen=True)
class _Line:
    number: int
    indent: int
    text: str


def safe_load(stream: str | Any) -> Any:
    """Parse a YAML string or text stream without external dependencies."""
    content = stream.read() if hasattr(stream, "read") else stream
    if not isinstance(content, str):
        raise YAMLParseError("Input must be a string or file-like object")
    lines = _tokenize(content)
    if not lines:
        return {}
    if lines[0].indent:
        _error(lines[0], "root content must not be indented")
    value, index = _parse_block(lines, 0, 0)
    if index != len(lines):
        _error(lines[index], "unexpected content")
    return value


def _tokenize(content: str) -> list[_Line]:
    lines: list[_Line] = []
    for number, raw in enumerate(content.splitlines(), start=1):
        if "\t" in raw:
            raise YAMLParseError(f"Line {number}: tab indentation is not supported")
        text = _strip_comment(raw).rstrip()
        if not text.strip():
            continue
        indent = len(text) - len(text.lstrip(" "))
        lines.append(_Line(number, indent, text[indent:]))
    return lines


def _parse_block(lines: list[_Line], index: int, indent: int) -> tuple[object, int]:
    if lines[index].indent != indent:
        _error(lines[index], f"expected indentation {indent}, got {lines[index].indent}")
    if lines[index].text == "-" or lines[index].text.startswith("- "):
        return _parse_block_list(lines, index, indent)
    return _parse_block_mapping(lines, index, indent)


def _parse_block_mapping(lines: list[_Line], index: int, indent: int) -> tuple[dict[str, object], int]:
    result: dict[str, object] = {}
    while index < len(lines):
        line = lines[index]
        if line.indent < indent:
            break
        if line.indent > indent:
            _error(line, f"unexpected indentation {line.indent}; expected {indent}")
        if line.text == "-" or line.text.startswith("- "):
            _error(line, "list item is not valid in a mapping")
        key, scalar = _mapping_entry(line)
        if key in result:
            _error(line, f"duplicate mapping key {key!r}")
        index += 1
        if scalar:
            result[key] = _parse_scalar(scalar, line.number)
            continue
        if index < len(lines) and lines[index].indent > indent:
            result[key], index = _parse_block(lines, index, lines[index].indent)
        else:
            result[key] = None
    return result, index


def _parse_block_list(lines: list[_Line], index: int, indent: int) -> tuple[list[object], int]:
    result: list[object] = []
    while index < len(lines):
        line = lines[index]
        if line.indent < indent:
            break
        if line.indent > indent:
            _error(line, f"unexpected indentation {line.indent}; expected {indent}")
        if not (line.text == "-" or line.text.startswith("- ")):
            _error(line, "expected a list item")
        item = line.text[1:].strip()
        index += 1
        if not item:
            if index < len(lines) and lines[index].indent > indent:
                value, index = _parse_block(lines, index, lines[index].indent)
            else:
                value = None
        elif _has_mapping_separator(item):
            value, index = _parse_list_mapping_item(lines, index, indent, line, item)
        else:
            value = _parse_scalar(item, line.number)
            if index < len(lines) and lines[index].indent > indent:
                _error(lines[index], "scalar list item cannot have nested content")
        result.append(value)
    return result, index


def _parse_list_mapping_item(
    lines: list[_Line], index: int, parent_indent: int, first_line: _Line, first: str
) -> tuple[dict[str, object], int]:
    key, scalar = _mapping_entry(_Line(first_line.number, first_line.indent, first))
    result: dict[str, object] = {}
    if scalar:
        result[key] = _parse_scalar(scalar, first_line.number)
    elif index < len(lines) and lines[index].indent > parent_indent:
        result[key], index = _parse_block(lines, index, lines[index].indent)
    else:
        result[key] = None

    child_indent: int | None = None
    while index < len(lines):
        line = lines[index]
        if line.indent <= parent_indent:
            break
        if child_indent is None:
            child_indent = line.indent
        if line.indent != child_indent:
            _error(line, f"inconsistent mapping-list indentation; expected {child_indent}")
        if line.text == "-" or line.text.startswith("- "):
            _error(line, "list item is not valid in a mapping list item")
        child_key, child_scalar = _mapping_entry(line)
        if child_key in result:
            _error(line, f"duplicate mapping key {child_key!r}")
        index += 1
        if child_scalar:
            result[child_key] = _parse_scalar(child_scalar, line.number)
        elif index < len(lines) and lines[index].indent > child_indent:
            result[child_key], index = _parse_block(lines, index, lines[index].indent)
        else:
            result[child_key] = None
    return result, index


def _mapping_entry(line: _Line) -> tuple[str, str]:
    separator = _mapping_separator(line.text)
    if separator is None:
        _error(line, "expected a mapping key followed by ':'")
    key = line.text[:separator].strip()
    if not key:
        _error(line, "mapping key cannot be empty")
    return key, line.text[separator + 1:].strip()


def _parse_scalar(value: str, number: int) -> object:
    value = value.strip()
    if value == "[]":
        return []
    if value == "{}":
        return {}
    if value.startswith("["):
        return _parse_flow_list(value, number)
    if value.startswith(("'", '"')):
        quote = value[0]
        if len(value) < 2 or not value.endswith(quote):
            raise YAMLParseError(f"Line {number}: unterminated quoted scalar")
        return value[1:-1]
    lower = value.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    if lower in {"null", "none", "~"}:
        return None
    if re.fullmatch(r"[-+]?\d+", value):
        return int(value)
    if re.fullmatch(r"[-+]?(?:\d+\.\d*|\d*\.\d+)", value):
        return float(value)
    return value


def _parse_flow_list(value: str, number: int) -> list[object]:
    if not value.endswith("]"):
        raise YAMLParseError(f"Line {number}: unterminated flow list")
    inner = value[1:-1].strip()
    if not inner:
        return []
    return [_parse_scalar(item, number) for item in _split_flow(inner, number)]


def _split_flow(value: str, number: int) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    quote: str | None = None
    depth = 0
    for char in value:
        if quote:
            current.append(char)
            if char == quote:
                quote = None
        elif char in {"'", '"'}:
            quote = char
            current.append(char)
        elif char == "[":
            depth += 1
            current.append(char)
        elif char == "]":
            if depth == 0:
                raise YAMLParseError(f"Line {number}: unmatched closing bracket")
            depth -= 1
            current.append(char)
        elif char == "," and depth == 0:
            item = "".join(current).strip()
            if not item:
                raise YAMLParseError(f"Line {number}: empty flow-list item")
            parts.append(item)
            current = []
        else:
            current.append(char)
    if quote or depth:
        raise YAMLParseError(f"Line {number}: unterminated flow value")
    item = "".join(current).strip()
    if not item:
        raise YAMLParseError(f"Line {number}: empty flow-list item")
    parts.append(item)
    return parts


def _strip_comment(value: str) -> str:
    quote: str | None = None
    depth = 0
    for index, char in enumerate(value):
        if quote:
            if char == quote:
                quote = None
        elif char in {"'", '"'}:
            quote = char
        elif char == "[":
            depth += 1
        elif char == "]" and depth:
            depth -= 1
        elif char == "#" and depth == 0:
            return value[:index]
    return value


def _mapping_separator(value: str) -> int | None:
    quote: str | None = None
    depth = 0
    for index, char in enumerate(value):
        if quote:
            if char == quote:
                quote = None
        elif char in {"'", '"'}:
            quote = char
        elif char == "[":
            depth += 1
        elif char == "]" and depth:
            depth -= 1
        elif char == ":" and depth == 0:
            return index
    return None


def _has_mapping_separator(value: str) -> bool:
    return _mapping_separator(value) is not None


def _error(line: _Line, message: str) -> None:
    raise YAMLParseError(f"Line {line.number}: {message}")


load = safe_load
YAMLError = YAMLParseError
