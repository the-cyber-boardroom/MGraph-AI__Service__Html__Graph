# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html_Cache__Entry - Schema for creating cache entries
# Used when creating new entries with the cache service
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from mgraph_ai_service_html_graph.service.cache_storage.safe_str.Safe_Str__Cache_Key     import Safe_Str__Cache_Key


class Schema__Html_Cache__Entry(Type_Safe):                                      # Entry for creation
    cache_key : Safe_Str__Cache_Key                                              # Used for hash lookup
    data      : dict                                                             # used to store unstuctured data
