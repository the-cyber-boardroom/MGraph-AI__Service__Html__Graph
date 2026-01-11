# ═══════════════════════════════════════════════════════════════════════════════
# Safe_Str__Data_File_Id - Child data file identifier
# ═══════════════════════════════════════════════════════════════════════════════

import re
from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str


class Safe_Str__Data_File_Id(Safe_Str):                                         # Child data file identifier
    max_length = 128
    regex      = re.compile(r'[^a-zA-Z0-9_\-\.]')                                # Allows dots for extensions
