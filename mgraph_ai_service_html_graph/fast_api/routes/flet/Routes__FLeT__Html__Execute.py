# ═══════════════════════════════════════════════════════════════════════════════
# Routes__FLeT__Html__Execute - REST API for low-level FLeT HTML execution
# Provides endpoints to execute FLeT__Html__To__Cache and FLeT__Html__From__Cache
#
# Path pattern: /flet/html/to/cache/{namespace}/{cache_id}
#               /flet/html/from/cache/{namespace}/{cache_id}
#
# Note: These require an existing cache_id (entity must already exist)
# For orchestrated operations that create entities, see Routes__FLeT__Html__Domain
# ═══════════════════════════════════════════════════════════════════════════════

from fastapi                                                                                    import HTTPException
from osbot_fast_api.api.decorators.route_path                                                   import route_path
from osbot_fast_api.api.routes.Fast_API__Routes                                                 import Fast_API__Routes
from mgraph_ai_service_html_graph.schemas.flet.html.Schema__FLeT__Html__From__Cache__Request    import Schema__FLeT__Html__From__Cache__Request
from mgraph_ai_service_html_graph.schemas.flet.html.Schema__FLeT__Html__From__Cache__Response   import Schema__FLeT__Html__From__Cache__Response
from mgraph_ai_service_html_graph.schemas.flet.html.Schema__FLeT__Html__To__Cache__Request      import Schema__FLeT__Html__To__Cache__Request
from mgraph_ai_service_html_graph.schemas.flet.html.Schema__FLeT__Html__To__Cache__Response     import Schema__FLeT__Html__To__Cache__Response
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.FLeT__Html__Execute__Service       import FLeT__Html__Execute__Service

TAG__ROUTES_FLET_HTML_EXECUTE = 'flet-html-execute'

ROUTES_PATHS__FLET_HTML_EXECUTE = [f'/{TAG__ROUTES_FLET_HTML_EXECUTE}' + '/html/to/cache/{namespace}/{cache_id}'  ,
                                   f'/{TAG__ROUTES_FLET_HTML_EXECUTE}' + '/html/from/cache/{namespace}/{cache_id}']


class Routes__FLeT__Html__Execute(Fast_API__Routes):                                # FLeT HTML execution routes
    tag     : str                          = TAG__ROUTES_FLET_HTML_EXECUTE          # Route tag
    service : FLeT__Html__Execute__Service                                          # Execution service

    # ═══════════════════════════════════════════════════════════════════════════════
    # Execute Html-To-Cache
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/html/to/cache/{namespace}/{cache_id}')
    def html__to__cache(self                                              ,         # Store HTML in cache via FLeT
                        namespace : str                                   ,         # Cache namespace
                        cache_id  : str                                   ,         # Entity cache ID
                        request   : Schema__FLeT__Html__To__Cache__Request          # Request with HTML content
                   ) -> Schema__FLeT__Html__To__Cache__Response:                    # POST /html/to/cache/{namespace}/{cache_id}
        try:
            return self.service.execute_to_cache(namespace = namespace ,
                                                 cache_id  = cache_id  ,
                                                 request   = request   )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Execute Html-From-Cache
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/html/from/cache/{namespace}/{cache_id}')
    def html__from__cache(self                                                ,     # Retrieve HTML from cache via FLeT
                          namespace : str                                     ,     # Cache namespace
                          cache_id  : str                                     ,     # Entity cache ID
                          request   : Schema__FLeT__Html__From__Cache__Request      # Request with data location
                     ) -> Schema__FLeT__Html__From__Cache__Response:                # POST /html/from/cache/{namespace}/{cache_id}
        try:
            return self.service.execute_from_cache(namespace = namespace ,
                                                   cache_id  = cache_id  ,
                                                   request   = request   )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Route Setup
    # ═══════════════════════════════════════════════════════════════════════════════

    def setup_routes(self):                                                         # Configure all routes
        self.add_route_post(self.html__to__cache   )
        self.add_route_post(self.html__from__cache )

        return self