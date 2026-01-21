# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Profile__Execute__Response - Response from profile execution
# ═══════════════════════════════════════════════════════════════════════════════
from typing import List

from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                                           import Safe_Float
from osbot_utils.type_safe.primitives.core.Safe_Int                                             import Safe_Int
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id                 import Safe_Str__Id
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List                           import Type_Safe__List
from mgraph_ai_service_html_graph.schemas.routes.lets.Schema__LETS__Step__Execute__Response     import Schema__LETS__Step__Execute__Response


class List__Step__Execute__Response(Type_Safe__List):                            # List of step results
    expected_type = Schema__LETS__Step__Execute__Response


class Schema__Profile__Execute__Response(Type_Safe):                             # Execution response
    profile_id        : Safe_Str__Id                = None                       # Profile that was executed
    success           : bool                        = False                      # Whether all steps succeeded
    total_duration_ms : Safe_Float                  = 0                          # Total execution time
    steps_completed   : Safe_Int                    = 0                          # Number of steps completed
    steps_total       : Safe_Int                    = 0                          # Total steps in profile
    #step_results      : List__Step__Execute__Response                            # Individual step results
    step_results      : List[Schema__LETS__Step__Execute__Response]
    final_output      : dict                        = None                       # Output from last step
    error             : str                         = None                       # Error message if failed
