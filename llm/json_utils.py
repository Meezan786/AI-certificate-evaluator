import json
import re
from typing import Any, Dict


def safe_json_parse(content: str, fallback: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Safely parse JSON content with multiple fallback strategies.

    Args:
        content: String content to parse as JSON
        fallback: Default value to return if parsing fails

    Returns:
        Parsed JSON dict or fallback value
    """
    if fallback is None:
        fallback = {}

    # Strategy 1: Direct JSON parsing
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Extract JSON from markdown code blocks
    try:
        # Look for ```json or ``` code blocks
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
    except (json.JSONDecodeError, AttributeError):
        pass

    # Strategy 3: Find first valid JSON object in text
    try:
        # Find content between first { and last }
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            json_str = content[start : end + 1]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    # Strategy 4: Try to clean common issues
    try:
        # Remove potential markdown or extra text
        cleaned = content.strip()
        if cleaned.startswith("```") and cleaned.endswith("```"):
            # Remove code block markers
            cleaned = "\n".join(cleaned.split("\n")[1:-1])
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # All strategies failed, return fallback
    return fallback


def validate_json_structure(data: Dict[str, Any], required_keys: list) -> bool:
    """
    Validate that a parsed JSON dict has required keys.

    Args:
        data: Dictionary to validate
        required_keys: List of required key names

    Returns:
        True if all required keys present, False otherwise
    """
    return all(key in data for key in required_keys)


def extract_with_default(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Extract value from dict with default fallback.

    Args:
        data: Dictionary to extract from
        key: Key to look for
        default: Default value if key not found

    Returns:
        Value at key or default
    """
    return data.get(key, default)
