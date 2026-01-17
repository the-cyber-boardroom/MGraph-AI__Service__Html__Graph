from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                  import Cache_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace              import Safe_Str__Namespace

# todo: convert lookup_type to Safe_* primitive
class Schema__Html_From_Cache__Load__Output(Type_Safe):                              # Output from load phase
    namespace   : Safe_Str__Namespace  = ''                                          # Namespace
    cache_id    : Cache_Id             = None                                        # Resolved cache ID
    lookup_type : str                  = ''                                          # How we looked it up
    found       : bool                 = False                                       # Whether entry exists
