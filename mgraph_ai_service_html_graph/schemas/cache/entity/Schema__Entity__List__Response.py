from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__Namespace       import Safe_Str__Cache__Namespace
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Info                 import Schema__Entity__Info

class Schema__Entity__List__Response(Type_Safe):
    success   : bool                       = True               # todo: review the use of this success var (since at the moment it is not adding a lot of value)
    namespace : Safe_Str__Cache__Namespace
    count     : int
    entities  : list[Schema__Entity__Info]