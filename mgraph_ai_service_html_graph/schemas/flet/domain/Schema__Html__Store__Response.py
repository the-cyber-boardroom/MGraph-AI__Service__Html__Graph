# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html__Store__Response - Response from domain-level store operations
# ═══════════════════════════════════════════════════════════════════════════════

from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__Cache_Hash import Safe_Str__Cache__File__Cache_Hash
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__Cache_Key  import Safe_Str__Cache__File__Cache_Key
from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                         import Safe_UInt
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                           import Cache_Id
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                     import Safe_Str__Url



class Schema__Html__Store__Response(Type_Safe):                                   # Response from store
    success        : bool                                                         # Whether store succeeded
    cache_id       : Cache_Id                                                     # Cache entity ID
    cache_key      : Safe_Str__Cache__File__Cache_Key                             # Cache key used
    cache_hash     : Safe_Str__Cache__File__Cache_Hash                            # Content hash
    char_count     : Safe_UInt                                                    # Character count of HTML
    final_url      : Safe_Str__Url                                                # Final URL after redirects
