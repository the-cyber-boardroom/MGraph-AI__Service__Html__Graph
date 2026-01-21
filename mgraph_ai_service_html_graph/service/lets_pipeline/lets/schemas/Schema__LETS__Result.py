# ═══════════════════════════════════════════════════════════════════════════════
# Schema__LETS__Result - Result of a LETS execution
# Returned by executor to indicate success/failure and stats
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_utils.type_safe.Type_Safe                                                               import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                               import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                       import Safe_Str__Text
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.safe_str.Safe_Str__LETS__Name import Safe_Str__LETS__Name



class Schema__LETS__Result(Type_Safe):                                           # Result of LETS execution
    lets_name    : Safe_Str__LETS__Name                                          # Which LETS was run
    success      : bool                                                          # Did it complete
    from_cache   : bool                                                          # Was result from cache
    duration_ms  : Safe_UInt               = 0                                   # Execution time
    error        : Safe_Str__Text          = None                                # Error message if failed
