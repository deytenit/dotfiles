"""
Minimal YAML parser for dotfiles bootstrap.

This is a simple YAML parser designed specifically for the dotfiles strap files format.
It supports a subset of YAML that covers our use cases:
- Simple key-value pairs (string, number, boolean)
- Lists (flow style and block style)
- Nested dictionaries (1-2 levels)
- Comments

Not supported (not needed for our use case):
- Advanced YAML features (anchors, aliases, tags, etc.)
- Multi-line strings with complex formatting
- Complex nested structures beyond 2-3 levels
"""

import re
from typing import Any, Dict, List, Union


class YAMLParseError(Exception):
    """Exception raised when YAML parsing fails."""
    pass


def safe_load(stream: Union[str, Any]) -> Dict[str, Any]:
    """
    Parse a YAML string or file-like object into a Python dictionary.
    
    Args:
        stream: YAML content as string or file-like object
        
    Returns:
        Parsed YAML as dictionary
        
    Raises:
        YAMLParseError: If parsing fails
    """
    if hasattr(stream, 'read'):
        content = stream.read()
    else:
        content = stream
    
    if not isinstance(content, str):
        raise YAMLParseError("Input must be a string or file-like object")
    
    return _parse_yaml(content)


def _parse_yaml(content: str) -> Dict[str, Any]:
    """
    Parse YAML content into a dictionary.
    
    Args:
        content: YAML string
        
    Returns:
        Parsed dictionary
    """
    lines = content.split('\n')
    result = {}
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        
        # Skip empty lines and comments
        if not stripped or stripped.startswith('#'):
            i += 1
            continue
        
        # Calculate indentation level
        indent = len(line) - len(stripped)
        
        # Only parse root level (indent 0)
        if indent == 0:
            key, value, lines_consumed = _parse_line(lines, i)
            if key:
                result[key] = value
            i += lines_consumed
        else:
            i += 1
    
    return result


def _parse_line(lines: List[str], start_idx: int) -> tuple:
    """
    Parse a line and its potential children.
    
    Args:
        lines: All lines
        start_idx: Index of current line
        
    Returns:
        Tuple of (key, value, lines_consumed)
    """
    line = lines[start_idx]
    stripped = line.strip()
    
    # Handle key-value pair
    if ':' in stripped:
        parts = stripped.split(':', 1)
        key = parts[0].strip()
        value_part = parts[1].strip() if len(parts) > 1 else ''
        
        # If value is on same line
        if value_part:
            # Check for inline list [item1, item2]
            if value_part.startswith('[') and value_part.endswith(']'):
                value = _parse_flow_list(value_part)
                return key, value, 1
            else:
                # Simple value
                value = _parse_scalar(value_part)
                return key, value, 1
        
        # Value might be on next lines (list or dict)
        base_indent = len(line) - len(line.lstrip())
        next_idx = start_idx + 1
        
        # Check if next line is a list or nested structure
        if next_idx < len(lines):
            next_line = lines[next_idx]
            next_stripped = next_line.lstrip()
            next_indent = len(next_line) - len(next_stripped)
            
            # If next line is more indented, it's a child
            if next_indent > base_indent and next_stripped:
                if next_stripped.startswith('-'):
                    # It's a list
                    value, consumed = _parse_list(lines, next_idx, next_indent)
                    return key, value, consumed + 1
                elif ':' in next_stripped:
                    # It's a nested dict
                    value, consumed = _parse_dict(lines, next_idx, next_indent)
                    return key, value, consumed + 1
        
        # Empty value
        return key, None, 1
    
    return None, None, 1


def _parse_list(lines: List[str], start_idx: int, expected_indent: int) -> tuple:
    """
    Parse a block-style list.
    
    Args:
        lines: All lines
        start_idx: Starting index
        expected_indent: Expected indentation level
        
    Returns:
        Tuple of (list_value, lines_consumed)
    """
    result = []
    i = start_idx
    
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        
        # Stop if we're back at a lower indentation
        if stripped and indent < expected_indent:
            break
        
        # Skip empty lines and comments
        if not stripped or stripped.startswith('#'):
            i += 1
            continue
        
        # Process list item
        if indent == expected_indent and stripped.startswith('-'):
            item_content = stripped[1:].strip()
            
            if not item_content:
                # Multi-line list item or nested structure (not common in our case)
                i += 1
                continue
            
            # Check for inline list [a, b]
            if item_content.startswith('[') and item_content.endswith(']'):
                item = _parse_flow_list(item_content)
            else:
                # Simple item or string
                item = _parse_scalar(item_content)
            
            result.append(item)
            i += 1
        else:
            i += 1
    
    return result, i - start_idx


def _parse_dict(lines: List[str], start_idx: int, expected_indent: int) -> tuple:
    """
    Parse a nested dictionary.
    
    Args:
        lines: All lines
        start_idx: Starting index
        expected_indent: Expected indentation level
        
    Returns:
        Tuple of (dict_value, lines_consumed)
    """
    result = {}
    i = start_idx
    
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        
        # Stop if we're back at a lower indentation
        if stripped and indent < expected_indent:
            break
        
        # Skip empty lines and comments
        if not stripped or stripped.startswith('#'):
            i += 1
            continue
        
        # Process key-value
        if indent == expected_indent and ':' in stripped:
            parts = stripped.split(':', 1)
            key = parts[0].strip()
            value_part = parts[1].strip() if len(parts) > 1 else ''
            
            if value_part:
                result[key] = _parse_scalar(value_part)
            else:
                result[key] = None
            
            i += 1
        else:
            i += 1
    
    return result, i - start_idx


def _parse_flow_list(content: str) -> List[Any]:
    """
    Parse a flow-style list: [item1, item2, item3]
    
    Args:
        content: String like "[item1, item2]"
        
    Returns:
        List of items
    """
    # Remove brackets
    inner = content[1:-1].strip()
    
    if not inner:
        return []
    
    # Split by comma, but respect nested brackets
    items = []
    current = []
    bracket_depth = 0
    
    for char in inner:
        if char == '[':
            bracket_depth += 1
            current.append(char)
        elif char == ']':
            bracket_depth -= 1
            current.append(char)
        elif char == ',' and bracket_depth == 0:
            item_str = ''.join(current).strip()
            if item_str:
                items.append(_parse_scalar(item_str))
            current = []
        else:
            current.append(char)
    
    # Don't forget the last item
    if current:
        item_str = ''.join(current).strip()
        if item_str:
            items.append(_parse_scalar(item_str))
    
    return items


def _parse_scalar(value: str) -> Any:
    """
    Parse a scalar value (string, number, boolean, or list).
    
    Args:
        value: String value
        
    Returns:
        Parsed value
    """
    value = value.strip()
    
    # Remove quotes if present
    if (value.startswith('"') and value.endswith('"')) or \
       (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    
    # Boolean
    if value.lower() == 'true':
        return True
    if value.lower() == 'false':
        return False
    
    # Null/None
    if value.lower() in ('null', 'none', '~'):
        return None
    
    # Number (int or float)
    try:
        if '.' in value:
            return float(value)
        else:
            return int(value)
    except ValueError:
        pass
    
    # Default to string
    return value


# Alias for compatibility with PyYAML
load = safe_load

