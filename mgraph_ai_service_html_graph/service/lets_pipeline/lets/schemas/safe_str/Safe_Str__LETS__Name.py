# ═══════════════════════════════════════════════════════════════════════════════
# Safe_Str__LETS__Name - Type-safe LETS transformation name
# Validates names like "html-to-dict", "dict-to-mgraph"
# ═══════════════════════════════════════════════════════════════════════════════

import re
from osbot_utils.type_safe.primitives.core.Safe_Str                              import Safe_Str


class Safe_Str__LETS__Name(Safe_Str):                                            # LETS transformation name
    max_length = 64                                                              # Max 64 characters
    regex      = re.compile(r'[^a-zA-Z0-9_\-]')                                  # Alphanumeric, underscore, hyphen
