# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html__Store__Key__Request - Request to store HTML with explicit cache_key
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                      import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html import Safe_Str__Html


class Schema__Html__Store__Key__Request(Type_Safe):                               # Request to store with key
    html : Safe_Str__Html                                                         # HTML content to store
