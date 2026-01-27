# ═══════════════════════════════════════════════════════════════════════════════
# Html_Graph__Service__Client
# Stateless facade for Html Graph service operations
# Config is stored in registry, looked up at request time
# ═══════════════════════════════════════════════════════════════════════════════

from urllib.parse                                                                                   import urlparse
from mgraph_ai_service_html_graph.client.Html_Graph__Service__Client__Requests                      import Html_Graph__Service__Client__Requests
from mgraph_ai_service_html_graph.schemas.client.consts__html_graph_client                          import DEFAULT__HTML_GRAPH__NAMESPACE
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Load__Response                  import Schema__Html__Load__Response
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Store__Response                 import Schema__Html__Store__Response
from osbot_utils.decorators.methods.cache_on_self                                                   import cache_on_self
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                   import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                           import Safe_Str__Html
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                            import Safe_Str__Url
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                      import type_safe


class Html_Graph__Service__Client(Type_Safe):                                   # Stateless facade - config in registry

    @cache_on_self
    def requests(self) -> Html_Graph__Service__Client__Requests:                # Create transport with service_type set
        requests              = Html_Graph__Service__Client__Requests()
        requests.service_type = Html_Graph__Service__Client                     # Self-reference for registry lookup
        return requests

    # ───────────────────────────────────────────────────────────────────────────
    # URL Utilities
    # ───────────────────────────────────────────────────────────────────────────

    @type_safe
    def url_to_cache_key(self, url: Safe_Str__Url) -> Safe_Str__File__Path:     # Convert URL to cache key
        parsed = urlparse(url)
        domain = parsed.netloc

        if not domain:
            return Safe_Str__File__Path("unknown/root")

        path = parsed.path.strip('/')

        if not path:
            path = "root"

        return f"{domain}/{path}"

    # ───────────────────────────────────────────────────────────────────────────
    # Store Operations
    # ───────────────────────────────────────────────────────────────────────────

    @type_safe
    def store_html(self, url       : Safe_Str__Url                       ,      # Store HTML content by URL
                         html      : Safe_Str__Html                      ,      # HTML content to store
                         namespace : str = DEFAULT__HTML_GRAPH__NAMESPACE       # Cache namespace
                  ) -> Schema__Html__Store__Response:

        cache_key = self.url_to_cache_key(url)
        path      = f"/flet-html-domain/html/store/{namespace}/key/{cache_key}"

        result = self.requests().execute(method = "POST"        ,
                                         path   = path          ,
                                         body   = {"html": html})

        if result.status_code == 200:
            return Schema__Html__Store__Response.from_json(result.json())
        return None

    # ───────────────────────────────────────────────────────────────────────────
    # Load Operations
    # ───────────────────────────────────────────────────────────────────────────

    @type_safe
    def load_html(self, url       : Safe_Str__Url                       ,       # Load HTML content by URL
                        namespace : str = DEFAULT__HTML_GRAPH__NAMESPACE        # Cache namespace
                 ) -> Schema__Html__Load__Response:

        cache_key = self.url_to_cache_key(url)
        path      = f"/flet-html-domain/html/load/{namespace}/key/{cache_key}"

        result = self.requests().execute(method = "POST",
                                         path   = path  ,
                                         body   = {}    )

        if result.status_code == 200:
            return Schema__Html__Load__Response.from_json(result.json())
        return None

    # ───────────────────────────────────────────────────────────────────────────
    # Health Check
    # ───────────────────────────────────────────────────────────────────────────

    def health(self) -> bool:                                                   # Check service health
        try:
            result = self.requests().execute(method="GET", path="/info/health")
            if result.status_code == 200:
                data = result.json() or {}
                return data.get('status') == 'ok'
            return False
        except:
            return False