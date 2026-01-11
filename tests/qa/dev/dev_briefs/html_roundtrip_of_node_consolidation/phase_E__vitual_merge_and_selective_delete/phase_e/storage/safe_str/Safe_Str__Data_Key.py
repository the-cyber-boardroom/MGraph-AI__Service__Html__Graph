# ═══════════════════════════════════════════════════════════════════════════════
# Safe_Str__Data_Key - Child data path key
# ═══════════════════════════════════════════════════════════════════════════════

import re
from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str


class Safe_Str__Data_Key(Safe_Str):                                             # Child data path key
    max_length = 256
    regex      = re.compile(r'[^a-zA-Z0-9_\-/]')                                 # Allows path separators
