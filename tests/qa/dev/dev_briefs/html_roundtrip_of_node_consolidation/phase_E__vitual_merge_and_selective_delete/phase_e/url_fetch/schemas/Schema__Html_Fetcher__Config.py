# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html_Fetcher__Config - Configuration for HTML fetcher
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                               import Safe_UInt
from phase_e.url_fetch.primitives.Safe_UInt__Seconds                               import Safe_UInt__Seconds
from phase_e.url_fetch.primitives.Safe_UInt__Milliseconds                          import Safe_UInt__Milliseconds


class Schema__Html_Fetcher__Config(Type_Safe):                      # PURE DATA - NO METHODS
    timeout_seconds         : Safe_UInt__Seconds      = 30          # HTTP request timeout
    max_retries             : Safe_UInt               = 3           # Number of retry attempts
    retry_delay_seconds     : Safe_UInt__Seconds      = 1           # Delay between retries
    min_request_interval_ms : Safe_UInt__Milliseconds = 100         # Rate limiting (min ms between requests)
    user_agent              : str = 'MGraph-AI Html_Fetcher/1.0'    # User-Agent header
    follow_redirects        : bool = True                           # Follow HTTP redirects
    max_redirects           : Safe_UInt = 5                         # Maximum redirect hops
