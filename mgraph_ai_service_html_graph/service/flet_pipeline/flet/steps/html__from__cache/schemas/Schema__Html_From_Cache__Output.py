# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html_From_Cache__Output - Output schema for HTML from cache FLeT
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                      import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html import Safe_Str__Html


class Schema__Html_From_Cache__Output(Type_Safe):                                         # Output from loading HTML from cache
    success : bool          = False                                                       # Whether operation succeeded
    html    : Safe_Str__Html                                                              # Retrieved HTML content
    found   : bool          = False                                                       # Whether data was found