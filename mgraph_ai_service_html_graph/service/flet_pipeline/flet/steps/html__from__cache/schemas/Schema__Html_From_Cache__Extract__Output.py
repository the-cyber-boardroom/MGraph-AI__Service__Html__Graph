from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                  import Cache_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace              import Safe_Str__Namespace

class Schema__Html_From_Cache__Extract__Output(Type_Safe):                           # Output from extract phase
    namespace   : Safe_Str__Namespace  = ''                                          # Namespace
    cache_id    : Cache_Id             = None                                        # Cache ID
    found       : bool                 = False                                       # Entry found
    entry_data  : dict                 = None                                        # Raw entry data from cache
