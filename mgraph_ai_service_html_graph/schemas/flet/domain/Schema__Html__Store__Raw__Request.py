# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html__Store__Raw__Request - Request to store raw HTML (auto-generates key)
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                      import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html import Safe_Str__Html


class Schema__Html__Store__Raw__Request(Type_Safe):                               # Request to store raw HTML
    html : Safe_Str__Html                                                         # HTML content to store
