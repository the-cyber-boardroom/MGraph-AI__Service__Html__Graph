# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Url__Cache_Key__Config - Configuration for URL to cache_key conversion
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                 import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt import Safe_UInt


# todo find type safe primitives classes to use below (instead of list)
class Schema__Url__Cache_Key__Config(Type_Safe):
    include_query_params : bool      = False                                         # Include query params in cache_key
    sort_query_params    : bool      = True                                          # Sort params for consistent keys
    query_params_as_hash : bool      = True                                          # Hash query params (vs inline them)
    hash_length          : Safe_UInt = 12                                            # Length of query params hash
    include_params       : list      = None                                          # Only include these params (None = all)
    exclude_params       : list      = None                                          # Exclude these params (e.g. ['utm_source'])