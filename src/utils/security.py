"""PathMatch AI - Security and Guardrails Utility.

Provides:
- Input sanitization and stripping of malicious HTML/JS.
- Prompt injection detection and defense boundaries.
- CSRF token utilities.
- In-memory rate limiting.
"""

import re
import html
import secrets
import time
from typing import Tuple, Dict

# In-memory rate limit store: ip -> list of timestamps
_RATE_LIMIT_STORE: Dict[str, list] = {}

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior)\s+instructions",
    r"you\s+are\s+now\s+(an?\s+)?unrestricted",
    r"system\s*:\s*you\s+are",
    r"forget\s+(your\s+)?prompt",
    r"bypass\s+(safety|content)\s+filters",
    r"new\s+system\s+directive",
    r"act\s+as\s+a\s+hacked",
    r"jailbreak",
]


def sanitize_text(text: str, max_length: int = 5000) -> str:
    """Sanitize user text input by escaping HTML and trimming excessive length."""
    if not text:
        return ""
    text = str(text).strip()
    if len(text) > max_length:
        text = text[:max_length]
    # Neutralize HTML tags
    sanitized = html.escape(text)
    return sanitized


def check_prompt_injection(text: str) -> Tuple[bool, str]:
    """Check if input contains potential prompt injection attempts.

    Returns (is_suspicious, sanitized_or_flagged_message)
    """
    if not text:
        return False, ""

    lowered = text.lower()
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            return True, "Potential prompt injection detected and neutralized."

    return False, text


def wrap_user_prompt(text: str) -> str:
    """Safely format and delimit untrusted student input within prompt boundaries."""
    sanitized = text.replace("```", "'''")
    return f"<student_input>\n{sanitized}\n</student_input>"


def generate_csrf_token() -> str:
    """Generate a secure cryptographically random CSRF token."""
    return secrets.token_hex(32)


def is_rate_limited(client_ip: str, limit: int = 60, window_seconds: int = 60) -> bool:
    """Check if client IP has exceeded request limit within the sliding window."""
    now = time.time()
    timestamps = _RATE_LIMIT_STORE.get(client_ip, [])
    # Filter out timestamps older than window
    valid_timestamps = [ts for ts in timestamps if now - ts < window_seconds]
    if len(valid_timestamps) >= limit:
        _RATE_LIMIT_STORE[client_ip] = valid_timestamps
        return True
    valid_timestamps.append(now)
    _RATE_LIMIT_STORE[client_ip] = valid_timestamps
    return False

