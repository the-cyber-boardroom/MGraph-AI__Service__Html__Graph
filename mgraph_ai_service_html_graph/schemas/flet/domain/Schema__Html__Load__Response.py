# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html__Load__Response - Response from domain-level load operations
# ═══════════════════════════════════════════════════════════════════════════════

from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__Cache_Key import Safe_Str__Cache__File__Cache_Key
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                        import Safe_UInt
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                          import Cache_Id
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                   import Safe_Str__Html


class Schema__Html__Load__Response(Type_Safe):                                    # Response from load
    success    : bool                                                             # Whether load succeeded
    cache_id   : Cache_Id                                                         # Cache entity ID
    cache_key  : Safe_Str__Cache__File__Cache_Key                                 # Cache key
    html       : Safe_Str__Html                                                   # Retrieved HTML content
    found      : bool                                                             # Whether HTML was found
    char_count : Safe_UInt                                                        # Character count of HTML
