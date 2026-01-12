# ═══════════════════════════════════════════════════════════════════════════════
# Html_Cache__Session - A cache session that processes multiple URLs/targets
# ═══════════════════════════════════════════════════════════════════════════════

import re
from urllib.parse                                                                  import urlparse
from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url           import Safe_Str__Url
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                 import Cache_Id
from phase_e.url_fetch.Html_Fetcher                                                import Html_Fetcher
from phase_e.url_fetch.Html_Cache__Layer__Url                                      import Html_Cache__Layer__Url
from phase_e.url_fetch.Html_Cache__Storage_Factory                                 import Html_Cache__Storage_Factory
from phase_e.url_fetch.schemas.Schema__Html_Fetcher__Config                        import Schema__Html_Fetcher__Config
from phase_e.url_fetch.schemas.Schema__Url_Fetch__Stats                            import Schema__Url_Fetch__Stats
from phase_e.storage.safe_str.Safe_Str__Session_Name                               import Safe_Str__Session_Name
from phase_e.storage.safe_str.Safe_Str__Target_Name                                import Safe_Str__Target_Name


class Html_Cache__Session(Type_Safe):
    """A cache session that can process multiple URLs/targets.
    
    This session handles L0 (URL fetching) and can optionally integrate 
    with Html_Cache__Manager for L1-L3 processing.
    """
    
    session_name    : Safe_Str__Session_Name                        # Session identifier
    storage_factory : Html_Cache__Storage_Factory                   # Factory for storage instances
    fetcher_config  : Schema__Html_Fetcher__Config                  # Fetcher configuration
    
    # Statistics
    url_stats       : Schema__Url_Fetch__Stats                      # L0 URL fetch stats
    
    # Internal state
    _fetcher        : Html_Fetcher = None                           # Shared fetcher instance
    _targets        : dict         = None                           # target_name → cache_id mapping

    # ═══════════════════════════════════════════════════════════════════════════
    # Setup and Lifecycle
    # ═══════════════════════════════════════════════════════════════════════════

    def setup(self) -> 'Html_Cache__Session':
        """Initialize session resources."""
        if self.url_stats is None:
            self.url_stats = Schema__Url_Fetch__Stats()
        if self.fetcher_config is None:
            self.fetcher_config = Schema__Html_Fetcher__Config()
        
        self._fetcher = Html_Fetcher(config=self.fetcher_config)
        self._targets = {}
        return self

    def __enter__(self):
        """Context manager entry."""
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        return False

    # ═══════════════════════════════════════════════════════════════════════════
    # Public Methods - URL Processing (L0 Only)
    # ═══════════════════════════════════════════════════════════════════════════

    def get_html_from_url(self                              ,
                          url           : Safe_Str__Url     ,
                          force_refresh : bool = False      ) -> str:
        """Fetch URL and return HTML (L0 layer)."""
        target_name = self._url_to_target(url)
        storage     = self._get_storage_for_target(target_name)
        cache_id    = storage.create_file__perf_entry()
        
        self._targets[str(target_name)] = cache_id
        
        layer_url = Html_Cache__Layer__Url(
            storage = storage,
            stats   = self.url_stats,
            fetcher = self._fetcher
        )
        
        return layer_url.get_html(
            cache_id      = cache_id,
            url           = url,
            force_refresh = force_refresh
        )

    def fetch_url(self                              ,
                  url           : Safe_Str__Url     ,
                  force_refresh : bool = False      ) -> str:
        """Alias for get_html_from_url."""
        return self.get_html_from_url(url, force_refresh)

    def batch_fetch_urls(self                              ,
                         urls          : list              ,
                         force_refresh : bool = False      ) -> dict:
        """Fetch multiple URLs and return HTML for each."""
        results = {
            'fetched'  : 0,
            'cached'   : 0,
            'failed'   : 0,
            'html'     : {}
        }
        
        for url in urls:
            try:
                safe_url = Safe_Str__Url(str(url))
                
                # Check stats before processing
                hits_before = self.url_stats.l0_hits
                
                html = self.get_html_from_url(safe_url, force_refresh=force_refresh)
                
                if html:
                    results['html'][str(url)] = html
                    if self.url_stats.l0_hits > hits_before:
                        results['cached'] += 1
                    else:
                        results['fetched'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                results['failed'] += 1
                print(f"Error fetching {url}: {e}")
        
        return results

    # ═══════════════════════════════════════════════════════════════════════════
    # Public Methods - Cache Status
    # ═══════════════════════════════════════════════════════════════════════════

    def has_url(self, url: Safe_Str__Url) -> bool:
        """Check if URL is cached at L0."""
        target_name = self._url_to_target(url)
        cache_id    = self._targets.get(str(target_name))
        if not cache_id:
            return False
        
        storage   = self._get_storage_for_target(target_name)
        layer_url = Html_Cache__Layer__Url(
            storage = storage,
            stats   = self.url_stats,
            fetcher = self._fetcher
        )
        return layer_url.exists(cache_id=cache_id)

    def get_cache_id_for_url(self, url: Safe_Str__Url) -> Cache_Id:
        """Get the cache_id for a URL (creates if needed)."""
        target_name = self._url_to_target(url)
        
        if str(target_name) in self._targets:
            return self._targets[str(target_name)]
        
        storage  = self._get_storage_for_target(target_name)
        cache_id = storage.create_file__perf_entry()
        self._targets[str(target_name)] = cache_id
        return cache_id

    def reset_stats(self):
        """Reset all statistics."""
        self.url_stats = Schema__Url_Fetch__Stats()

    def get_stats(self) -> dict:
        """Get URL fetch statistics."""
        return self.url_stats.json()

    # ═══════════════════════════════════════════════════════════════════════════
    # Private Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _url_to_target(self, url: Safe_Str__Url) -> Safe_Str__Target_Name:
        """Convert URL to safe target name."""
        parsed = urlparse(str(url))
        # example.com/page/1 → example-com-page-1
        raw    = f"{parsed.netloc}{parsed.path}"
        safe   = re.sub(r'[^a-zA-Z0-9]+', '-', raw)
        return Safe_Str__Target_Name(safe.strip('-').lower())

    def _get_storage_for_target(self, target_name: Safe_Str__Target_Name):
        """Get storage instance for target."""
        return self.storage_factory.create_for_layer(
            layer_name  = 'L0',
            target_name = target_name
        )
