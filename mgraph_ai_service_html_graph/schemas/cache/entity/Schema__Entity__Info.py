from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                        import Safe_UInt
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Cache_Hash    import Safe_Str__Cache_Hash
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                          import Cache_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now            import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id             import Safe_Str__Id
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__Cache_Key import Safe_Str__Cache__File__Cache_Key
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__File_Id   import Safe_Str__Cache__File__File_Id
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__Namespace       import Safe_Str__Cache__Namespace
from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Store__Strategy        import Enum__Cache__Store__Strategy
from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type              import Enum__Cache__Data_Type

class Schema__Entity__Info(Type_Safe):
    cache_id         : Cache_Id                         = None
    cache_key        : Safe_Str__Cache__File__Cache_Key = None
    cache_hash       : Safe_Str__Cache_Hash             = None
    file_id          : Safe_Str__Cache__File__File_Id   = None
    namespace        : Safe_Str__Cache__Namespace       = None
    strategy         : Enum__Cache__Store__Strategy     = None
    stored_at        : Timestamp_Now                    = None
    file_type        : Enum__Cache__Data_Type           = None
    content_encoding : Safe_Str__Id                     = None
    content_size     : Safe_UInt                        = None
    data_files       : list[dict]                       = None    # Optional - only if include_data_files=true