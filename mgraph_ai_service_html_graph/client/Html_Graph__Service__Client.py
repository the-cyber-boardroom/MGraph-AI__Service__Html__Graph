# ═══════════════════════════════════════════════════════════════════════════════
# Html_Graph__Service__Client
# HTTP client for Html Graph service store/load operations
# Supports IN_MEMORY (TestClient) and REMOTE (requests) modes
# ═══════════════════════════════════════════════════════════════════════════════

from urllib.parse                                                                                   import urlparse
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Load__Response                  import Schema__Html__Load__Response
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Store__Response                 import Schema__Html__Store__Response
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode import Enum__Fast_API__Service__Registry__Client__Mode
from osbot_utils.decorators.methods.cache_on_self                                                   import cache_on_self
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                   import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                           import Safe_Str__Html
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                            import Safe_Str__Url
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                      import type_safe
from osbot_utils.utils.Env                                                                          import get_env
from mgraph_ai_service_html_graph.client.Html_Graph__Service__Client__Config                        import Html_Graph__Service__Client__Config
from mgraph_ai_service_html_graph.client.Html_Graph__Service__Client__Requests                      import Html_Graph__Service__Client__Requests
from mgraph_ai_service_html_graph.schemas.client.consts__html_graph_client                          import (ENV_VAR__HTML_GRAPH__BASE_URL  ,
                                                                                                            ENV_VAR__HTML_GRAPH__KEY_NAME  ,
                                                                                                            ENV_VAR__HTML_GRAPH__KEY_VALUE ,
                                                                                                            ENV_VAR__HTML_GRAPH__NAMESPACE )

# todo: refactor this to match the routes structure, just like we did for the cache service

class Html_Graph__Service__Client(Type_Safe):                                   # Client for Html Graph service
    config: Html_Graph__Service__Client__Config                                 # Client configuration

    @cache_on_self
    def requests(self) -> Html_Graph__Service__Client__Requests:                # Get request handler
        self.setup_config_from_env()
        return Html_Graph__Service__Client__Requests(config=self.config)

    def setup_config_from_env(self) -> 'Html_Graph__Service__Client':           # Configure from environment
        key_name   = get_env(ENV_VAR__HTML_GRAPH__KEY_NAME )
        key_value  = get_env(ENV_VAR__HTML_GRAPH__KEY_VALUE)
        target_url = get_env(ENV_VAR__HTML_GRAPH__BASE_URL )
        namespace  = get_env(ENV_VAR__HTML_GRAPH__NAMESPACE)

        if target_url:                                                          # Only set if env vars present
            with self.config as _:
                _.base_url = target_url
                _.mode     = Enum__Fast_API__Service__Registry__Client__Mode.REMOTE
                if key_name and key_value:
                    _.api_key_header = key_name
                    _.api_key        = key_value
                if namespace:
                    _.namespace = namespace
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # URL Utilities
    # ═══════════════════════════════════════════════════════════════════════════

    # todo: refactor to use version of Url__To__Cache_Key from Osbot-utils (after that refactoring has taken place)
    @type_safe
    def url_to_cache_key(self, url: Safe_Str__Url) -> Safe_Str__File__Path:                 # Convert URL to cache key
        parsed = urlparse(str(url))
        domain = parsed.netloc

        if not domain:
            return Safe_Str__File__Path("unknown/root")

        path = parsed.path.strip('/')

        if not path:
            path = "root"

        return f"{domain}/{path}"

    # ═══════════════════════════════════════════════════════════════════════════
    # Store Operations
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def store_html(self, url  : Safe_Str__Url ,                                 # Store HTML content by URL
                         html : Safe_Str__Html                                  # HTML content to store
                  ) -> Schema__Html__Store__Response:                           # Store result

        cache_key   = self.url_to_cache_key(url)
        namespace   = self.config.namespace
        path        = f"/flet-html-domain/html/store/{namespace}/key/{cache_key}"



        result = self.requests().execute(method = "POST"         ,
                                         path   = path           ,
                                         body   = {"html": html} )

        if result.status_code == 200:
            return Schema__Html__Store__Response.from_json(result.json)
        else:
            return None

    # ═══════════════════════════════════════════════════════════════════════════
    # Load Operations
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def load_html(self, url: Safe_Str__Url                                      # Load HTML content by URL
                 ) -> Schema__Html__Load__Response:                             # Load result

        cache_key = self.url_to_cache_key(url)
        namespace = self.config.namespace
        path      = f"/flet-html-domain/html/load/{namespace}/key/{cache_key}"


        result = self.requests().execute(method = "POST" ,
                                         path   = path   ,
                                         body   = {}     )

        if result.status_code == 200:
            return Schema__Html__Load__Response.from_json(result.json)
        return None

    # ═══════════════════════════════════════════════════════════════════════════
    # Health Check
    # ═══════════════════════════════════════════════════════════════════════════

    def health(self) -> bool:                                                   # Check service health
        try:
            result = self.requests().execute(method="GET", path="/info/health")
            if result.status_code == 200:
                data = result.json or {}
                return data.get('status') == 'ok'
            return False
        except:
            return False
