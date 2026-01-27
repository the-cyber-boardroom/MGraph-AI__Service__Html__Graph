# ═══════════════════════════════════════════════════════════════════════════════
# Html_Graph__Service__In_Memory
# In-memory Html Graph service wrapper for testing and embedded usage
# Accepts injected cache client for flexible composition
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                         import Any
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from mgraph_ai_service_html_graph.schemas.in_memory.Schema__Html_Graph__Service__In_Memory__Config  import Schema__Html_Graph__Service__In_Memory__Config
from mgraph_ai_service_cache_client.client.client_contract.Cache__Service__Fast_API__Client         import Cache__Service__Fast_API__Client
from mgraph_ai_service_cache.service.cache.in_memory.Cache__Service__In_Memory                      import Cache__Service__In_Memory
from mgraph_ai_service_html_graph.fast_api.Html_Graph__Service__Fast_API                            import Html_Graph__Service__Fast_API
from mgraph_ai_service_html_graph.client.Html_Graph__Service__Client                                import Html_Graph__Service__Client
from mgraph_ai_service_html_graph.client.Html_Graph__Service__Client__Config                        import Html_Graph__Service__Client__Config
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API__Config                                import Serverless__Fast_API__Config


class Html_Graph__Service__In_Memory(Type_Safe):                                # In-memory Html Graph service
    config             : Schema__Html_Graph__Service__In_Memory__Config         # Configuration for in-memory mode
    html_graph_service : Html_Graph__Service__Fast_API           = None         # Backend service (set by setup)
    fast_api_app       : Any                                     = None         # FastAPI app (set by setup)
    cache_client       : Cache__Service__Fast_API__Client        = None         # Injected cache client
    html_graph_client  : Html_Graph__Service__Client             = None         # Client for html graph operations (set by setup)

    def setup(self, cache_client: Cache__Service__Fast_API__Client = None       # Initialize in-memory service
             ) -> 'Html_Graph__Service__In_Memory':                             # Returns self for chaining
        if cache_client:
            self.cache_client = cache_client
        self.setup_html_graph_service()
        self.setup_fast_api_app()
        self.setup_html_graph_client()
        return self

    def setup_html_graph_service(self):                                         # Create backend Html Graph service
        self.html_graph_service = Html_Graph__Service__Fast_API(cache_client=self.cache_client)

    def setup_fast_api_app(self):                                               # Create FastAPI app
        serverless_config   = Serverless__Fast_API__Config(enable_api_key=self.config.enable_api_key)
        html_graph_fast_api = Html_Graph__Service__Fast_API(config             = serverless_config      ,
                                                            html_graph_service = self.html_graph_service)
        html_graph_fast_api.setup()
        self.fast_api_app = html_graph_fast_api.app()

    def setup_html_graph_client(self):                                          # Create client pointing to in-memory app
        config                 = Html_Graph__Service__Client__Config(fast_api_app=self.fast_api_app)
        self.html_graph_client = Html_Graph__Service__Client(config=config)


def html_graph_client__in_memory(cache_client: Cache__Service__Fast_API__Client = None):  # Convenience function
    return Html_Graph__Service__In_Memory().setup(cache_client=cache_client).html_graph_client


def html_graph_client__in_memory__with_cache():                                 # Full in-memory stack (Html Graph + Cache)
    cache_in_memory = Cache__Service__In_Memory().setup()
    return Html_Graph__Service__In_Memory().setup(cache_client=cache_in_memory.cache_client).html_graph_client
