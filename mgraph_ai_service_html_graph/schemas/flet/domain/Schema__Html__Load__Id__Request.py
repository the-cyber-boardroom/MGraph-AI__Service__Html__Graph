# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html__Load__Id__Request - Request to load HTML by cache_id
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                               import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id import Cache_Id


class Schema__Html__Load__Id__Request(Type_Safe):                                 # Request to load by ID
    cache_id : Cache_Id                                                           # Cache entity ID to load from
