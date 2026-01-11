# ═══════════════════════════════════════════════════════════════════════════════
# Cache_Service__Client - Wrapper for MGraph-AI Cache Service Client
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                   import Optional
from mgraph_ai_service_cache_client.client.client_contract.Cache__Service__Fast_API__Client   import Cache__Service__Fast_API__Client
from mgraph_ai_service_cache_client.schemas.cache.Schema__Cache__Store__Response              import Schema__Cache__Store__Response
from mgraph_ai_service_cache_client.schemas.cache.data.Schema__Cache__Data__Store__Response import Schema__Cache__Data__Store__Response
from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type import Enum__Cache__Data_Type
from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Store__Strategy          import Enum__Cache__Store__Strategy
from osbot_utils.helpers.cache.Cache__Hash__Generator                                         import Cache__Hash__Generator
from osbot_utils.type_safe.Type_Safe                                                          import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path             import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Json__Field_Path import Safe_Str__Json__Field_Path
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                import type_safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                            import Cache_Id
from phase_e.storage.safe_str.Safe_Str__Data_Key                                              import Safe_Str__Data_Key
from phase_e.storage.safe_str.Safe_Str__Data_File_Id                                          import Safe_Str__Data_File_Id
from phase_e.storage.schemas.Schema__Perf__Entry                                              import Schema__Perf__Entry
from phase_e.storage.schemas.Schema__Perf__Storage__Config                                    import Schema__Perf__Storage__Config


class Cache_Service__Client(Type_Safe):                                                     # Cache service client wrapper
    config         : Schema__Perf__Storage__Config                                          # Storage configuration
    cache_client   : Cache__Service__Fast_API__Client                                       # Official cache client
    hash_generator : Cache__Hash__Generator                                                 # Hash generator for cache keys

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Entry Operations (key_based strategy)
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def store_entry(self                                              ,                     # Store main entry
                    cache_key       : Safe_Str__File__Path            ,                     # Semantic path key
                    file_id         : Safe_Str__Data_File_Id          ,                     # File identifier
                    json_field_path : Safe_Str__Json__Field_Path      ,                     # Field for cache_hash
                    perf_entry      : Schema__Perf__Entry                                   # Entry data
               ) -> Schema__Cache__Store__Response:
        data = perf_entry.json()
        return self.cache_client.store().store__json__cache_key(namespace       = self.config.cache_namespace            ,
                                                                strategy        = Enum__Cache__Store__Strategy.KEY_BASED ,
                                                                cache_key       = cache_key                              ,
                                                                body            = data                                   ,
                                                                file_id         = file_id                                ,
                                                                json_field_path = json_field_path                        )

    @type_safe
    def retrieve_entry(self                  ,                                              # Retrieve entry by ID
                       cache_id : Cache_Id   ) -> Optional[dict]:                           # Returns None if not found
        try:
            return self.cache_client.retrieve().retrieve__cache_id__json(cache_id  = cache_id                  ,
                                                                         namespace = self.config.cache_namespace)
        except Exception:
            return None

    @type_safe
    def hash_exists(self              ,                                                     # Check if hash exists
                    cache_hash : str  ) -> dict:                                            # Returns exists response
        return self.cache_client.exists().exists__hash__cache_hash(cache_hash = cache_hash                  ,
                                                                   namespace  = self.config.cache_namespace )

    @type_safe
    def find_entry_by_key(self                         ,                                    # Find entry by semantic key
                          cache_key : Safe_Str__File__Path) -> Cache_Id:                    # Returns Cache_Id if found
        cache_hash = self.hash_generator.from_string(cache_key)
        response   = self.cache_client.retrieve().retrieve__hash__cache_hash__cache_id(cache_hash = cache_hash                  ,
                                                                                       namespace  = self.config.cache_namespace )
        if response:
            return response.get('cache_id')
        return None

    # ═══════════════════════════════════════════════════════════════════════════
    # Child Data Operations
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def store_child_string(self                                 ,                                           # Store string child data
                           cache_id     : Cache_Id              ,                                           # Parent cache ID
                           data_key     : Safe_Str__Data_Key    ,                                           # Data path key
                           data_file_id : Safe_Str__Data_File_Id,                                           # File identifier
                           content      : str                   ) -> Schema__Cache__Data__Store__Response:                  # String content
        return self.cache_client.data_store().data__store_string__with__id_and_key(cache_id     = cache_id                   ,
                                                                                   namespace    = self.config.cache_namespace,
                                                                                   data_key     = data_key                   ,
                                                                                   data_file_id = data_file_id               ,
                                                                                   body         = content                    )

    @type_safe
    def store_child_json(self                                 ,                                             # Store JSON child data
                         cache_id     : Cache_Id              ,                                             # Parent cache ID
                         data_key     : Safe_Str__Data_Key    ,                                             # Data path key
                         data_file_id : Safe_Str__Data_File_Id,                                             # File identifier
                         data         : dict                  ) -> Schema__Cache__Data__Store__Response:    # response
        return self.cache_client.data_store().data__store_json__with__id_and_key(cache_id     = cache_id                   ,
                                                                                 namespace    = self.config.cache_namespace,
                                                                                 data_key     = data_key                   ,
                                                                                 data_file_id = data_file_id               ,
                                                                                 body         = data                       )

    @type_safe
    def retrieve_child_string(self                                 ,                        # Retrieve string child
                              cache_id     : Cache_Id              ,                        # Parent cache ID
                              data_key     : Safe_Str__Data_Key    ,                        # Data path key
                              data_file_id : Safe_Str__Data_File_Id) -> Optional[str]:      # Returns None if not found

        return self.cache_client.data().retrieve().data__string__with__id_and_key(cache_id     = cache_id                   ,
                                                                                  namespace    = self.config.cache_namespace,
                                                                                  data_key     = data_key                   ,
                                                                                  data_file_id = data_file_id               )

    @type_safe
    def retrieve_child_json(self                                 ,                          # Retrieve JSON child
                            cache_id     : Cache_Id              ,                          # Parent cache ID
                            data_key     : Safe_Str__Data_Key    ,                          # Data path key
                            data_file_id : Safe_Str__Data_File_Id) -> Optional[dict]:       # Returns None if not found
        return self.cache_client.data().retrieve().data__json__with__id_and_key(cache_id     = cache_id                   ,
                                                                                namespace    = self.config.cache_namespace,
                                                                                data_key     = data_key                   ,
                                                                                data_file_id = data_file_id               )


    @type_safe
    def delete_child(self                                 ,                                 # Delete child data file
                     cache_id     : Cache_Id              ,                                 # Parent cache ID
                     data_key     : Safe_Str__Data_Key    ,                                 # Data path key
                     data_file_id : Safe_Str__Data_File_Id,
                     data_type    : Enum__Cache__Data_Type,                                 # Data type
                ) -> bool:                                                                  # Success flag

        result  = self.cache_client.data().delete().delete__data__file__with__id_and_key(cache_id     = cache_id                   ,
                                                                                         namespace    = self.config.cache_namespace,
                                                                                         data_key     = data_key                   ,
                                                                                         data_file_id = data_file_id               ,
                                                                                         data_type    = data_type.value            )
        if result:
            return result.get('status') == 'success'
        return False


    # ═══════════════════════════════════════════════════════════════════════════
    # Health Check
    # ═══════════════════════════════════════════════════════════════════════════

    def health_check(self) -> bool:                                                         # Check service availability
        result = self.cache_client.info().health()
        if result:
            return result.get('status') == 'ok'
        else:
            return False