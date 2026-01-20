# ═══════════════════════════════════════════════════════════════════════════════
# Schema__FLeT__Html__From__Cache__Response - Response from Html-From-Cache execution
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                      import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                      import Safe_UInt
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id        import Cache_Id
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html import Safe_Str__Html


class Schema__FLeT__Html__From__Cache__Response(Type_Safe):                       # Response from Html-From-Cache
    success    : bool                                                             # Whether FLeT succeeded
    cache_id   : Cache_Id                                                         # Cache entity ID
    html       : Safe_Str__Html                                                   # Retrieved HTML content
    found      : bool                                                             # Whether HTML was found in cache
    char_count : Safe_UInt                                                        # Character count of HTML
    flow_saved : bool                                                             # Whether flow data was saved
