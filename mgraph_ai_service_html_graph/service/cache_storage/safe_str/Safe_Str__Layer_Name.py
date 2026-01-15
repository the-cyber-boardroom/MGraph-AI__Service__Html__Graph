# ═══════════════════════════════════════════════════════════════════════════════
# Safe_Str__Layer_Name - Type-safe cache layer name
# Validates names like "html-to-dict", "raw-html"
# ═══════════════════════════════════════════════════════════════════════════════

import re
from osbot_utils.type_safe.primitives.core.Safe_Str                              import Safe_Str


class Safe_Str__Layer_Name(Safe_Str):                                            # Cache layer name
    max_length = 32                                                              # Max 32 characters
    regex      = re.compile(r'[^a-zA-Z0-9_\-]')                                  # Simple identifier
