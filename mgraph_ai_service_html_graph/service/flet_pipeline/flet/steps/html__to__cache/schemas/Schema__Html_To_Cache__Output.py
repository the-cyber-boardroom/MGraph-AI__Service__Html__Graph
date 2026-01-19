# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html_To_Cache__Output - Output from HTML to cache FLeT
# ═══════════════════════════════════════════════════════════════════════════════
from mgraph_ai_service_cache_client.schemas.cache.data.Schema__Cache__Data__Store__Response import Schema__Cache__Data__Store__Response

from osbot_utils.type_safe.Type_Safe                 import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt import Safe_UInt


class Schema__Html_To_Cache__Output(Type_Safe):                                           # Output from HTML to cache
    success        : bool                                                                   # Whether save succeeded
    data_key       : str                                                                    # Where it was saved
    data_file_id   : str                                                                    # File identifier used
    char_count     : Safe_UInt                                                              # Content length
    store_response : Schema__Cache__Data__Store__Response = None
