# ═══════════════════════════════════════════════════════════════════════════════
# Safe_Str__Content_Hash - SHA-256 content hash (16 hex chars)
# ═══════════════════════════════════════════════════════════════════════════════

import re
from osbot_utils.type_safe.primitives.core.Safe_Str import Safe_Str


class Safe_Str__Content_Hash(Safe_Str):                             # Content hash (truncated SHA-256)
    max_length = 16                                                 # 16 hex characters
    regex      = re.compile(r'[^a-f0-9]')                           # Only lowercase hex chars
