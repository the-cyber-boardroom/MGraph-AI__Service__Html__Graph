# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Entity__Create__Request - Request to create a cache entity
# ═══════════════════════════════════════════════════════════════════════════════

from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__Cache_Key import Safe_Str__Cache__File__Cache_Key
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__File_Id   import Safe_Str__Cache__File__File_Id
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe

DEFAULT__ENTITY__FILE_ID = 'root'

class Schema__Entity__Create__Request(Type_Safe):                                 # Request for entity creation
    cache_key : Safe_Str__Cache__File__Cache_Key                                  # Semantic path key
    file_id   : Safe_Str__Cache__File__File_Id = DEFAULT__ENTITY__FILE_ID         # File identifier (default: 'root')
