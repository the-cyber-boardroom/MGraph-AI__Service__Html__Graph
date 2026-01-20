# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Entity__Lookup__Request - Request to lookup a cache entity
# ═══════════════════════════════════════════════════════════════════════════════

from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__Cache_Hash import Safe_Str__Cache__File__Cache_Hash
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__Cache_Key  import Safe_Str__Cache__File__Cache_Key
from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe


class Schema__Entity__Lookup__Request(Type_Safe):                                 # Request for entity lookup
    cache_key  : Safe_Str__Cache__File__Cache_Key                                 # Lookup by semantic key
    cache_hash : Safe_Str__Cache__File__Cache_Hash                                # Lookup by content hash
