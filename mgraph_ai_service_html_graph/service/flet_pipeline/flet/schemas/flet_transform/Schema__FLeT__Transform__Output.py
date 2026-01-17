from typing                                                                       import Dict, Any
from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html         import Safe_Str__Html
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Cache_Hash import Safe_Str__Cache_Hash


class Schema__FLeT__Transform__Output(Type_Safe):                                    # Base output from Transform phase
    html       : Safe_Str__Html      = ''                                            # Transformed HTML
    html_hash  : Safe_Str__Cache_Hash = ''                                           # Hash of HTML content
    stats      : Dict[str, Any]      = None                                          # Optional stats/metadata
