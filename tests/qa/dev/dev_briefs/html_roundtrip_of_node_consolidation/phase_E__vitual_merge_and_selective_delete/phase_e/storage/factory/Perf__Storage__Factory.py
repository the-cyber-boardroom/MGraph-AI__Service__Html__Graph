# ═══════════════════════════════════════════════════════════════════════════════
# Perf__Storage__Factory - Creates storage backend based on configuration
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                 import Optional
from mgraph_ai_service_cache_client.client.client_contract.Cache__Service__Fast_API__Client import Cache__Service__Fast_API__Client
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                              import type_safe
from phase_e.storage.base.Perf__Storage__Base                                               import Perf__Storage__Base
from phase_e.storage.backends.Perf__Storage__Local                                          import Perf__Storage__Local
from phase_e.storage.backends.Perf__Storage__Memory                                         import Perf__Storage__Memory
from phase_e.storage.backends.Perf__Storage__Cache_Service                                  import Perf__Storage__Cache_Service
from phase_e.storage.cache_service.Cache_Service__Client                                    import Cache_Service__Client
from phase_e.storage.schemas.Schema__Perf__Storage__Config                                  import Schema__Perf__Storage__Config
from phase_e.storage.safe_str.Safe_Str__Session_Name                                        import Safe_Str__Session_Name
from phase_e.storage.safe_str.Safe_Str__Target_Name                                         import Safe_Str__Target_Name
from phase_e.storage.enums.Enum__Storage_Mode                                               import Enum__Storage_Mode


class Perf__Storage__Factory(Type_Safe):                                                    # Storage factory
    config       : Schema__Perf__Storage__Config                                            # Configuration
    cache_client : Cache__Service__Fast_API__Client                                         # Cache client (for CACHE_SERVICE mode)
    session_name : Safe_Str__Session_Name                                                   # Session name (for CACHE_SERVICE mode)
    target_name  : Safe_Str__Target_Name                                                    # Target name (for CACHE_SERVICE mode)

    @type_safe
    def create(self) -> Optional[Perf__Storage__Base]:                                      # Create storage backend
        mode = self.config.storage_mode

        if mode == Enum__Storage_Mode.LOCAL:
            return Perf__Storage__Local(storage_path=self.config.local_storage_path)

        if mode == Enum__Storage_Mode.MEMORY:
            return Perf__Storage__Memory()

        if mode == Enum__Storage_Mode.CACHE_SERVICE:
            client = Cache_Service__Client(cache_client=self.cache_client)
            return Perf__Storage__Cache_Service(config       = self.config      ,
                                                client       = client           ,
                                                session_name = self.session_name,
                                                target_name  = self.target_name )

        return None                                                                         # Unknown mode