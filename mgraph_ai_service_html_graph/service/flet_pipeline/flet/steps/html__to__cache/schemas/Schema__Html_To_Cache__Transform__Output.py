from osbot_utils.type_safe.Type_Safe                                                     import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt import Safe_UInt
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                import Safe_Str__Html
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Cache_Hash import Safe_Str__Cache_Hash
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace   import Safe_Str__Namespace


class Schema__Html_To_Cache__Transform__Output(Type_Safe):                           # Output from transform phase
    html       : Safe_Str__Html                                                      # HTML content
    html_hash  : Safe_Str__Cache_Hash                                                # Hash of HTML
    namespace  : Safe_Str__Namespace                                                 # Namespace
    cache_key  : Safe_Str__File__Path                                                # Final cache key
    char_count : Safe_UInt                                                           # Character count
