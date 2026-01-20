from osbot_utils.type_safe.Type_Safe                                     import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url import Safe_Str__Url


class Schema__Route__Cache_Status__Response(Type_Safe):
    cache_enabled : bool
    health_check  : bool
    target_server : Safe_Str__Url