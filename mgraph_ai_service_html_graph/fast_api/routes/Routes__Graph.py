from osbot_fast_api.api.routes.Fast_API__Routes                                             import Fast_API__Routes
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Dot__Response                import Schema__Graph__Dot__Response
from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Html__Request          import Schema__Graph__From_Html__Request
from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Url__Request           import Schema__Graph__From_Url__Request
from mgraph_ai_service_html_graph.schemas.routes.Schema__Html__From_Url__Request            import Schema__Html__From_Url__Request
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service    import Html_Graph__Export__Service
from mgraph_ai_service_html_graph.service.html_url.Html__Url__Fetcher                       import Html__Url__Fetcher

TAG__ROUTES_GRAPH = 'graph'
ROUTES_PATHS__GRAPH = [f'/{TAG__ROUTES_GRAPH}/from/html/to/dot'      ,
                       # f'/{TAG__ROUTES_GRAPH}/from/html/to/visjs'    ,
                       # f'/{TAG__ROUTES_GRAPH}/from/html/to/d3'       ,
                       # f'/{TAG__ROUTES_GRAPH}/from/html/to/cytoscape',
                       # f'/{TAG__ROUTES_GRAPH}/from/html/to/mermaid'
                        f'/{TAG__ROUTES_GRAPH}/from/url/to/dot'       ,
                       ]


class Routes__Graph(Fast_API__Routes):                                                            # Routes for graph export operations
    tag           = TAG__ROUTES_GRAPH
    graph_service : Html_Graph__Export__Service                                                   # Auto-initialized by Type_Safe
    url_fetcher   : Html__Url__Fetcher

    def from__html__to__dot(self, request: Schema__Graph__From_Html__Request                      # POST /graph/from/html/to/dot
                            ) -> Schema__Graph__Dot__Response:
        return self.graph_service.to_dot(request)

    def from__url__to__dot(self,                                                                  # POST /graph/from/url/to/dot
                           request: Schema__Graph__From_Url__Request
                               ) -> Schema__Graph__Dot__Response:
        # First fetch the HTML from URL
        url_request  = Schema__Html__From_Url__Request(url     = request.url     ,
                                                       timeout = request.timeout )
        url_response = self.url_fetcher.fetch_html(url_request)

        # Then convert to DOT using existing service
        html_request = Schema__Graph__From_Html__Request(html            = url_response.html       ,
                                                         preset          = request.preset          ,
                                                         show_tag_nodes  = request.show_tag_nodes  ,
                                                         show_attr_nodes = request.show_attr_nodes ,
                                                         show_text_nodes = request.show_text_nodes ,
                                                         color_scheme    = request.color_scheme    )
        return self.graph_service.to_dot(html_request)
    # def from__html__to__visjs(self, request: Schema__Graph__From_Html__Request                  # POST /graph/from/html/to/visjs (future)
    #                           ) -> Schema__Graph__VisJs__Response:
    #     return self.graph_service.to_visjs(request)

    # def from__html__to__d3(self, request: Schema__Graph__From_Html__Request                     # POST /graph/from/html/to/d3 (future)
    #                        ) -> Schema__Graph__D3__Response:
    #     return self.graph_service.to_d3(request)

    # def from__html__to__cytoscape(self, request: Schema__Graph__From_Html__Request              # POST /graph/from/html/to/cytoscape (future)
    #                               ) -> Schema__Graph__Cytoscape__Response:
    #     return self.graph_service.to_cytoscape(request)

    # def from__html__to__mermaid(self, request: Schema__Graph__From_Html__Request                # POST /graph/from/html/to/mermaid (future)
    #                             ) -> Schema__Graph__Mermaid__Response:
    #     return self.graph_service.to_mermaid(request)

    def setup_routes(self):
        self.add_route_post(self.from__html__to__dot)
        # self.add_route_post(self.from__html__to__visjs    )                                     # Enable when implemented
        # self.add_route_post(self.from__html__to__d3       )
        # self.add_route_post(self.from__html__to__cytoscape)
        # self.add_route_post(self.from__html__to__mermaid  )
        self.add_route_post(self.from__url__to__dot )
        return self