# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Entity__Lookup__Response - Response from entity lookup
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                               import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id import Cache_Id


class Schema__Entity__Lookup__Response(Type_Safe):                                # Response from entity lookup
    success  : bool                                                               # Whether lookup succeeded
    cache_id : Cache_Id                                                           # Found entity cache_id
    found    : bool                                                               # Whether entity was found
