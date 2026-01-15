# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Cache__Document__Layers__Response - Response listing layers
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id


class Schema__Cache__Document__Layers__Response(Type_Safe):                      # Layers response
    cache_id  : Safe_Str__Id = None                                              # Cache entry ID
    namespace : Safe_Str__Id = None                                              # Cache namespace
    layers    : list         = None                                              # Layer names
