# ═══════════════════════════════════════════════════════════════════════════════
# Perf__Storage__Cache_Service - Remote cache service storage backend
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                 import Optional, List, Tuple

from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type import Enum__Cache__Data_Type

from osbot_utils.type_safe.type_safe_core.decorators.type_safe                              import type_safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                          import Cache_Id
from phase_e.storage.base.Perf__Storage__Base                                               import Perf__Storage__Base
from phase_e.storage.schemas.Schema__Perf__Storage__Config                                  import Schema__Perf__Storage__Config
from phase_e.storage.schemas.Schema__Perf__Entry                                            import Schema__Perf__Entry
from phase_e.storage.cache_service.Cache_Service__Client                                    import Cache_Service__Client
from phase_e.storage.safe_str.Safe_Str__Session_Name                                        import Safe_Str__Session_Name
from phase_e.storage.safe_str.Safe_Str__Target_Name                                         import Safe_Str__Target_Name
from phase_e.storage.safe_str.Safe_Str__Data_Key                                            import Safe_Str__Data_Key
from phase_e.storage.safe_str.Safe_Str__Data_File_Id                                        import Safe_Str__Data_File_Id


DEFAULT__PERF_STORAGE__SESSION_NAME = 'default-session'
DEFAULT__PERF_STORAGE__TARGET_NAME  = 'default-target'


class Perf__Storage__Cache_Service(Perf__Storage__Base):                                    # Cache service backend
    config       : Schema__Perf__Storage__Config                                            # Configuration
    client       : Cache_Service__Client                                                    # Cache service client
    session_name : Safe_Str__Session_Name = DEFAULT__PERF_STORAGE__SESSION_NAME             # Current session
    target_name  : Safe_Str__Target_Name  = DEFAULT__PERF_STORAGE__TARGET_NAME              # Current target

    def __init__(self, **kwargs):                                                           # Initialize with config binding
        super().__init__(**kwargs)
        self.client.config = self.config                                                    # Bind config to client

    # ═══════════════════════════════════════════════════════════════════════════
    # Cache Key/Hash Generation
    # ═══════════════════════════════════════════════════════════════════════════

    def cache_key(self) -> str:                                                             # Generate semantic cache key
        return f"sessions/{self.session_name}/targets/{self.target_name}"

    def cache_hash(self) -> str:                                                            # Generate hash from cache_key
        return self.client.hash_generator.from_string(self.cache_key())

    # ═══════════════════════════════════════════════════════════════════════════
    # Entry Management
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def ensure_entry(self) -> Cache_Id:                                                     # Ensure perf-entry exists
        cache_key = self.cache_key()
        cache_id  = self.client.find_entry_by_key(cache_key=cache_key)                      # Check if entry exists

        if not cache_id:
            json_field_path = 'cache_key'
            perf_entry      = Schema__Perf__Entry(session_name = self.session_name,
                                                  target_name  = self.target_name ,
                                                  cache_key    = cache_key        )
            store_response  = self.client.store_entry(cache_key       = cache_key                            ,
                                                      file_id         = Safe_Str__Data_File_Id('perf-entry') ,
                                                      json_field_path = json_field_path                      ,
                                                      perf_entry      = perf_entry                           )
            cache_id = store_response.cache_id
        return cache_id

    # ═══════════════════════════════════════════════════════════════════════════
    # Key Parsing
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def parse_key(self            ,                                                         # Parse key into parts
                  key : str       ) -> Tuple[Safe_Str__Data_Key, Safe_Str__Data_File_Id]:
        parts = key.rsplit('/', 1)
        if len(parts) == 2:
            return Safe_Str__Data_Key(parts[0]), Safe_Str__Data_File_Id(parts[1])
        return Safe_Str__Data_Key(''), Safe_Str__Data_File_Id(parts[0])

    # ═══════════════════════════════════════════════════════════════════════════
    # Abstract Method Implementations
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def save(self                  ,                                                        # Save JSON data
             key  : str            ,                                                        # Data key path
             data : dict           ) -> bool:                                               # Data to store
        cache_id               = self.ensure_entry()
        data_key, data_file_id = self.parse_key(key)
        result                 = self.client.store_child_json(cache_id     = cache_id    ,
                                                              data_key     = data_key    ,
                                                              data_file_id = data_file_id,
                                                              data         = data        )
        return result is not None

    @type_safe
    def save_string(self                  ,                                                 # Save string content
                    key     : str         ,                                                 # Data key path
                    content : str         ) -> bool:                                        # String content
        cache_id               = self.ensure_entry()
        data_key, data_file_id = self.parse_key(key)
        result                 = self.client.store_child_string(cache_id     = cache_id    ,
                                                                data_key     = data_key    ,
                                                                data_file_id = data_file_id,
                                                                content      = content     )
        return result is not None

    @type_safe
    def load(self             ,                                                             # Load JSON data
             key : str        ) -> Optional[dict]:                                          # Returns None if not found
        cache_id = self.ensure_entry()
        if not cache_id:
            return None
        data_key, data_file_id = self.parse_key(key)
        return self.client.retrieve_child_json(cache_id     = cache_id    ,
                                               data_key     = data_key    ,
                                               data_file_id = data_file_id)

    @type_safe
    def load_string(self             ,                                                      # Load string content
                    key : str        ) -> Optional[str]:                                    # Returns None if not found
        cache_id = self.ensure_entry()
        if not cache_id:
            return None
        data_key, data_file_id = self.parse_key(key)
        return self.client.retrieve_child_string(cache_id     = cache_id    ,
                                                 data_key     = data_key    ,
                                                 data_file_id = data_file_id)

    @type_safe
    def exists(self             ,                                                           # Check if key exists
               key : str        ) -> bool:
        if self.load(key) :                                                 # todo: review why we need to calls
            return True

        if self.load_string(key):
            return True

        return False

    @type_safe
    def delete(self                             ,                                                       # Delete data by key
               key : str                        ,
               data_type: Enum__Cache__Data_Type) -> bool:
        cache_id = self.ensure_entry()                              # todo: review this use of ensure_entry, this doesn't feel right
        if not cache_id:
            return False
        data_key, data_file_id = self.parse_key(key)
        return self.client.delete_child(cache_id     = cache_id    ,
                                        data_key     = data_key    ,
                                        data_file_id = data_file_id,
                                        data_type    = data_type   )
    @type_safe
    def delete__string(self      ,                                                       # Delete string by key
                      key : str  ,
                 ) -> bool:
        return self.delete(key       = key,
                           data_type = Enum__Cache__Data_Type.STRING)

    @type_safe
    def list_keys(self                  ,                                                   # List child data files
                  prefix : str = ''     ) -> List[str]:                                     # Requires refs endpoint
        return []                                                                           # TODO: implement via refs API