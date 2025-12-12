# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Graph Routes (Updated)
# Routes for graph export operations - all formats enabled
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_fast_api.api.routes.Fast_API__Routes                                             import Fast_API__Routes
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Dot__Response                import Schema__Graph__Dot__Response
from mgraph_ai_service_html_graph.schemas.render_engines.cytoscape.Schemas__For__Cytoscape  import Schema__Graph__Cytoscape__Response
from mgraph_ai_service_html_graph.schemas.render_engines.d3.Schemas__For__D3                import Schema__Graph__D3__Response
from mgraph_ai_service_html_graph.schemas.render_engines.mermaid.Schemas__For__Mermaid import Schema__Graph__Mermaid__Response
from mgraph_ai_service_html_graph.schemas.render_engines.vis_js.Schemas__For__VisJs import Schema__Graph__VisJs__Response

from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Html__Request      import Schema__Graph__From_Html__Request
from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Url__Request       import Schema__Graph__From_Url__Request
from mgraph_ai_service_html_graph.schemas.routes.Schema__Html__From_Url__Request        import Schema__Html__From_Url__Request
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service import Html_Graph__Export__Service
from mgraph_ai_service_html_graph.service.html_url.Html__Url__Fetcher                    import Html__Url__Fetcher

TAG__ROUTES_GRAPH = 'graph'
ROUTES_PATHS__GRAPH = [f'/{TAG__ROUTES_GRAPH}/from/html/to/dot'       ,
                       f'/{TAG__ROUTES_GRAPH}/from/html/to/visjs'     ,
                       f'/{TAG__ROUTES_GRAPH}/from/html/to/d3'        ,
                       f'/{TAG__ROUTES_GRAPH}/from/html/to/cytoscape' ,
                       f'/{TAG__ROUTES_GRAPH}/from/html/to/mermaid'   ,
                       f'/{TAG__ROUTES_GRAPH}/from/url/to/dot'        ,
                       f'/{TAG__ROUTES_GRAPH}/from/url/to/visjs'      ,
                       f'/{TAG__ROUTES_GRAPH}/from/url/to/d3'         ,
                       f'/{TAG__ROUTES_GRAPH}/from/url/to/cytoscape'  ,
                       f'/{TAG__ROUTES_GRAPH}/from/url/to/mermaid'    ]


class Routes__Graph(Fast_API__Routes):                                                  # Routes for graph export operations
    tag           = TAG__ROUTES_GRAPH
    graph_service : Html_Graph__Export__Service                                         # Auto-initialized by Type_Safe
    url_fetcher   : Html__Url__Fetcher

    # ═══════════════════════════════════════════════════════════════════════════
    # HTML to Graph Format Endpoints
    # ═══════════════════════════════════════════════════════════════════════════

    def from__html__to__dot(self, request: Schema__Graph__From_Html__Request            # POST /graph/from/html/to/dot
                            ) -> Schema__Graph__Dot__Response:
        return self.graph_service.to_dot(request)

    def from__html__to__visjs(self, request: Schema__Graph__From_Html__Request          # POST /graph/from/html/to/visjs
                              ) -> Schema__Graph__VisJs__Response:
        return self.graph_service.to_visjs(request)

    def from__html__to__d3(self, request: Schema__Graph__From_Html__Request             # POST /graph/from/html/to/d3
                           ) -> Schema__Graph__D3__Response:
        return self.graph_service.to_d3(request)

    def from__html__to__cytoscape(self, request: Schema__Graph__From_Html__Request      # POST /graph/from/html/to/cytoscape
                                  ) -> Schema__Graph__Cytoscape__Response:
        return self.graph_service.to_cytoscape(request)

    def from__html__to__mermaid(self, request: Schema__Graph__From_Html__Request        # POST /graph/from/html/to/mermaid
                                ) -> Schema__Graph__Mermaid__Response:
        return self.graph_service.to_mermaid(request)

    # ═══════════════════════════════════════════════════════════════════════════
    # URL to Graph Format Endpoints
    # ═══════════════════════════════════════════════════════════════════════════

    def from__url__to__dot(self, request: Schema__Graph__From_Url__Request              # POST /graph/from/url/to/dot
                           ) -> Schema__Graph__Dot__Response:
        html_request = self._fetch_and_create_request(request)
        return self.graph_service.to_dot(html_request)

    def from__url__to__visjs(self, request: Schema__Graph__From_Url__Request            # POST /graph/from/url/to/visjs
                             ) -> Schema__Graph__VisJs__Response:
        html_request = self._fetch_and_create_request(request)
        return self.graph_service.to_visjs(html_request)

    def from__url__to__d3(self, request: Schema__Graph__From_Url__Request               # POST /graph/from/url/to/d3
                          ) -> Schema__Graph__D3__Response:
        html_request = self._fetch_and_create_request(request)
        return self.graph_service.to_d3(html_request)

    def from__url__to__cytoscape(self, request: Schema__Graph__From_Url__Request        # POST /graph/from/url/to/cytoscape
                                 ) -> Schema__Graph__Cytoscape__Response:
        html_request = self._fetch_and_create_request(request)
        return self.graph_service.to_cytoscape(html_request)

    def from__url__to__mermaid(self, request: Schema__Graph__From_Url__Request          # POST /graph/from/url/to/mermaid
                               ) -> Schema__Graph__Mermaid__Response:
        html_request = self._fetch_and_create_request(request)
        return self.graph_service.to_mermaid(html_request)

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _fetch_and_create_request(self, request: Schema__Graph__From_Url__Request       # Fetch HTML and create graph request
                                  ) -> Schema__Graph__From_Html__Request:
        url_request  = Schema__Html__From_Url__Request(url     = request.url     ,
                                                       timeout = request.timeout )
        url_response = self.url_fetcher.fetch_html(url_request)

        return Schema__Graph__From_Html__Request(html            = url_response.html       ,
                                                 preset          = request.preset          ,
                                                 show_tag_nodes  = request.show_tag_nodes  ,
                                                 show_attr_nodes = request.show_attr_nodes ,
                                                 show_text_nodes = request.show_text_nodes ,
                                                 color_scheme    = request.color_scheme    )

    def setup_routes(self):
        # HTML to format endpoints
        self.add_route_post(self.from__html__to__dot      )
        self.add_route_post(self.from__html__to__visjs    )
        self.add_route_post(self.from__html__to__d3       )
        self.add_route_post(self.from__html__to__cytoscape)
        self.add_route_post(self.from__html__to__mermaid  )

        # URL to format endpoints
        self.add_route_post(self.from__url__to__dot       )
        self.add_route_post(self.from__url__to__visjs     )
        self.add_route_post(self.from__url__to__d3        )
        self.add_route_post(self.from__url__to__cytoscape )
        self.add_route_post(self.from__url__to__mermaid   )

        return self
