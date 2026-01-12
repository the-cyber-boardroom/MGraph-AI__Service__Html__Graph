# ═══════════════════════════════════════════════════════════════════════════════
# Html_Cache__Session_Factory - Factory for creating cache sessions
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from phase_e.url_fetch.Html_Cache__Session                                         import Html_Cache__Session
from phase_e.url_fetch.Html_Cache__Storage_Factory                                 import Html_Cache__Storage_Factory
from phase_e.url_fetch.schemas.Schema__Html_Fetcher__Config                        import Schema__Html_Fetcher__Config
from phase_e.storage.cache_service.Cache_Service__Client                           import Cache_Service__Client
from phase_e.storage.schemas.Schema__Perf__Storage__Config                         import Schema__Perf__Storage__Config
from phase_e.storage.safe_str.Safe_Str__Session_Name                               import Safe_Str__Session_Name


class Html_Cache__Session_Factory(Type_Safe):
    """Factory for creating cache sessions with all layers configured."""
    
    cache_client   : Cache_Service__Client                          # Cache service client
    storage_config : Schema__Perf__Storage__Config                  # Storage configuration
    fetcher_config : Schema__Html_Fetcher__Config                   # Default fetcher config

    # ═══════════════════════════════════════════════════════════════════════════
    # Public Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def create_session(self, session_name: Safe_Str__Session_Name) -> Html_Cache__Session:
        """Create a new cache session."""
        # Create storage factory for this session
        storage_factory = Html_Cache__Storage_Factory(
            config       = self.storage_config or Schema__Perf__Storage__Config(),
            cache_client = self.cache_client,
            session_name = session_name
        )
        
        # Create session with factory
        return Html_Cache__Session(
            session_name    = session_name,
            storage_factory = storage_factory,
            fetcher_config  = self.fetcher_config or Schema__Html_Fetcher__Config()
        ).setup()

    def create_session_with_name(self, name: str) -> Html_Cache__Session:
        """Convenience method - create session from plain string name."""
        return self.create_session(Safe_Str__Session_Name(name))
