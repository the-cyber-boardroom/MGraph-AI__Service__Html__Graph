from typing                                                                              import Dict, Any
from osbot_utils.type_safe.Type_Safe                                                     import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                import Safe_Str__Html
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Cache_Hash import Safe_Str__Cache_Hash


class Schema__FLeT__Save__Input(Type_Safe):                                          # Base input for Save phase
    html       : Safe_Str__Html       = ''                                           # HTML to save
    html_hash  : Safe_Str__Cache_Hash = ''                                           # Hash of HTML
    stats      : Dict[str, Any]       = None                                         # Stats from transform
