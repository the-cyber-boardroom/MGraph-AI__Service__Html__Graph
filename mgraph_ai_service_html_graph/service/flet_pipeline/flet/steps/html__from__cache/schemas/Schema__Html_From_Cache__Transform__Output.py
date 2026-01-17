from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                import Safe_UInt
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                           import Safe_Str__Html
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Cache_Hash            import Safe_Str__Cache_Hash

class Schema__Html_From_Cache__Transform__Output(Type_Safe):                         # Output from transform phase
    html       : Safe_Str__Html                                                      # Retrieved HTML
    html_hash  : Safe_Str__Cache_Hash                                                # Hash of HTML
    found      : bool                                                                # Whether found
    char_count : Safe_UInt                                                            # Character count
