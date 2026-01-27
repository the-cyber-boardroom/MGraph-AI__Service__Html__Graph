# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html_Graph__Client__Requests__Result
# Unified result schema for Html Graph client HTTP requests
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                       import Dict
from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                              import Safe_UInt
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path


class Schema__Html_Graph__Client__Requests__Result(Type_Safe):                  # Result from HTTP request
    status_code : Safe_UInt                                                     # HTTP status code
    json        : dict                  = None                                  # Parsed JSON response
    text        : str                   = None                                  # Raw text response
    content     : bytes                 = None                                  # Raw bytes content
    headers     : Dict[str, str]        = None                                  # Response headers
    path        : Safe_Str__File__Path                                          # Request path
