# ═══════════════════════════════════════════════════════════════════════════════
# Routes__FLeT__Html__Domain - REST API for domain-level HTML operations
# Provides orchestrated endpoints that auto-create entities and handle lookups
#
# Store paths: /flet/html/store/{namespace}/raw
#              /flet/html/store/{namespace}/url
#              /flet/html/store/{namespace}/key/{cache_key:path}
#
# Load paths:  /flet/html/load/{namespace}/id
#              /flet/html/load/{namespace}/hash
#              /flet/html/load/{namespace}/key/{cache_key:path}
#              /flet/html/load/{namespace}/url
# ═══════════════════════════════════════════════════════════════════════════════

from fastapi                                                                                   import HTTPException
from osbot_fast_api.api.decorators.route_path                                                  import route_path
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Load__Hash__Request        import Schema__Html__Load__Hash__Request
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Load__Id__Request          import Schema__Html__Load__Id__Request
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Load__Response             import Schema__Html__Load__Response
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Load__Url__Request         import Schema__Html__Load__Url__Request
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Store__Key__Request        import Schema__Html__Store__Key__Request
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Store__Raw__Request        import Schema__Html__Store__Raw__Request
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Store__Response            import Schema__Html__Store__Response
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Store__Url__Request        import Schema__Html__Store__Url__Request
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.FLeT__Html__Domain__Service       import FLeT__Html__Domain__Service
from osbot_fast_api.api.routes.Fast_API__Routes                                                import Fast_API__Routes


TAG__ROUTES_FLET_HTML_DOMAIN = 'flet-html-domain'

ROUTES_PATHS__FLET_HTML_DOMAIN = [f'/{TAG__ROUTES_FLET_HTML_DOMAIN}'+ '/html/store/{namespace}/raw'                 ,
                                  f'/{TAG__ROUTES_FLET_HTML_DOMAIN}'+ '/html/store/{namespace}/url'                 ,
                                  f'/{TAG__ROUTES_FLET_HTML_DOMAIN}'+ '/html/store/{namespace}/key/{cache_key:path}',
                                  f'/{TAG__ROUTES_FLET_HTML_DOMAIN}'+ '/html/load/{namespace}/id'                   ,
                                  f'/{TAG__ROUTES_FLET_HTML_DOMAIN}'+ '/html/load/{namespace}/hash'                 ,
                                  f'/{TAG__ROUTES_FLET_HTML_DOMAIN}'+ '/html/load/{namespace}/key/{cache_key:path}' ,
                                  f'/{TAG__ROUTES_FLET_HTML_DOMAIN}'+ '/html/load/{namespace}/url'                  ]


class Routes__FLeT__Html__Domain(Fast_API__Routes):                                 # Domain-level HTML routes
    tag     : str                         = TAG__ROUTES_FLET_HTML_DOMAIN            # Route tag
    service : FLeT__Html__Domain__Service = None                                    # Domain service

    # ═══════════════════════════════════════════════════════════════════════════════
    # Store Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/html/store/{namespace}/raw')
    def store__raw(self                                          ,                  # Store raw HTML, auto-gen key
                   namespace : str                               ,                  # Cache namespace
                   request   : Schema__Html__Store__Raw__Request                    # Request with HTML content
              ) -> Schema__Html__Store__Response:                                   # POST /html/store/{namespace}/raw
        try:
            return self.service.store_raw(namespace = namespace ,
                                          request   = request   )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @route_path('/html/store/{namespace}/url')
    def store__url(self                                          ,                  # Fetch HTML from URL and store
                   namespace : str                               ,                  # Cache namespace
                   request   : Schema__Html__Store__Url__Request                    # Request with URL
              ) -> Schema__Html__Store__Response:                                   # POST /html/store/{namespace}/url
        try:
            return self.service.store_from_url(namespace = namespace ,
                                               request   = request   )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @route_path('/html/store/{namespace}/key/{cache_key:path}')
    def store__key(self                                          ,                  # Store HTML with explicit key
                   namespace : str                               ,                  # Cache namespace
                   cache_key : str                               ,                  # Explicit cache key
                   request   : Schema__Html__Store__Key__Request                    # Request with HTML content
              ) -> Schema__Html__Store__Response:                                   # POST /html/store/{namespace}/key/{cache_key}
        try:
            return self.service.store_with_key(namespace = namespace ,
                                               cache_key = cache_key ,
                                               request   = request   )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Load Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/html/load/{namespace}/id')
    def load__id(self                                         ,                     # Load HTML by cache_id
                 namespace : str                              ,                     # Cache namespace
                 request   : Schema__Html__Load__Id__Request                        # Request with cache_id
            ) -> Schema__Html__Load__Response:                                      # POST /html/load/{namespace}/id
        try:
            result = self.service.load_by_id(namespace = namespace ,
                                             request   = request   )
            if result.success is False:
                raise HTTPException(status_code = 404                                    ,
                                    detail      = f"Entity not found: {request.cache_id}")
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @route_path('/html/load/{namespace}/hash')
    def load__hash(self                                          ,                  # Load HTML by cache_hash
                   namespace : str                               ,                  # Cache namespace
                   request   : Schema__Html__Load__Hash__Request                    # Request with cache_hash
              ) -> Schema__Html__Load__Response:                                    # POST /html/load/{namespace}/hash
        try:
            return self.service.load_by_hash(namespace = namespace ,
                                             request   = request   )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @route_path('/html/load/{namespace}/key/{cache_key:path}')
    def load__key(self              ,                                               # Load HTML by cache_key
                  namespace : str   ,                                               # Cache namespace
                  cache_key : str                                                   # Cache key to lookup
             ) -> Schema__Html__Load__Response:                                     # POST /html/load/{namespace}/key/{cache_key}
        try:
            return self.service.load_by_key(namespace = namespace ,
                                            cache_key = cache_key )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @route_path('/html/load/{namespace}/url')
    def load__url(self                                          ,                   # Load HTML by URL as key
                  namespace : str                               ,                   # Cache namespace
                  request   : Schema__Html__Load__Url__Request                      # Request with URL
             ) -> Schema__Html__Load__Response:                                     # POST /html/load/{namespace}/url
        try:
            return self.service.load_by_url(namespace = namespace ,
                                            request   = request   )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Route Setup
    # ═══════════════════════════════════════════════════════════════════════════════

    def setup_routes(self):                                                         # Configure all routes
        self.add_route_post(self.store__raw )
        self.add_route_post(self.store__url )
        self.add_route_post(self.store__key )

        self.add_route_post(self.load__id   )
        self.add_route_post(self.load__hash )
        self.add_route_post(self.load__key  )
        self.add_route_post(self.load__url  )

        return self