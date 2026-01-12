# ═══════════════════════════════════════════════════════════════════════════════
# Perf__Storage__Base - Abstract base class for storage backends
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                                  import Optional, List

from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type import Enum__Cache__Data_Type
from mgraph_ai_service_cache_client.schemas.routes.admin.Schema__Routes__Admin__Storage__Files_All__Response import Schema__Routes__Admin__Storage__Files_All__Response
from osbot_utils.type_safe.Type_Safe                                                                         import Type_Safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Cache_Hash                     import Safe_Str__Cache_Hash
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                            import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                           import Cache_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace                       import Safe_Str__Namespace
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                               import type_safe
from phase_e.storage.safe_str.Safe_Str__Data_File_Id                                                         import Safe_Str__Data_File_Id
from phase_e.storage.safe_str.Safe_Str__Session_Name                                                         import Safe_Str__Session_Name
from phase_e.storage.safe_str.Safe_Str__Target_Name                                                          import Safe_Str__Target_Name


class Perf__Storage__Base(Type_Safe):                                           # Abstract storage backend
    session_name : Safe_Str__Session_Name                                       # Current session context
    target_name  : Safe_Str__Target_Name                                        # Current target context

    # ═══════════════════════════════════════════════════════════════════════════
    # Context Management
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def set_context(self                                    ,                   # Set session/target context
                    session_name : Safe_Str__Session_Name   ,                   # Session identifier
                    target_name  : Safe_Str__Target_Name    ) -> None:          # Target identifier
        self.session_name = session_name
        self.target_name  = target_name

    # ═══════════════════════════════════════════════════════════════════════════
    # Abstract Methods - Must be implemented by subclasses
    # ═══════════════════════════════════════════════════════════════════════════

    def admin_storage__files_all__path(self,
                                       path : Safe_Str__File__Path
                                  ) -> Schema__Routes__Admin__Storage__Files_All__Response:
        raise NotImplementedError

    def cache_id(self) -> Optional[Cache_Id]:
        raise NotImplementedError

    def cache_hash(self) -> Safe_Str__Cache_Hash:
        raise NotImplementedError

    def cache_key(self) -> str:
        raise NotImplementedError

    def create_file__if_not_available(self) -> Cache_Id:
        raise NotImplementedError

    def data_folder(self) -> Safe_Str__File__Path:
        raise NotImplementedError

    def data_file(self,
                  data_type: Enum__Cache__Data_Type,
                  key_data : Safe_Str__File__Path
             ) -> Safe_Str__File__Path:
        raise NotImplementedError

    def file_id(self):
        raise NotImplementedError

    def file_delete(self,
                    cache_id : Cache_Id              ,
                    data_type: Enum__Cache__Data_Type,
                    path     : Safe_Str__File__Path  ,
                    key_data : Safe_Str__File__Path  ) -> bool:
        raise NotImplementedError

    def file_exist(self, path: Safe_Str__File__Path) -> bool:
        raise NotImplementedError

    def file_folder(self) -> Safe_Str__File__Path:
        raise NotImplementedError

    def file__contents__json(self, cache_id: Cache_Id) -> Optional[dict]:
        raise NotImplementedError

    def file__config(self, cache_id: Cache_Id) -> Optional[dict]:
        raise NotImplementedError

    def file__hash(self, cache_hash: Safe_Str__Cache_Hash) -> Optional[dict]:
        raise NotImplementedError

    def file__metadata(self, cache_id: Cache_Id) -> Optional[dict]:
        raise NotImplementedError

    def file__refs(self, cache_id: Cache_Id):
        raise NotImplementedError

    def save(self                           ,                                   # Save JSON data
             cache_id : Cache_Id            ,
             key      : Safe_Str__File__Path,
             data     : dict
        ) -> bool:
        raise NotImplementedError

    def save_string(self                           ,                            # Save string content
                    cache_id : Cache_Id            ,
                    key      : Safe_Str__File__Path,
                    content  : str
                 ) -> bool:
        raise NotImplementedError

    def load__json(self                           ,                             # Load JSON data
                   cache_id : Cache_Id            ,
                   key      : Safe_Str__File__Path
              ) -> Optional[dict]:                                              # Returns None if not found
        raise NotImplementedError

    def load_string(self                           ,                            # Load string content
                    cache_id : Cache_Id            ,
                    key      : Safe_Str__File__Path
               ) -> Optional[str]:                                              # Returns None if not found
        raise NotImplementedError

    def exists(self                           ,                                 # Check if key exists
               cache_id : Cache_Id            ,
               data_type: Enum__Cache__Data_Type,
               key      : Safe_Str__File__Path
          ) -> bool:
        raise NotImplementedError

    def delete(self, key: str) -> bool:                                         # Delete data by key
        raise NotImplementedError

    def list_keys(self, prefix: str = '') -> List[str]:                         # List stored keys
        raise NotImplementedError

    def namespace__all_files(self) -> List[Safe_Str__File__Path]:
        raise NotImplementedError

    def namespace__cache_hashes(self) -> List[Safe_Str__Namespace]:
        raise NotImplementedError

    def namespace__cache_ids(self) -> List[Safe_Str__Namespace]:
        raise NotImplementedError

    def namespaces__list(self) -> List[Safe_Str__Namespace]:
        raise NotImplementedError