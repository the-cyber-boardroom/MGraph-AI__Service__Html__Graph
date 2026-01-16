# ═══════════════════════════════════════════════════════════════════════════════
# Safe_Str__LETS__Data_Key - Type-safe LETS data path key
# Validates paths like "html-to-dict", "html-to-dict/v2"
# ═══════════════════════════════════════════════════════════════════════════════

import re
from osbot_utils.type_safe.primitives.core.Safe_Str                              import Safe_Str


class Safe_Str__LETS__Data_Key(Safe_Str):                                        # LETS data path key
    max_length = 128                                                             # Max 128 characters
    regex      = re.compile(r'[^a-zA-Z0-9_\-/]')                                 # Allows path separators
