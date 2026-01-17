from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path       import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html               import Safe_Str__Html
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace  import Safe_Str__Namespace


class Schema__Html_To_Cache__Extract__Output(Type_Safe):                             # Output from extract phase
    html      : Safe_Str__Html                                                       # HTML content
    namespace : Safe_Str__Namespace                                                  # Namespace
    cache_key : Safe_Str__File__Path                                                 # Cache key
