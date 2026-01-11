# ═══════════════════════════════════════════════════════════════════════════════
# Safe_Str__Session_Name - Performance session identifier
# ═══════════════════════════════════════════════════════════════════════════════

import re
from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str


class Safe_Str__Session_Name(Safe_Str):                                         # Performance session identifier
    max_length = 100
    regex      = re.compile(r'[^a-zA-Z0-9_\-]')                                  # Alphanumeric, underscore, hyphen
