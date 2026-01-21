# ═══════════════════════════════════════════════════════════════════════════════
# Html_Cache__Layer__Url - L0: URL fetching and caching layer
# ═══════════════════════════════════════════════════════════════════════════════

import hashlib
from urllib.parse                                                                  import urlparse, urlunparse

from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type import Enum__Cache__Data_Type

from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html import Safe_Str__Html
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url           import Safe_Str__Url
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now   import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                 import Cache_Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe import type_safe
from phase_e.url_fetch.Html_Fetcher                                                import Html_Fetcher
from phase_e.url_fetch.primitives.Safe_UInt__Seconds import Safe_UInt__Seconds
from phase_e.url_fetch.schemas.Schema__Html_Fetcher__Response                      import Schema__Html_Fetcher__Response
from phase_e.url_fetch.schemas.Schema__Html_Cache__L0__Url_Metadata                import Schema__Html_Cache__L0__Url_Metadata
from phase_e.url_fetch.schemas.Schema__Url_Fetch__Stats                            import Schema__Url_Fetch__Stats
from phase_e.url_fetch.primitives.Safe_UInt__Http__Status_Code                     import Safe_UInt__Http__Status_Code
from phase_e.url_fetch.primitives.Safe_UInt__Milliseconds                          import Safe_UInt__Milliseconds
from phase_e.url_fetch.primitives.Safe_UInt__Bytes                                 import Safe_UInt__Bytes
from phase_e.url_fetch.primitives.Safe_Str__Content_Hash                           import Safe_Str__Content_Hash
from phase_e.storage.base.Perf__Storage__Base                                      import Perf__Storage__Base


class Html_Cache__Layer__Url(Type_Safe):                            # L0: URL layer
    storage    : Perf__Storage__Base                                # Storage backend
    stats      : Schema__Url_Fetch__Stats                           # Hit/miss tracking
    fetcher    : Html_Fetcher                                       # HTTP client
    layer_name : str = 'L0'                                         # Layer identifier

    # ═══════════════════════════════════════════════════════════════════════════
    # Cache Key Generation
    # ═══════════════════════════════════════════════════════════════════════════

    def key_metadata(self) -> str:                                  # Key for metadata file
        return f"{self.layer_name}/url-metadata.json"

    def key_html(self) -> str:                                      # Key for HTML content reference
        return f"{self.layer_name}/html-ref.json"

    # ═══════════════════════════════════════════════════════════════════════════
    # Public Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def fetch_and_cache(self                              , 
                        cache_id      : Cache_Id          ,
                        url           : Safe_Str__Url     , 
                        force_refresh : bool = False      ) -> str:
        """Fetch URL and cache response, or return cached HTML."""
        
        # Check if we have cached response
        if not force_refresh:
            metadata = self.load_metadata(cache_id=cache_id)
            if metadata:
                self.stats.l0_hits += 1
                # Return cached content hash (caller can use this to get HTML from L1)
                return metadata.get('content_hash', '')
        
        # Fetch from network
        self.stats.l0_misses += 1
        self.stats.network_requests += 1
        
        response = self.fetcher.fetch(url)
        
        if response.ok:
            content_hash = self._cache_response(cache_id, url, response)
            self.stats.total_fetch_time_ms += int(response.duration_ms)
            self.stats.total_bytes_fetched += len(response.html.encode('utf-8'))
            return content_hash
        else:
            self.stats.network_failures += 1
            return ''

    def conditional_fetch(self                     ,
                          cache_id : Cache_Id      ,
                          url      : Safe_Str__Url ) -> str:
        """Fetch with If-None-Match / If-Modified-Since."""
        metadata = self.load_metadata(cache_id=cache_id)
        if not metadata:
            return self.fetch_and_cache(cache_id, url)
        
        # Make conditional request
        self.stats.network_requests += 1
        response = self.fetcher.fetch_conditional(
            url           = url,
            etag          = metadata.get('etag', ''),
            last_modified = metadata.get('last_modified', '')
        )
        
        if response.status_code == 304:                             # Not Modified
            self.stats.l0_conditional_hits += 1
            self._update_fetch_time(cache_id, metadata)
            return metadata.get('content_hash', '')
        
        if response.ok:
            self.stats.l0_misses += 1
            content_hash = self._cache_response(cache_id, url, response)
            self.stats.total_fetch_time_ms += int(response.duration_ms)
            self.stats.total_bytes_fetched += len(response.html.encode('utf-8'))
            return content_hash
        
        self.stats.network_failures += 1
        return ''

    def delete_html(self, cache_id: Cache_Id):
        return self.storage.delete(cache_id  = cache_id,
                                   data_type = Enum__Cache__Data_Type.JSON,         # todo: double check why this is not Enum__Cache__Data_Type.STRING
                                   key       = self.key_html())
    def delete_metadata(self, cache_id: Cache_Id):
        return self.storage.delete(cache_id  = cache_id,
                                   data_type = Enum__Cache__Data_Type.JSON,         # todo: double check why this is not Enum__Cache__Data_Type.STRING
                                   key       = self.key_metadata())


    @type_safe
    def get_html(self                         ,                     # Get HTML content for URL (fetch if needed).
                 cache_id : Cache_Id          ,
                 url      : Safe_Str__Url     ,
                 force_refresh : bool = False
            ) -> Safe_Str__Html:

        if force_refresh:                                           # Force refresh - always fetch from network
            self.stats.l0_misses += 1
            self.stats.network_requests += 1
            response = self.fetcher.fetch(url)
        else:
            metadata = self.load_metadata(cache_id=cache_id)        # Try cache first
            if metadata:
                self.stats.l0_hits += 1
                return self._load_html(cache_id)

            self.stats.l0_misses += 1                               # Cache miss - fetch from network
            self.stats.network_requests += 1
            response = self.fetcher.fetch(url)

        if response.ok:
            self._cache_response(cache_id, url, response)
            self._save_html(cache_id, response.html)
            return response.html

        self.stats.network_failures += 1
        return ''

    @type_safe
    def load_metadata(self,                                             # Load URL metadata from cache.
                      cache_id: Cache_Id
                 ) -> Schema__Html_Cache__L0__Url_Metadata:
        metadata_json = self.storage.load__json(cache_id=cache_id, key=self.key_metadata())
        if metadata_json:
            metadata      = Schema__Html_Cache__L0__Url_Metadata.from_json(metadata_json)
            return metadata
        return None

    def exists(self, cache_id: Cache_Id) -> bool:
        """Check if URL metadata exists in cache."""
        return self.load_metadata(cache_id=cache_id) is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # Private Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _cache_response(self                               , 
                        cache_id : Cache_Id                ,
                        url      : Safe_Str__Url           , 
                        response : Schema__Html_Fetcher__Response) -> str:      # Save URL metadata and return content hash.
        content_hash = self._content_hash(response.html)
        
        metadata = Schema__Html_Cache__L0__Url_Metadata(url            = url,
                                                        normalized_url = Safe_Str__Url(self._normalize_url(str(url))),
                                                        final_url      = response.final_url,
                                                        status_code    = response.status_code,
                                                        content_type   = response.headers.get('Content-Type', ''),
                                                        content_length = Safe_UInt__Bytes(len(response.html.encode('utf-8'))),
                                                        etag           = response.headers.get('ETag', ''),
                                                        last_modified  = response.headers.get('Last-Modified', ''),
                                                        cache_control  = response.headers.get('Cache-Control', ''),
                                                        fetched_at     = Timestamp_Now(),
                                                        fetch_duration = response.duration_ms,
                                                        content_hash   = Safe_Str__Content_Hash(content_hash))
        
        self.storage.save(cache_id=cache_id, key=self.key_metadata(), data=metadata.json())
        return content_hash

    def _update_fetch_time(self, cache_id: Cache_Id, metadata: dict):
        """Update fetch time in metadata (for conditional hits)."""
        metadata['fetched_at'] = Timestamp_Now()
        self.storage.save(cache_id=cache_id, key=self.key_metadata(), data=metadata)

    def _save_html(self, cache_id: Cache_Id, html: str):                                    # Save HTML content.
        self.storage.save(cache_id=cache_id, key=self.key_html(), data={'html': html})

    def _load_html(self, cache_id: Cache_Id) -> str:
        """Load HTML content."""
        data = self.storage.load__json(cache_id=cache_id, key=self.key_html())
        if data:
            return data.get('html', '')
        return ''

    def _content_hash(self, content: str) -> str:
        """Generate 16-char hex hash for content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

    def _normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication."""
        parsed = urlparse(url.lower())
        # Remove trailing slash, default port, etc.
        path = parsed.path.rstrip('/') or '/'
        return urlunparse((parsed.scheme, parsed.netloc, path, '', '', ''))
