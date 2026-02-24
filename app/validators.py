"""Message validation logic."""

import re
from typing import Tuple


class ValidationError:
    """Represents a validation error."""
    
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message


def validate_message(text: str) -> Tuple[bool, str]:
    """
    Validate a message according to business rules.
    
    Rules:
    - Must be at least 5 characters
    - Must be less than 200 characters
    - Must not be empty/only whitespace
    - Must contain at least 1 alphanumeric character
    
    Args:
        text: The message text to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    
    if not text:
        return False, "Message must not be empty"
    
    stripped = text.strip()
    if not stripped:
        return False, "Message must not be empty or only whitespace"
    
    if len(stripped) < 5:
        return False, "Message must be at least 5 characters"
    
    if len(stripped) > 200:
        return False, "Message must be less than 200 characters"
    
    if not re.search(r'[a-zA-Z0-9]', stripped):
        return False, "Message must contain at least 1 alphanumeric character"
    
    return True, ""


def is_duplicate(text: str, existing_texts: set) -> bool:
    """
    Check if a message is a duplicate of an existing message.
    Uses normalized comparison (case-insensitive, whitespace normalized).
    
    Args:
        text: The message text to check
        existing_texts: Set of existing message texts
        
    Returns:
        True if duplicate, False otherwise
    """
    normalized = text.strip().lower()
    normalized_existing = {t.strip().lower() for t in existing_texts}
    return normalized in normalized_existing
