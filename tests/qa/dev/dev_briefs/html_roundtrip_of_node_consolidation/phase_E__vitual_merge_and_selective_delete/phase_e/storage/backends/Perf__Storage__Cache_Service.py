# ═══════════════════════════════════════════════════════════════════════════════
# Perf__Storage__Cache_Service - Remote cache service storage backend
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                                  import Optional, List, Tuple
from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type                               import Enum__Cache__Data_Type
from mgraph_ai_service_cache_client.schemas.routes.admin.Schema__Routes__Admin__Storage__Files_All__Response import Schema__Routes__Admin__Storage__Files_All__Response
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Cache_Hash                     import Safe_Str__Cache_Hash
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                            import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace                       import Safe_Str__Namespace
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                               import type_safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                           import Cache_Id
from phase_e.storage.base.Perf__Storage__Base                                                                import Perf__Storage__Base
from phase_e.storage.schemas.Schema__Perf__Storage__Config                                                   import Schema__Perf__Storage__Config
from phase_e.storage.schemas.Schema__Perf__Entry                                                             import Schema__Perf__Entry
from phase_e.storage.cache_service.Cache_Service__Client                                                     import Cache_Service__Client
from phase_e.storage.safe_str.Safe_Str__Session_Name                                                         import Safe_Str__Session_Name
from phase_e.storage.safe_str.Safe_Str__Target_Name                                                          import Safe_Str__Target_Name
from phase_e.storage.safe_str.Safe_Str__Data_Key                                                             import Safe_Str__Data_Key
from phase_e.storage.safe_str.Safe_Str__Data_File_Id                                                         import Safe_Str__Data_File_Id


DEFAULT__PERF_STORAGE__SESSION_NAME         = 'default-session'
DEFAULT__PERF_STORAGE__TARGET_NAME          = 'default-target'
DEFAULT__PERF_STORAGE__FILE_ID__PERF_ENTRY  = 'perf-entry'

class Perf__Storage__Cache_Service(Perf__Storage__Base):                                    # Cache service backend
    config       : Schema__Perf__Storage__Config                                            # Configuration
    client       : Cache_Service__Client                                                    # Cache service client
    session_name : Safe_Str__Session_Name = DEFAULT__PERF_STORAGE__SESSION_NAME             # Current session
    target_name  : Safe_Str__Target_Name  = DEFAULT__PERF_STORAGE__TARGET_NAME              # Current target
    file_id      : Safe_Str__Data_File_Id = DEFAULT__PERF_STORAGE__FILE_ID__PERF_ENTRY      # File_id, todo: refactor methods below so that we can make this generic

    def __init__(self, **kwargs):                                                           # Initialize with config binding
        super().__init__(**kwargs)
        if self.client:                             # todo: see if self.client is setup
            self.client.config = self.config        #       this happens during the type_safe template creation (figure out a better way to handle this side effect and to do this type of dependency injection)                                     # Bind config to client

    # ═══════════════════════════════════════════════════════════════════════════
    # Cache Key/Hash Generation
    # ═══════════════════════════════════════════════════════════════════════════

    def cache_id(self) -> Optional[Cache_Id]:                                               # Get cache_id (may be None)
        cache_key = self.cache_key()
        cache_id  = self.client.find_entry_by_key(cache_key=cache_key)                      # Check if entry exists
        return cache_id

    def cache_hash(self) -> Safe_Str__Cache_Hash:                                           # Generate hash from cache_key
        cache_key  = self.cache_key()
        cache_hash = self.client.hash_generator.from_string(cache_key)
        return cache_hash

    def cache_key(self) -> str:                                                             # Generate semantic cache key
        return f"sessions/{self.session_name}/targets/{self.target_name}"


    # ═══════════════════════════════════════════════════════════════════════════
    # Entry Management
    # ═══════════════════════════════════════════════════════════════════════════


    @type_safe
    def create_file__if_not_available(self) -> Cache_Id:   # Ensure perf-entry exists
        cache_id = self.cache_id()

        if not cache_id:
            cache_key       = self.cache_key()
            json_field_path = 'cache_key'
            perf_entry      = Schema__Perf__Entry(session_name = self.session_name,
                                                  target_name  = self.target_name ,
                                                  cache_key    = cache_key        )
            store_response  = self.client.store_entry(cache_key       = cache_key       ,
                                                      file_id         = self.file_id    ,
                                                      json_field_path = json_field_path ,
                                                      perf_entry      = perf_entry      )
            cache_id = store_response.cache_id
        return cache_id

    def create_file__perf_entry(self) -> Cache_Id:                                          # todo: remove this legacy method
        self.file_id = DEFAULT__PERF_STORAGE__FILE_ID__PERF_ENTRY
        return self.create_file__if_not_available()

    def data_folder(self) -> Safe_Str__File__Path:
        return f'{self.namespace()}/data/key-based/{self.cache_key()}/{self.file_id}/data'

    def data_file(self,
                  data_type: Enum__Cache__Data_Type,
                  key_data : Safe_Str__File__Path,
                  ) -> Safe_Str__File__Path:
        if data_type == Enum__Cache__Data_Type.JSON:
            extension = 'json'
        elif data_type == Enum__Cache__Data_Type.STRING:
            extension = 'txt'
        elif data_type == Enum__Cache__Data_Type.BINARY:
            extension = 'bin'
        else:
            extension = 'json'
        return f'{self.data_folder()}/{key_data}.{extension}'

    def file_delete(self,
                    cache_id : Cache_Id              ,
                    data_type: Enum__Cache__Data_Type,
                    path     : Safe_Str__File__Path  ,
                    key_data : Safe_Str__File__Path  ) -> bool:

        data_key,data_file_id  = self.parse_key(key_data)

        response = self.client.file_delete(cache_id     = cache_id                   ,
                                           namespace    = self.namespace()           ,
                                           data_type    = data_type                  ,
                                           data_key     = data_key                   ,                     # Data path key
                                           data_file_id = data_file_id               )
        if response:
            if response.get('status') == 'success':
                return True
        return False

    def file_exist(self, path: Safe_Str__File__Path) -> bool:
        response = self.client.admin_storage__file_exist(path=path)
        if response:
            return response.get('exists')
        return False

    def file_folder(self) -> Safe_Str__File__Path:
        return f'{self.config.cache_namespace}/data/key-based/sessions/{self.session_name}/targets/{self.target_name}'

    # ═══════════════════════════════════════════════════════════════════════════
    # Key Parsing
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def parse_key(self                      ,                                                         # Parse key into parts
                  key : Safe_Str__File__Path) -> Tuple[Safe_Str__Data_Key, Safe_Str__Data_File_Id]:
        parts = key.rsplit('/', 1)
        if len(parts) == 2:
            return Safe_Str__Data_Key(parts[0]), Safe_Str__Data_File_Id(parts[1])
        return Safe_Str__Data_Key(''), Safe_Str__Data_File_Id(parts[0])

    # ═══════════════════════════════════════════════════════════════════════════
    # Misc helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def namespace(self) -> Safe_Str__Namespace:
        return self.config.cache_namespace

    # ═══════════════════════════════════════════════════════════════════════════
    # Abstract Method Implementations
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def admin_storage__file_exist(self, path: Safe_Str__File__Path) -> bool:
        return self.client.admin_storage__file_exist(path=path)

    @type_safe
    def admin_storage__files_all__path(self ,
                                       path: Safe_Str__File__Path
                ) -> Schema__Routes__Admin__Storage__Files_All__Response:
        return self.client.admin_storage__files_all__path(path=path)

    def file__contents__json(self, cache_id: Cache_Id) -> Optional[dict]:
        return self.client.file__contents__json(cache_id  = cache_id        ,
                                                namespace = self.namespace())

    def file__config(self, cache_id: Cache_Id) -> Optional[dict]:
        return self.client.file__config(cache_id  = cache_id        ,
                                        namespace = self.namespace())

    def file__hash(self, cache_hash: Safe_Str__Cache_Hash) -> Optional[dict]:
        return self.client.file_hash(cache_hash  = cache_hash     ,
                                     namespace   = self.namespace())

    def file__metadata(self, cache_id: Cache_Id) -> Optional[dict]:
        return self.client.file__metadata(cache_id  = cache_id        ,
                                          namespace = self.namespace())

    def file__refs(self, cache_id: Cache_Id):
        return self.client.file__refs(cache_id  = cache_id        ,
                                      namespace = self.namespace())

    @type_safe
    def save(self                           ,                                       # Save JSON data
             cache_id : Cache_Id            ,                                       # Cache_Id of base file
             key      : Safe_Str__File__Path,                                       # Data key path
             data     : dict                                                        # Data to store
        ) -> bool:

        data_key, data_file_id = self.parse_key(key)
        result                 = self.client.store_child_json(cache_id     = cache_id    ,
                                                              data_key     = data_key    ,
                                                              data_file_id = data_file_id,
                                                              data         = data        )
        return result is not None

    @type_safe
    def save_string(self                           ,                                # Save string content
                    cache_id : Cache_Id            ,                                # Cache_Id of base file (FIXED: was missing)
                    key      : Safe_Str__File__Path,                                # Data key path
                    content  : str                                                  # String content
                 ) -> bool:

        data_key, data_file_id = self.parse_key(key)
        result                 = self.client.store_child_string(cache_id     = cache_id    ,
                                                                data_key     = data_key    ,
                                                                data_file_id = data_file_id,
                                                                content      = content     )
        return result is not None

    @type_safe
    def load__json(self                           ,                                 # Load JSON data
                   cache_id : Cache_Id            ,
                   key      : Safe_Str__File__Path
              ) -> Optional[dict]:                                                  # Returns None if not found (FIXED: was dict)
        data_key, data_file_id = self.parse_key(key)
        return self.client.retrieve_child_json(cache_id     = cache_id    ,
                                               data_key     = data_key    ,
                                               data_file_id = data_file_id)

    @type_safe
    def load_string(self                           ,                                # Load string content
                    cache_id : Cache_Id            ,                                # Cache_Id of base file (FIXED: was missing)
                    key      : Safe_Str__File__Path                                 # Data key path
               ) -> Optional[str]:                                                  # Returns None if not found
        data_key, data_file_id = self.parse_key(key)
        response = self.client.retrieve_child_string(cache_id     = cache_id    ,
                                                     data_key     = data_key    ,
                                                     data_file_id = data_file_id)
        return response

    @type_safe
    def exists(self                             ,                                     # Check if key exists
               cache_id : Cache_Id              ,
               data_type: Enum__Cache__Data_Type,
               key      : Safe_Str__File__Path
           ) -> bool:
        # Use file_exist via calculated path
        path = self.data_file(data_type = data_type,
                              key_data  = key )
        return self.file_exist(path=path)


    @type_safe
    def delete(self                              ,                                  # Delete data by key
               cache_id  : Cache_Id              ,                                  # Cache_Id of base file
               key       : Safe_Str__File__Path  ,
               data_type : Enum__Cache__Data_Type
          ) -> bool:

        data_key, data_file_id = self.parse_key(key)
        return self.client.delete_child(cache_id     = cache_id    ,
                                        data_key     = data_key    ,
                                        data_file_id = data_file_id,
                                        data_type    = data_type   )

    @type_safe
    def delete__string(self                  ,                                      # Delete string by key
                       cache_id : Cache_Id   ,                                      # Cache_Id of base file
                       key      : str
                  ) -> bool:
        return self.delete(cache_id  = cache_id,
                           key       = key,
                           data_type = Enum__Cache__Data_Type.STRING)

    @type_safe
    def list_keys(self                  ,                                           # List child data files
                  prefix : str = ''     ) -> List[str]:                             # Requires refs endpoint
        return []                                                                   # TODO: implement via refs API


    #
    def namespace__all_files(self) -> List[Safe_Str__File__Path]:
        return self.client.admin_storage__files_all__path(path=self.namespace()).files

    def namespace__cache_hashes(self) -> List[Safe_Str__Namespace]:
        return self.client.namespace__cache_hashes(namespace=self.namespace())

    def namespace__cache_ids(self) -> List[Safe_Str__Namespace]:
        return self.client.namespace__cache_ids(namespace=self.namespace())


    def namespaces__list(self) -> List[Cache_Id]:
        return self.client.namespaces__list()