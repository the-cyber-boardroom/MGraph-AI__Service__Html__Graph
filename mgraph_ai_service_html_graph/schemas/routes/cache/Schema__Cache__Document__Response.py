# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Cache__Document__Response - Response with document info
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id


class Schema__Cache__Document__Response(Type_Safe):                              # Document info response
    cache_id   : Safe_Str__Id = None                                             # Cache entry ID
    namespace  : Safe_Str__Id = None                                             # Cache namespace
    cache_key  : str          = None                                             # Semantic path
    created_at : str          = None                                             # Creation timestamp
    updated_at : str          = None                                             # Last update timestamp
    exists     : bool         = True                                             # Whether document exists
