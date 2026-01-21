# ═══════════════════════════════════════════════════════════════════════════════
# Html_Fetcher - HTTP client with retries, rate limiting, and error handling
# ═══════════════════════════════════════════════════════════════════════════════

import time
import requests
from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url           import Safe_Str__Url
from phase_e.url_fetch.schemas.Schema__Html_Fetcher__Config                        import Schema__Html_Fetcher__Config
from phase_e.url_fetch.schemas.Schema__Html_Fetcher__Response                      import Schema__Html_Fetcher__Response
from phase_e.url_fetch.primitives.Safe_UInt__Http__Status_Code                     import Safe_UInt__Http__Status_Code
from phase_e.url_fetch.primitives.Safe_UInt__Milliseconds                          import Safe_UInt__Milliseconds


class Html_Fetcher(Type_Safe):
    config            : Schema__Html_Fetcher__Config                # Fetcher configuration
    last_request_time : float = 0.0                                 # Timestamp of last request (for rate limiting)

    # ═══════════════════════════════════════════════════════════════════════════
    # Public Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def fetch(self, url: Safe_Str__Url, headers: dict = None) -> Schema__Html_Fetcher__Response:
        """Fetch URL with retries and rate limiting."""
        self._apply_rate_limit()
        
        start_time      = time.time()
        request_headers = self._build_headers(headers)
        
        for attempt in range(int(self.config.max_retries)):
            try:
                response = requests.get(
                    str(url),
                    headers         = request_headers,
                    timeout         = int(self.config.timeout_seconds),
                    allow_redirects = self.config.follow_redirects
                )
                
                duration_ms = Safe_UInt__Milliseconds(int((time.time() - start_time) * 1000))
                
                return Schema__Html_Fetcher__Response(
                    url         = url,
                    final_url   = Safe_Str__Url(response.url),
                    status_code = Safe_UInt__Http__Status_Code(response.status_code),
                    headers     = dict(response.headers),
                    html        = response.text if response.ok else '',
                    ok          = response.ok,
                    error       = '',
                    duration_ms = duration_ms
                )
                
            except requests.RequestException as e:
                if attempt < int(self.config.max_retries) - 1:
                    time.sleep(int(self.config.retry_delay_seconds))
                    continue
                
                duration_ms = Safe_UInt__Milliseconds(int((time.time() - start_time) * 1000))
                
                return Schema__Html_Fetcher__Response(
                    url         = url,
                    final_url   = url,
                    status_code = Safe_UInt__Http__Status_Code(0),
                    headers     = {},
                    html        = '',
                    ok          = False,
                    error       = str(e),
                    duration_ms = duration_ms
                )
        
        # Should not reach here, but just in case
        duration_ms = Safe_UInt__Milliseconds(int((time.time() - start_time) * 1000))
        
        return Schema__Html_Fetcher__Response(
            url         = url,
            final_url   = url,
            status_code = Safe_UInt__Http__Status_Code(0),
            headers     = {},
            html        = '',
            ok          = False,
            error       = 'Max retries exceeded',
            duration_ms = duration_ms
        )

    def fetch_conditional(self                           , 
                          url           : Safe_Str__Url  , 
                          etag          : str = ''       ,
                          last_modified : str = ''       ) -> Schema__Html_Fetcher__Response:
        """Fetch with conditional headers (If-None-Match, If-Modified-Since)."""
        headers = {}
        if etag:
            headers['If-None-Match'] = etag
        if last_modified:
            headers['If-Modified-Since'] = last_modified
        
        return self.fetch(url, headers=headers)

    # ═══════════════════════════════════════════════════════════════════════════
    # Private Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _apply_rate_limit(self):
        """Apply rate limiting between requests."""
        if int(self.config.min_request_interval_ms) > 0:
            elapsed_ms = (time.time() - self.last_request_time) * 1000
            if elapsed_ms < int(self.config.min_request_interval_ms):
                sleep_time = (int(self.config.min_request_interval_ms) - elapsed_ms) / 1000
                time.sleep(sleep_time)
        self.last_request_time = time.time()

    def _build_headers(self, custom_headers: dict = None) -> dict:
        """Build request headers with User-Agent."""
        headers = {'User-Agent': self.config.user_agent}
        if custom_headers:
            headers.update(custom_headers)
        return headers
