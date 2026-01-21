# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Profile__List__Response - Response listing all profiles
# ═══════════════════════════════════════════════════════════════════════════════
from typing import List

from osbot_utils.type_safe.Type_Safe                                                           import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Int                                            import Safe_Int
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List                          import Type_Safe__List
from mgraph_ai_service_html_graph.schemas.routes.profiles.Schema__Profile__Info                import Schema__Profile__Info


class List__Profile__Info(Type_Safe__List):                                      # List of profile info
    expected_type = Schema__Profile__Info


class Schema__Profile__List__Response(Type_Safe):                                # List response
    #profiles : List__Profile__Info                                               # All available profiles
    profiles : List[Schema__Profile__Info]
    count    : Safe_Int = 0                                                      # Number of profiles
