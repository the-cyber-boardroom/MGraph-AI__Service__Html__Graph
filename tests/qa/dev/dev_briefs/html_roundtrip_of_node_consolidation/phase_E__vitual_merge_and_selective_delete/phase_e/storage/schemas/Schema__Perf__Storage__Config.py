# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Perf__Storage__Config - Storage configuration schema
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                   import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace import Safe_Str__Namespace
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path      import Safe_Str__File__Path
from phase_e.storage.enums.Enum__Storage_Mode                                          import Enum__Storage_Mode

# todo: move default values below to config variables

class Schema__Perf__Storage__Config(Type_Safe):                                 # Storage configuration
    storage_mode       : Enum__Storage_Mode    = Enum__Storage_Mode.LOCAL       # Backend mode
    cache_namespace    : Safe_Str__Namespace   = 'perf-results'                 # Cache namespace
    local_storage_path : Safe_Str__File__Path  = './perf_results'               # Local storage dir
