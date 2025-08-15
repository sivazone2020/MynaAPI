from typing import Any, Dict, List
import json
from datetime import datetime


def format_response(data: Any, success: bool = True, message: str = "") -> Dict[str, Any]:
    """Format API response consistently."""
    return {
        "data": data,
        "success": success,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def extract_keywords(text: str) -> List[str]:
    """Extract keywords from text for search/filtering."""
    # Simple keyword extraction - in production, use more sophisticated NLP
    import re
    words = re.findall(r'\b\w+\b', text.lower())
    return [word for word in words if len(word) > 3]


def validate_json(json_string: str) -> bool:
    """Validate if string is valid JSON."""
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False
