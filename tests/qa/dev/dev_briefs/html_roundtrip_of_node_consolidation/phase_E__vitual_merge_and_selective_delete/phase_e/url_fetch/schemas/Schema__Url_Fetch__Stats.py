# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Url_Fetch__Stats - Statistics for URL fetching operations
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                               import Safe_UInt


class Schema__Url_Fetch__Stats(Type_Safe):                          # PURE DATA - NO METHODS
    # L0 (URL fetch) statistics
    l0_hits              : Safe_UInt                                # Cache hits at L0
    l0_misses            : Safe_UInt                                # Cache misses at L0 (network fetch)
    l0_conditional_hits  : Safe_UInt                                # 304 Not Modified responses
    
    # Network statistics
    network_requests     : Safe_UInt                                # Total network requests made
    network_failures     : Safe_UInt                                # Failed network requests
    network_retries      : Safe_UInt                                # Retry attempts
    
    # Timing totals
    total_fetch_time_ms  : Safe_UInt                                # Total time spent fetching
    total_bytes_fetched  : Safe_UInt                                # Total bytes downloaded
