# ═══════════════════════════════════════════════════════════════════════════════
# Safe_Str__Cache_Key - Type-safe cache semantic path
# Validates paths like "example.com/blog/post-1", "graphs/doc-abc123"
# ═══════════════════════════════════════════════════════════════════════════════

import re
from osbot_utils.type_safe.primitives.core.Safe_Str                              import Safe_Str


class Safe_Str__Cache_Key(Safe_Str):                                             # Cache semantic path
    max_length = 512                                                             # Max 512 characters
    regex      = re.compile(r'[^a-zA-Z0-9_\-/\.]')                               # URL-safe path chars
