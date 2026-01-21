# ═══════════════════════════════════════════════════════════════════════════════
# Schema__LETS__Step__List__Response - Response listing all steps
# ═══════════════════════════════════════════════════════════════════════════════
from typing import List

from osbot_utils.type_safe.Type_Safe                                                           import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Int                                            import Safe_Int
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List                          import Type_Safe__List
from mgraph_ai_service_html_graph.schemas.routes.lets.Schema__LETS__Step__Info                 import Schema__LETS__Step__Info


class List__LETS__Step__Info(Type_Safe__List):                                   # List of step info
    expected_type = Schema__LETS__Step__Info


class Schema__LETS__Step__List__Response(Type_Safe):                             # List response
    #steps : List__LETS__Step__Info                                               # All available steps
    steps  : List[Schema__LETS__Step__Info]
    count : Safe_Int = 0                                                         # Number of steps
