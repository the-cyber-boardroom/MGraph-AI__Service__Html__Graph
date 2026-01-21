# ═══════════════════════════════════════════════════════════════════════════════
# Schema__LETS__Step__Info - Information about a LETS step
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text    import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id


class Schema__LETS__Step__Info(Type_Safe):                                       # Step information
    step_type   : Safe_Str__Id   = None                                          # Enum value name
    name        : Safe_Str__Text = None                                          # Human-readable name
    description : Safe_Str__Text = None                                          # What this step does
