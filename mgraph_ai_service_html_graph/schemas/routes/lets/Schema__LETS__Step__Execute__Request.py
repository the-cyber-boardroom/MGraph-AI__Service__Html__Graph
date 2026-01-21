# ═══════════════════════════════════════════════════════════════════════════════
# Schema__LETS__Step__Execute__Request - Request for step execution
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html       import Safe_Str__Html


class Schema__LETS__Step__Execute__Request(Type_Safe):                           # Stateless execution request
    input_data : dict = None                                                     # Input for the step


class Schema__LETS__Step__Execute__Cached__Request(Type_Safe):                   # Cached execution request
    force_rerun : bool = False                                                   # Re-execute even if completed
    html        : Safe_Str__Html = None                                          # Optional HTML for first step
