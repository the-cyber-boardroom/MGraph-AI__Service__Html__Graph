# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html__Store__Url__Request - Request to fetch and store HTML from URL
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                     import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                     import Safe_UInt
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url import Safe_Str__Url


DEFAULT__URL_FETCH__TIMEOUT = 30


class Schema__Html__Store__Url__Request(Type_Safe):                               # Request to store from URL
    url     : Safe_Str__Url                                                       # URL to fetch HTML from
    timeout : Safe_UInt = DEFAULT__URL_FETCH__TIMEOUT                             # Request timeout in seconds
