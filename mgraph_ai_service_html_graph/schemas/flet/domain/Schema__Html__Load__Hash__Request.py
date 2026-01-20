# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html__Load__Hash__Request - Request to load HTML by cache_hash
# ═══════════════════════════════════════════════════════════════════════════════

from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__Cache_Hash import Safe_Str__Cache__File__Cache_Hash
from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe


class Schema__Html__Load__Hash__Request(Type_Safe):                               # Request to load by hash
    cache_hash : Safe_Str__Cache__File__Cache_Hash                                # Content hash to lookup
