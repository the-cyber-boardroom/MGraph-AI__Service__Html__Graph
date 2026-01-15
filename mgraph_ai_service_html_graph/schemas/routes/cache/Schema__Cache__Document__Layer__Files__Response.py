# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Cache__Document__Layer__Files__Response - Response listing files in layer
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id


class Schema__Cache__Document__Layer__Files__Response(Type_Safe):                # Layer files response
    cache_id   : Safe_Str__Id = None                                             # Cache entry ID
    namespace  : Safe_Str__Id = None                                             # Cache namespace
    layer_name : str          = None                                             # Layer name
    files      : list         = None                                             # File info list
