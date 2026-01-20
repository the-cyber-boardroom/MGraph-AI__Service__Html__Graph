# ═══════════════════════════════════════════════════════════════════════════════
# Schema__FLeT__Html__To__Cache__Response - Response from Html-To-Cache execution
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                       import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                       import Safe_UInt
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                         import Cache_Id
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__Data_Key import Safe_Str__Cache__File__Data_Key
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__File_Id  import Safe_Str__Cache__File__File_Id


class Schema__FLeT__Html__To__Cache__Response(Type_Safe):                         # Response from Html-To-Cache
    success      : bool                                                           # Whether FLeT succeeded
    cache_id     : Cache_Id                                                       # Cache entity ID
    char_count   : Safe_UInt                                                      # Character count of stored HTML
    data_key     : Safe_Str__Cache__File__Data_Key                                # Data path key used
    data_file_id : Safe_Str__Cache__File__File_Id                                 # File identifier used
    flow_saved   : bool                                                           # Whether flow data was saved
