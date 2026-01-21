# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html__Load__Url__Request - Request to load HTML by URL (used as cache_key)
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                     import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url import Safe_Str__Url


class Schema__Html__Load__Url__Request(Type_Safe):                                # Request to load by URL
    url : Safe_Str__Url                                                           # URL to lookup (used as key)
