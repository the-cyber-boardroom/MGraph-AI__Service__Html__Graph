# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Profile__Info - Information about a profile
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text    import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id


class Schema__Profile__Info(Type_Safe):                                          # Profile information
    profile_id  : Safe_Str__Id   = None                                          # Unique identifier
    name        : Safe_Str__Text = None                                          # Human readable name
    description : Safe_Str__Text = None                                          # What this profile does
    steps       : list           = None                                          # Ordered list of step types
