# ═══════════════════════════════════════════════════════════════════════════════
# Schema__LETS__Step__Status__Response - Response for step status check
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                           import Safe_Float
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id


class Schema__LETS__Step__Status__Response(Type_Safe):                           # Status response
    step_type    : Safe_Str__Id = None                                           # Step type checked
    cache_id     : Safe_Str__Id = None                                           # Cache entry ID
    namespace    : Safe_Str__Id = None                                           # Cache namespace
    completed    : bool         = False                                          # Whether step completed
    duration_ms  : Safe_Float   = None                                           # Execution time if completed
    completed_at : str          = None                                           # Timestamp if completed
