# ═══════════════════════════════════════════════════════════════════════════════
# IFD Snapshot - Custom Safe_Str Types
# Domain-specific string types for IFD snapshot generation
# ═══════════════════════════════════════════════════════════════════════════════

import re
from osbot_utils.type_safe.primitives.core.Safe_Str                               import Safe_Str
from osbot_utils.type_safe.primitives.core.Safe_UInt                              import Safe_UInt
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path


class Safe_Str__IFD_Version(Safe_Str):                                           # IFD version string (e.g., "v0.2.10")
    max_length = 40                                                              # Allow for "v0.2.10__snapshot" format
    regex      = re.compile(r'[^a-zA-Z0-9._-]')                                  # Allow alphanumeric, dot, underscore, hyphen


class Safe_Str__Logical_Name(Safe_Str__File__Path):                                          # Logical resource name (e.g., "js/services/api-client")
    max_length = 256


class Safe_Str__Resource_Type(Safe_Str):                                         # Resource type: 'css' or 'js'
    max_length = 10


class Safe_Str__File_Type(Safe_Str):                                             # File type: 'base' or 'surgical'
    max_length = 20


class Safe_UInt__Load_Order(Safe_UInt):                                          # Load order position (0-based)
    min_value = 0
    max_value = 10000
