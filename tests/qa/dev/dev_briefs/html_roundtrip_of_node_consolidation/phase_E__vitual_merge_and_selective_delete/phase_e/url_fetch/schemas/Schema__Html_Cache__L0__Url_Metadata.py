# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html_Cache__L0__Url_Metadata - L0 URL layer metadata
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now   import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url           import Safe_Str__Url
from phase_e.url_fetch.primitives.Safe_UInt__Http__Status_Code                     import Safe_UInt__Http__Status_Code
from phase_e.url_fetch.primitives.Safe_UInt__Milliseconds                          import Safe_UInt__Milliseconds
from phase_e.url_fetch.primitives.Safe_UInt__Bytes                                 import Safe_UInt__Bytes
from phase_e.url_fetch.primitives.Safe_Str__Content_Hash                           import Safe_Str__Content_Hash


class Schema__Html_Cache__L0__Url_Metadata(Type_Safe):              # PURE DATA - NO METHODS
    # URL Information
    url            : Safe_Str__Url                                  # Original URL
    normalized_url : Safe_Str__Url                                  # Normalized for deduplication
    final_url      : Safe_Str__Url                                  # URL after redirects
    
    # HTTP Response
    status_code    : Safe_UInt__Http__Status_Code                   # HTTP status code
    content_type   : str                                            # Content-Type header
    content_length : Safe_UInt__Bytes                               # Response size in bytes
    
    # Caching Headers
    etag           : str                                            # ETag header for conditional requests
    last_modified  : str                                            # Last-Modified header
    cache_control  : str                                            # Cache-Control header
    
    # Timing
    fetched_at     : Timestamp_Now                                  # When fetched
    fetch_duration : Safe_UInt__Milliseconds                        # Fetch duration in ms
    
    # Content Reference
    content_hash   : Safe_Str__Content_Hash                         # Links to L1 content
