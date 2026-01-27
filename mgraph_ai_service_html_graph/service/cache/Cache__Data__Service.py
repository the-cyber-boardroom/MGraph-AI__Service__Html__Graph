# ═══════════════════════════════════════════════════════════════════════════════
# Cache__Data__Service - Service layer for cache data file operations
# ═══════════════════════════════════════════════════════════════════════════════
from mgraph_ai_service_cache_client.schemas.cache.data.Schema__Cache__Data__List__Response  import Schema__Cache__Data__List__Response
from mgraph_ai_service_cache_client.schemas.cache.data.Schema__Cache__Data__Store__Response import Schema__Cache__Data__Store__Response
from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type              import Enum__Cache__Data_Type
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__Data_Key  import Safe_Str__Cache__File__Data_Key
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__File_Id   import Safe_Str__Cache__File__File_Id
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__Namespace       import Safe_Str__Cache__Namespace
from mgraph_ai_service_html_graph.schemas.cache.data.Schema__Data__Delete__Response         import Schema__Data__Delete__Response
from mgraph_ai_service_html_graph.schemas.cache.data.Schema__Data__Exists__Response         import Schema__Data__Exists__Response
from mgraph_ai_service_html_graph.schemas.cache.data.Schema__Data__Paths__Response          import Schema__Data__Paths__Response
from mgraph_ai_service_html_graph.schemas.cache.data.Schema__Data__Update__Response         import Schema__Data__Update__Response
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                  import Html_Cache__Client
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                          import Cache_Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                              import type_safe


class Cache__Data__Service(Type_Safe):                                              # Service for data file ops
    html_cache_client : Html_Cache__Client                                               # Cache client for storage

    # ═══════════════════════════════════════════════════════════════════════════════
    # List Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def list_files(self                                                  ,          # List all data files for entity
                   namespace : Safe_Str__Cache__Namespace                ,          # Cache namespace
                   cache_id  : Cache_Id                                  ,          # Entity cache ID
                   data_key  : Safe_Str__Cache__File__Data_Key = None    ,          # Optional data key filter
                   recursive : bool                            = True               # Include subdirectories
              ) -> Schema__Cache__Data__List__Response:

        result = self.html_cache_client.data__list(namespace = namespace ,
                                                   cache_id  = cache_id  ,
                                                   data_key  = data_key  ,
                                                   recursive = recursive )
        return result


    @type_safe
    def list_paths(self                                                  ,          # List data file paths for entity
                   namespace : Safe_Str__Cache__Namespace                ,          # Cache namespace
                   cache_id  : Cache_Id                                  ,          # Entity cache ID
                   data_key  : Safe_Str__Cache__File__Data_Key = None    ,          # Optional data key filter
                   recursive : bool                            = True               # Include subdirectories
              ) -> Schema__Data__Paths__Response:
        list_result = self.list_files(namespace = namespace ,
                                      cache_id  = cache_id  ,
                                      data_key  = data_key  ,
                                      recursive = recursive )

        file_paths = [f.file_path for f in list_result.files]
        count = len(file_paths)
        return Schema__Data__Paths__Response(success    = count > 0 ,
                                             file_paths = file_paths,
                                             count      = count     )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def get_string(self                                                  ,          # Get string content from data file
                   namespace    : Safe_Str__Cache__Namespace             ,          # Cache namespace
                   cache_id     : Cache_Id                               ,          # Entity cache ID
                   data_key     : Safe_Str__Cache__File__Data_Key        ,          # Data key path
                   data_file_id : Safe_Str__Cache__File__File_Id                    # File identifier
              ) -> str:
        return self.html_cache_client.data__retrieve_string(namespace    = namespace    ,
                                                            cache_id     = cache_id     ,
                                                            data_key     = data_key     ,
                                                            data_file_id = data_file_id )

    @type_safe
    def get_json(self                                                  ,            # Get JSON content from data file
                 namespace    : Safe_Str__Cache__Namespace             ,            # Cache namespace
                 cache_id     : Cache_Id                               ,            # Entity cache ID
                 data_key     : Safe_Str__Cache__File__Data_Key        ,            # Data key path
                 data_file_id : Safe_Str__Cache__File__File_Id                      # File identifier
            ) -> dict:
        return self.html_cache_client.data__retrieve_json(namespace    = namespace    ,
                                                          cache_id     = cache_id     ,
                                                          data_key     = data_key     ,
                                                          data_file_id = data_file_id )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Store Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def store_string(self                                                  ,        # Store string content as data file
                     namespace    : Safe_Str__Cache__Namespace             ,        # Cache namespace
                     cache_id     : Cache_Id                               ,        # Entity cache ID
                     data_key     : Safe_Str__Cache__File__Data_Key        ,        # Data key path
                     data_file_id : Safe_Str__Cache__File__File_Id         ,        # File identifier
                     content      : str                                             # String content to store
                ) -> Schema__Cache__Data__Store__Response:
        result = self.html_cache_client.data__store_string(namespace    = namespace    ,
                                                           cache_id     = cache_id     ,
                                                           data_key     = data_key     ,
                                                           data_file_id = data_file_id ,
                                                           content      = content      )
        return result


    @type_safe
    def store_json(self                                                  ,          # Store JSON content as data file
                   namespace    : Safe_Str__Cache__Namespace             ,          # Cache namespace
                   cache_id     : Cache_Id                               ,          # Entity cache ID
                   data_key     : Safe_Str__Cache__File__Data_Key        ,          # Data key path
                   data_file_id : Safe_Str__Cache__File__File_Id         ,          # File identifier
                   content      : dict                                              # JSON content to store
              ) -> Schema__Cache__Data__Store__Response:
        result = self.html_cache_client.data__store_json(namespace    = namespace    ,
                                                         cache_id     = cache_id     ,
                                                         data_key     = data_key     ,
                                                         data_file_id = data_file_id ,
                                                         data         = content      )
        return result

    # ═══════════════════════════════════════════════════════════════════════════════
    # Update Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def update_string(self                                                  ,       # Update string content in data file
                      namespace    : Safe_Str__Cache__Namespace             ,       # Cache namespace
                      cache_id     : Cache_Id                               ,       # Entity cache ID
                      data_key     : Safe_Str__Cache__File__Data_Key        ,       # Data key path
                      data_file_id : Safe_Str__Cache__File__File_Id         ,       # File identifier
                      content      : str                                            # New string content
                 ) -> Schema__Data__Update__Response:
        result = self.html_cache_client.data__update_string(namespace    = namespace    ,
                                                            cache_id     = cache_id     ,
                                                            data_key     = data_key     ,
                                                            data_file_id = data_file_id ,
                                                            content      = content      )

        return Schema__Data__Update__Response(success=result)

    @type_safe
    def update_json(self                                                  ,         # Update JSON content in data file
                    namespace    : Safe_Str__Cache__Namespace             ,         # Cache namespace
                    cache_id     : Cache_Id                               ,         # Entity cache ID
                    data_key     : Safe_Str__Cache__File__Data_Key        ,         # Data key path
                    data_file_id : Safe_Str__Cache__File__File_Id         ,         # File identifier
                    content      : dict                                             # New JSON content
               ) -> Schema__Data__Update__Response:
        result = self.html_cache_client.data__update_json(namespace    = namespace    ,
                                                          cache_id     = cache_id     ,
                                                          data_key     = data_key     ,
                                                          data_file_id = data_file_id ,
                                                          data         = content      )

        return Schema__Data__Update__Response(success=result)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Exists / Delete Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def exists(self                                                  ,              # Check if data file exists
               namespace    : Safe_Str__Cache__Namespace             ,              # Cache namespace
               cache_id     : Cache_Id                               ,              # Entity cache ID
               data_key     : Safe_Str__Cache__File__Data_Key        ,              # Data key path
               data_file_id : Safe_Str__Cache__File__File_Id         ,              # File identifier
               data_type    : Enum__Cache__Data_Type                                # Data type (string/json)
          ) -> Schema__Data__Exists__Response:
        result = self.html_cache_client.data__exists(namespace    = namespace    ,
                                                     cache_id     = cache_id     ,
                                                     data_key     = data_key     ,
                                                     data_file_id = data_file_id ,
                                                     data_type    = data_type    )

        return Schema__Data__Exists__Response(exists=result)

    @type_safe
    def delete(self                                                  ,              # Delete data file
               namespace    : Safe_Str__Cache__Namespace             ,              # Cache namespace
               cache_id     : Cache_Id                               ,              # Entity cache ID
               data_key     : Safe_Str__Cache__File__Data_Key        ,              # Data key path
               data_file_id : Safe_Str__Cache__File__File_Id         ,              # File identifier
               data_type    : Enum__Cache__Data_Type                                # Data type (string/json)
          ) -> Schema__Data__Delete__Response:
        result = self.html_cache_client.data__delete(namespace    = namespace    ,
                                                     cache_id     = cache_id     ,
                                                     data_key     = data_key     ,
                                                     data_file_id = data_file_id ,
                                                     data_type    = data_type    )

        return Schema__Data__Delete__Response(success = True   ,
                                              deleted = result )

    @type_safe
    def delete_all(self                                      ,                      # Delete all data files for entity
                   namespace : Safe_Str__Cache__Namespace    ,                      # Cache namespace
                   cache_id  : Cache_Id                                             # Entity cache ID
              ) -> Schema__Data__Delete__Response:
        result = self.html_cache_client.data__delete_all(namespace = namespace ,
                                                         cache_id  = cache_id  )

        return Schema__Data__Delete__Response(success = True   ,
                                              deleted = result )

    @type_safe
    def delete_all_with_key(self                                            ,       # Delete all files under data_key
                            namespace : Safe_Str__Cache__Namespace          ,       # Cache namespace
                            cache_id  : Cache_Id                            ,       # Entity cache ID
                            data_key  : Safe_Str__Cache__File__Data_Key             # Data key prefix to delete
                       ) -> Schema__Data__Delete__Response:
        result = self.html_cache_client.data__delete_all_with_key(namespace = namespace ,
                                                                  cache_id  = cache_id  ,
                                                                  data_key  = data_key  )

        return Schema__Data__Delete__Response(success = True   ,
                                              deleted = result )