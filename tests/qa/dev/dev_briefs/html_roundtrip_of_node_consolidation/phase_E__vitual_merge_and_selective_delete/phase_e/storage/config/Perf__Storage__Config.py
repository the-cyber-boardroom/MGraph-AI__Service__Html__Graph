# ═══════════════════════════════════════════════════════════════════════════════
# Perf__Storage__Config - Storage configuration manager with environment loading
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.utils.Env                                                      import get_env
from phase_e.storage.schemas.Schema__Perf__Storage__Config                      import Schema__Perf__Storage__Config
from phase_e.storage.enums.Enum__Storage_Mode                                   import Enum__Storage_Mode


class Perf__Storage__Config(Type_Safe):                                         # Storage configuration manager
    config : Schema__Perf__Storage__Config                                      # Configuration schema
    
    def setup(self) -> 'Perf__Storage__Config':                                 # Load config from environment
        storage_mode_str = get_env('PERF_STORAGE_MODE', 'local')
        
        try:                                                                    # Convert string to enum
            storage_mode = Enum__Storage_Mode(storage_mode_str)
        except ValueError:
            storage_mode = Enum__Storage_Mode.LOCAL
        
        self.config = Schema__Perf__Storage__Config(
            storage_mode       = storage_mode                                                   ,
            cache_namespace    = get_env('PERF_CACHE_NAMESPACE'   , 'perf-results'          )  ,
            local_storage_path = get_env('PERF_LOCAL_STORAGE_PATH', './perf_results'        )  )
        return self