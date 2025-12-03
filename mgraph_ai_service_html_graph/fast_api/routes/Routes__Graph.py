from osbot_fast_api.api.routes.Fast_API__Routes                                     import Fast_API__Routes
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Dot__Response        import Schema__Graph__Dot__Response
from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Html__Request  import Schema__Graph__From_Html__Request
from mgraph_ai_service_html_graph.service.html_graph__export                        import Html_Graph__Export__Service

TAG__ROUTES_GRAPH = 'graph'
ROUTES_PATHS__GRAPH = [f'/{TAG__ROUTES_GRAPH}/from/html/to/dot'      ,
                       f'/{TAG__ROUTES_GRAPH}/from/html/to/visjs'    ,
                       f'/{TAG__ROUTES_GRAPH}/from/html/to/d3'       ,
                       f'/{TAG__ROUTES_GRAPH}/from/html/to/cytoscape',
                       f'/{TAG__ROUTES_GRAPH}/from/html/to/mermaid'  ]


class Routes__Graph(Fast_API__Routes):                                                            # Routes for graph export operations
    tag : str = TAG__ROUTES_GRAPH

    graph_service : Html_Graph__Export__Service                                                   # Auto-initialized by Type_Safe

    def from__html__to__dot(self, request: Schema__Graph__From_Html__Request                      # POST /graph/from/html/to/dot
                            ) -> Schema__Graph__Dot__Response:
        return self.graph_service.to_dot(request)

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
        return self