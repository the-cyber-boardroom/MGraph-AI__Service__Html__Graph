# ═══════════════════════════════════════════════════════════════════════════════
# Schema__LETS__Step__Execute__Response - Response from step execution
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                           import Safe_Float
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id


class Schema__LETS__Step__Execute__Response(Type_Safe):                          # Execution response
    step_type   : Safe_Str__Id = None                                            # Step that was executed
    success     : bool         = False                                           # Whether execution succeeded
    from_cache  : bool         = False                                           # Whether result was cached
    duration_ms : Safe_Float   = 0                                               # Execution time
    output      : dict         = None                                            # Step output data
    error       : str          = None                                            # Error message if failed
