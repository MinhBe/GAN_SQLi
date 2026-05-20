"""
state_detector.py -- Detect preprocessing state of a SQL payload.

State A (RAW):        "admin' AND sleep(5)--"
State B (NORMALIZED): "admin ' and sleep ( 5 ) --"   (spaces padded, lowercase)
State C (DELEX):      "admin ' and sleep ( __TIME__ ) --"  (values replaced by tokens)
"""

import re

_DELEX_TOKEN = re.compile(
    r'__(?:TIME|INT|STR|HEX|FLOAT|IDENT|DATE|IP|URL|EMAIL|WORD|NUM)__'
)

# State B heuristic: alphabetic word followed by space then '(' e.g. "sleep ("
_SPACED_CALL = re.compile(r'\b[a-z_]\w*\s+\(')


def detect_state(payload: str) -> str:
    """Return 'delex', 'normalized', or 'raw'."""
    if _DELEX_TOKEN.search(payload):
        return 'delex'
    if _SPACED_CALL.search(payload.lower()):
        return 'normalized'
    return 'raw'


def has_delex_tokens(payload: str) -> bool:
    return bool(_DELEX_TOKEN.search(payload))


def strip_delex_tokens(payload: str, replacement: str = '1') -> str:
    """Replace delex tokens with a concrete value for pattern matching."""
    p = _DELEX_TOKEN.sub(replacement, payload)
    # Also collapse extra spaces: "sleep ( 1 )" -> "sleep(1)"
    p = re.sub(r'\(\s+', '(', p)
    p = re.sub(r'\s+\)', ')', p)
    return p


if __name__ == '__main__':
    samples = [
        "admin' AND sleep(5)--",
        "admin ' and sleep ( 5 ) --",
        "admin ' and sleep ( __TIME__ ) --",
        "__STR__ ' or __INT__ = __INT__ --",
        "SELECT * FROM users WHERE id = 1",
    ]
    for s in samples:
        print(f"{detect_state(s):<12}  {s}")
