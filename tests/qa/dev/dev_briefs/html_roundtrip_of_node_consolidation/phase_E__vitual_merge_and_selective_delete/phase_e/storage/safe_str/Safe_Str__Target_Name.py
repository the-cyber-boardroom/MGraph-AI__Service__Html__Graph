# ═══════════════════════════════════════════════════════════════════════════════
# Safe_Str__Target_Name - Performance target identifier
# ═══════════════════════════════════════════════════════════════════════════════

import re
from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str


class Safe_Str__Target_Name(Safe_Str):                                          # Performance target identifier
    max_length = 100
    regex      = re.compile(r'[^a-zA-Z0-9_\-]')                                  # Alphanumeric, underscore, hyphen
