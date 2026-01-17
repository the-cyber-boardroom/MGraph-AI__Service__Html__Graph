# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html_Entry - Schema for HTML entries stored in cache
# Used by FLeT__Html__To__Cache for storing HTML with metadata
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                     import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Int                                      import Safe_Int
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                import Safe_Str__Html
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Cache_Hash import Safe_Str__Cache_Hash


class Schema__Html_Entry(Type_Safe):                                                # HTML entry for cache storage
    html       : Safe_Str__Html                                                     # HTML content
    cache_hash : Safe_Str__Cache_Hash                                               # Hash of HTML content
    char_count : Safe_Int                                                           # Character count