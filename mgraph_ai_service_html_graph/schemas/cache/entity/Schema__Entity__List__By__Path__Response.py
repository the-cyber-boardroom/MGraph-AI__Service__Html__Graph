from typing import List

from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__Namespace   import Safe_Str__Cache__Namespace
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                    import Safe_UInt
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path       import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id         import Safe_Str__Id


class Schema__Entity__List__By__Path__Response(Type_Safe):
    success     : bool
    namespace   : Safe_Str__Cache__Namespace
    path_prefix : Safe_Str__File__Path
    count       : Safe_UInt
    entities    : List[Safe_Str__Id]
