from osbot_utils.type_safe.Type_Safe                            import Type_Safe
from typing                                                     import Optional

from osbot_utils.type_safe.primitives.core.Safe_Int import Safe_Int
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Cache_Hash import Safe_Str__Cache_Hash
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now import Timestamp_Now


class Schema__Html_Cache__Metadata__L1(Type_Safe):              # Metadata for L1 (raw HTML) layer
    source       : str   = ''                                   # Source identifier (URL, file path, etc.)
    cached_at    : Timestamp_Now                                  # Timestamp when cached
    content_hash : str   = ''                                   # SHA256 hash of content (truncated)
    size_bytes   : int   = 0                                    # Size of HTML in bytes


# class Schema__Html_Cache__Metadata__L2(Type_Safe):              # Metadata for L2 (parsed dict) layer
#     content_hash : Safe_Str__Cache_Hash                         # SHA256 hash of serialized dict
#     #node_count   : Safe_Int                                     # Number of nodes in dict
#     cached_at    : Timestamp_Now                                # Timestamp when cached


class Schema__Html_Cache__Metadata__L3(Type_Safe):              # Metadata for L3 (MGraph document) layer
    content_hash : str   = ''                                   # SHA256 hash of serialized document
    node_count   : int   = 0                                    # Total nodes in graph
    edge_count   : int   = 0                                    # Total edges in graph
    cached_at    : Timestamp_Now                                  # Timestamp when cached


class Schema__Html_Cache__Config(Type_Safe):                    # Configuration for cache manager
    session_name         : str  = 'phase-e-4'                   # Default session name
    enable_content_hash  : bool = True                          # Enable content-addressable lookups
    auto_build_on_miss   : bool = True                          # Auto-build lower layers on cache miss


class Schema__Html_Cache__Stats(Type_Safe):                     # Statistics for cache operations
    l1_hits   : int = 0                                         # L1 cache hits
    l1_misses : int = 0                                         # L1 cache misses
    l2_hits   : int = 0                                         # L2 cache hits
    l2_misses : int = 0                                         # L2 cache misses
    l2_builds : int = 0                                         # L2 built from L1
    l3_hits   : int = 0                                         # L3 cache hits
    l3_misses : int = 0                                         # L3 cache misses
    l3_builds : int = 0                                         # L3 built from L2

    def reset(self):                                            # Reset all stats
        self.l1_hits   = 0
        self.l1_misses = 0
        self.l2_hits   = 0
        self.l2_misses = 0
        self.l2_builds = 0
        self.l3_hits   = 0
        self.l3_misses = 0
        self.l3_builds = 0
