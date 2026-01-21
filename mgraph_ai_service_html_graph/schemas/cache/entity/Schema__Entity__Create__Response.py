# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Entity__Create__Response - Response from entity creation
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                           import Cache_Id
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__Cache_Hash import Safe_Str__Cache__File__Cache_Hash


class Schema__Entity__Create__Response(Type_Safe):                                  # Response from entity creation
    success    : bool                                                               # Whether creation succeeded
    cache_id   : Cache_Id                                                           # Created entity cache_id   (this will always be unique)
    cache_hash : Safe_Str__Cache__File__Cache_Hash                                  # Created entity cache hash (this will depend on how the cache_hash is calculated)
