# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Data__Paths__Response - Response listing file paths for a data key
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                      import Safe_UInt
from typing                                                                               import List
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path         import Safe_Str__File__Path


class Schema__Data__Paths__Response(Type_Safe):                                     # Response listing file paths
    success    : bool                                                               # Whether list succeeded
    file_paths : List[Safe_Str__File__Path]                                         # Available file identifiers
    count      : Safe_UInt                                                          # Number of files
