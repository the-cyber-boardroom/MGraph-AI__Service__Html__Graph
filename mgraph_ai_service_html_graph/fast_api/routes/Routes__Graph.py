# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Graph Routes
# v0.2.6 - Routes with transformation pipeline support + tree view engines
#
# New URL pattern: /graph/from/{source}/to/{engine}/{transformation}
# ═══════════════════════════════════════════════════════════════════════════════

from enum                                                                                import Enum
from typing import List

from osbot_fast_api.api.decorators.route_path                                            import route_path
from osbot_fast_api.api.routes.Fast_API__Routes                                          import Fast_API__Routes
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Dot__Response             import Schema__Graph__Dot__Response
from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Html__Request       import Schema__Graph__From_Html__Request
from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Url__Request        import Schema__Graph__From_Url__Request
from mgraph_ai_service_html_graph.schemas.routes.Schema__Html__From_Url__Request         import Schema__Html__From_Url__Request
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Schemas import Schema__Transformations__List__Response, Schema__Transformation__Info
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service import Html_Graph__Export__Service
from mgraph_ai_service_html_graph.service.html_url.Html__Url__Fetcher                    import Html__Url__Fetcher


# ═══════════════════════════════════════════════════════════════════════════════
# Enums for URL path parameters
# ═══════════════════════════════════════════════════════════════════════════════

class Source_Type(str, Enum):
    """Source type for graph conversion."""
    html = "html"
    url  = "url"


class Engine_Type(str, Enum):
    """Rendering engine for graph output."""
    dot       = "dot"
    visjs     = "visjs"
    d3        = "d3"
    cytoscape = "cytoscape"
    mermaid   = "mermaid"
    tree      = "tree"
    tree_text = "tree_text"


TAG__ROUTES_GRAPH = 'graph'


ROUTES_PATHS__GRAPH = [
    # Transformations list
    f'/{TAG__ROUTES_GRAPH}/transformations',
    f'/{TAG__ROUTES_GRAPH}/from/html/to/{{engine}}/{{transformation}}' ,
    f'/{TAG__ROUTES_GRAPH}/from/url/to/{{engine}}/{{transformation}}' ,
]

class Routes__Graph(Fast_API__Routes):                                                  # Routes for graph export with transformations
    tag           = TAG__ROUTES_GRAPH
    graph_service : Html_Graph__Export__Service
    url_fetcher   : Html__Url__Fetcher

    # ═══════════════════════════════════════════════════════════════════════════
    # Transformation List Endpoint
    # ═══════════════════════════════════════════════════════════════════════════

    def transformations(self) -> list:                                                                                # GET /graph/transformations
        return self.graph_service.list_transformations()                                                              # List all available graph transformations.

    # ═══════════════════════════════════════════════════════════════════════════
    # HTML to Engine with Transformation
    # ═══════════════════════════════════════════════════════════════════════════

    @route_path("/from/html/to/{engine}/{transformation}")
    def from_html_to_transformation(self, engine: str, transformation:str, request: Schema__Graph__From_Html__Request) -> Schema__Graph__Dot__Response:
        if engine == 'default':
            render_method = self.graph_service.to_dot
        elif engine == 'dot':
            render_method = self.graph_service.to_dot
        elif engine == 'visjs':
            render_method = self.graph_service.to_visjs
        elif engine == 'd3':
            render_method = self.graph_service.to_d3
        elif engine == 'cytoscape':
            render_method = self.graph_service.to_cytoscape
        elif engine == 'mermaid':
            render_method = self.graph_service.to_mermaid
        elif engine == 'tree':
            render_method = self.graph_service.to_tree
        elif engine == 'tree_text':
            render_method = self.graph_service.to_tree_text
        else:
            raise Exception(f"Unknown graph engine: {engine}")

        return render_method(request, transformation=transformation)

    @route_path("/from/url/to/{engine}/{transformation}")
    def from_url_to_transformation(self, engine: str, transformation: str, request: Schema__Graph__From_Url__Request) -> Schema__Graph__Dot__Response:
        html_request = self._fetch_and_create_request(request)
        return self.from_html_to_transformation(engine=engine, transformation=transformation, request= html_request)

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _fetch_and_create_request(self, request: Schema__Graph__From_Url__Request) -> Schema__Graph__From_Html__Request:
        url_request  = Schema__Html__From_Url__Request(url     = request.url,
                                                       timeout = request.timeout)
        url_response = self.url_fetcher.fetch_html(url_request)

        return Schema__Graph__From_Html__Request(html            = url_response.html      ,
                                                 preset          = request.preset         ,
                                                 show_tag_nodes  = request.show_tag_nodes ,
                                                 show_attr_nodes = request.show_attr_nodes,
                                                 show_text_nodes = request.show_text_nodes,
                                                 color_scheme    = request.color_scheme   )

    def setup_routes(self):
        # Transformation list endpoint
        self.add_route_get(self.transformations)

        # HTML to format with transformation endpoints
        self.add_route_post(self.from_html_to_transformation)
        self.add_route_post(self.from_url_to_transformation)
        return self