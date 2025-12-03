from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Html__Request       import Schema__Graph__From_Html__Request
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph__To__Dot                import Html_MGraph__To__Dot
from osbot_utils.type_safe.Type_Safe                                                     import Type_Safe
from osbot_utils.helpers.html.transformers.Html__To__Html_Dict                           import Html__To__Html_Dict
from mgraph_ai_service_html_graph.service.html_graph.Html_Dict__OSBot__To__Html_Dict     import Html_Dict__OSBot__To__Html_Dict
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph                         import Html_MGraph
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config        import Html_MGraph__Render__Config
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors        import Html_MGraph__Render__Colors
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Labels        import Html_MGraph__Render__Labels
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Dot__Response             import Schema__Graph__Dot__Response
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Stats                     import Schema__Graph__Stats


class Html_Graph__Export__Service(Type_Safe):                                                     # Service to export HTML graphs to various formats

    def html_to_mgraph(self, html: str) -> Html_MGraph:                                           # Convert HTML string to Html_MGraph
        html_dict__osbot = Html__To__Html_Dict(html=html).convert()
        html_dict        = Html_Dict__OSBot__To__Html_Dict().convert(html_dict__osbot)
        return Html_MGraph.from_html_dict(html_dict)

    def create_config(self, request: Schema__Graph__From_Html__Request                            # Create render config from request
                      ) -> Html_MGraph__Render__Config:
        config = Html_MGraph__Render__Config(colors = Html_MGraph__Render__Colors() ,
                                             labels = Html_MGraph__Render__Labels() )
        config.apply_preset(request.preset)                                                       # Apply preset (full_detail, structure_only, minimal)
        config.show_tag_nodes  = request.show_tag_nodes                                           # Apply visibility settings
        config.show_attr_nodes = request.show_attr_nodes
        config.show_text_nodes = request.show_text_nodes
        config.show_tag_edges  = request.show_tag_nodes                                           # Edge visibility follows node visibility
        config.show_attr_edges = request.show_attr_nodes
        config.show_text_edges = request.show_text_nodes
        config.set_color_scheme(request.color_scheme)                                             # Apply color scheme
        return config

    def get_stats(self, html_mgraph: Html_MGraph) -> Schema__Graph__Stats:                        # Get graph statistics as schema
        raw_stats = html_mgraph.stats()
        return Schema__Graph__Stats(total_nodes   = raw_stats.get('total_nodes'  , 0) ,
                                    total_edges   = raw_stats.get('total_edges'  , 0) ,
                                    element_nodes = raw_stats.get('element_nodes', 0) ,
                                    value_nodes   = raw_stats.get('value_nodes'  , 0) ,
                                    tag_nodes     = raw_stats.get('tag_nodes'    , 0) ,
                                    text_nodes    = raw_stats.get('text_nodes'   , 0) ,
                                    attr_nodes    = raw_stats.get('attr_nodes'   , 0) )

    def to_dot(self, request: Schema__Graph__From_Html__Request                                   # Convert HTML to DOT format
               ) -> Schema__Graph__Dot__Response:
        html_mgraph = self.html_to_mgraph(request.html)                                           # Parse HTML to MGraph
        config      = self.create_config(request)                                                 # Create render config
        exporter    = Html_MGraph__To__Dot(mgraph = html_mgraph.mgraph ,                          # Create exporter
                                           config = config             )
        dot_string  = exporter.to_string()                                                        # Generate DOT string
        stats       = self.get_stats(html_mgraph)                                                 # Get statistics

        return Schema__Graph__Dot__Response(dot   = dot_string ,
                                            stats = stats      )