# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html_Fetcher__Response - Response from HTML fetcher
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text       import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url           import Safe_Str__Url

from phase_e.url_fetch.primitives.Safe_UInt__Http__Status_Code                     import Safe_UInt__Http__Status_Code
from phase_e.url_fetch.primitives.Safe_UInt__Milliseconds                          import Safe_UInt__Milliseconds


class Schema__Html_Fetcher__Response(Type_Safe):                    # PURE DATA - NO METHODS
    url            : Safe_Str__Url                                  # Original URL
    final_url      : Safe_Str__Url                                  # URL after redirects
    status_code    : Safe_UInt__Http__Status_Code                   # HTTP status code (100-599)
    headers        : dict                                           # Response headers
    html           : str                                            # Response body (HTML content)
    ok             : bool                                           # True if 200 <= status < 300
    error          : Safe_Str__Text                                 # Error message if failed
    duration_ms    : Safe_UInt__Milliseconds                        # Request duration in ms
