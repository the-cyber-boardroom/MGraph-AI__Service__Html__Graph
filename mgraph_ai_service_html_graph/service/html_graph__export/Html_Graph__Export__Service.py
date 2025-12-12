# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Export Service
# Unified service for exporting HTML graphs to all visualization formats
#
# Supports: DOT, vis.js, D3.js, Cytoscape.js, Mermaid
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.helpers.duration.decorators.capture_duration                           import capture_duration
from osbot_utils.helpers.html.transformers.Html__To__Html_Dict                          import Html__To__Html_Dict
from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Html__Request      import Schema__Graph__From_Html__Request
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Dot__Response            import Schema__Graph__Dot__Response
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Stats                    import Schema__Graph__Stats
from mgraph_ai_service_html_graph.service.html_graph.Html_Dict__OSBot__To__Html_Dict    import Html_Dict__OSBot__To__Html_Dict
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph                        import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph__To__Dot               import Html_MGraph__To__Dot
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config       import Html_MGraph__Render__Config
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors       import Html_MGraph__Render__Colors
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Labels       import Html_MGraph__Render__Labels

# New native exporters
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__VisJs     import Html_MGraph__To__VisJs
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__D3        import Html_MGraph__To__D3
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__Cytoscape import Html_MGraph__To__Cytoscape
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__Mermaid   import Html_MGraph__To__Mermaid


class Html_Graph__Export__Service(Type_Safe):                                           # Unified export service for all formats

    # ═══════════════════════════════════════════════════════════════════════════
    # Core Conversion Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def html_to_mgraph(self, html: str) -> Html_MGraph:                                 # Convert HTML string to Html_MGraph
        html_dict__osbot = Html__To__Html_Dict(html=html).convert()
        html_dict        = Html_Dict__OSBot__To__Html_Dict().convert(html_dict__osbot)
        return Html_MGraph.from_html_dict(html_dict)

    def create_config(self, request: Schema__Graph__From_Html__Request                  # Create render config from request
                      ) -> Html_MGraph__Render__Config:
        colors = Html_MGraph__Render__Colors()
        labels = Html_MGraph__Render__Labels()
        config = Html_MGraph__Render__Config(colors=colors, labels=labels)

        config.apply_preset(request.preset)                                             # Apply preset
        config.show_tag_nodes  = request.show_tag_nodes                                 # Node visibility
        config.show_attr_nodes = request.show_attr_nodes
        config.show_text_nodes = request.show_text_nodes
        config.show_tag_edges  = request.show_tag_nodes                                 # Edge visibility follows nodes
        config.show_attr_edges = request.show_attr_nodes
        config.show_text_edges = request.show_text_nodes
        config.set_color_scheme(request.color_scheme)                                   # Color scheme

        return config

    def get_stats(self, html_mgraph: Html_MGraph) -> Schema__Graph__Stats:              # Extract graph statistics
        raw_stats = html_mgraph.stats()
        return Schema__Graph__Stats(total_nodes   = raw_stats.get('total_nodes'  , 0),
                                    total_edges   = raw_stats.get('total_edges'  , 0),
                                    element_nodes = raw_stats.get('element_nodes', 0),
                                    value_nodes   = raw_stats.get('value_nodes'  , 0),
                                    tag_nodes     = raw_stats.get('tag_nodes'    , 0),
                                    text_nodes    = raw_stats.get('text_nodes'   , 0),
                                    attr_nodes    = raw_stats.get('attr_nodes'   , 0))

    # ═══════════════════════════════════════════════════════════════════════════
    # DOT Export (existing)
    # ═══════════════════════════════════════════════════════════════════════════

    def to_dot(self, request: Schema__Graph__From_Html__Request) -> Schema__Graph__Dot__Response:
        with capture_duration() as duration:
            html_mgraph = self.html_to_mgraph(request.html)
            config      = self.create_config(request)
            exporter    = Html_MGraph__To__Dot(mgraph=html_mgraph.mgraph, config=config)
            dot_string  = exporter.to_string()
            stats       = self.get_stats(html_mgraph)

            return Schema__Graph__Dot__Response(dot      = dot_string       ,
                                                stats    = stats            ,
                                                dot_size = len(dot_string)  ,
                                                duration = duration.seconds )

    # ═══════════════════════════════════════════════════════════════════════════
    # vis.js Export (NEW)
    # ═══════════════════════════════════════════════════════════════════════════

    def to_visjs(self, request: Schema__Graph__From_Html__Request) -> dict:
        with capture_duration() as duration:
            html_mgraph = self.html_to_mgraph(request.html)
            config      = self.create_config(request)
            exporter    = Html_MGraph__To__VisJs(mgraph=html_mgraph.mgraph, config=config)
            data        = exporter.export()
            stats       = self.get_stats(html_mgraph)

            return { 'nodes'    : data['nodes']       ,
                     'edges'    : data['edges']       ,
                     'rootId'   : data.get('rootId')  ,
                     'stats'    : stats.json()        ,
                     'duration' : duration.seconds    ,
                     'format'   : 'visjs'             }

    # ═══════════════════════════════════════════════════════════════════════════
    # D3.js Export (NEW)
    # ═══════════════════════════════════════════════════════════════════════════

    def to_d3(self, request: Schema__Graph__From_Html__Request) -> dict:
        with capture_duration() as duration:
            html_mgraph = self.html_to_mgraph(request.html)
            config      = self.create_config(request)
            exporter    = Html_MGraph__To__D3(mgraph=html_mgraph.mgraph, config=config)
            data        = exporter.export()
            stats       = self.get_stats(html_mgraph)

            return { 'nodes'    : data['nodes']       ,
                     'links'    : data['links']       ,
                     'rootId'   : data.get('rootId')  ,
                     'stats'    : stats.json()        ,
                     'duration' : duration.seconds    ,
                     'format'   : 'd3'                }

    # ═══════════════════════════════════════════════════════════════════════════
    # Cytoscape.js Export (NEW)
    # ═══════════════════════════════════════════════════════════════════════════

    def to_cytoscape(self, request: Schema__Graph__From_Html__Request) -> dict:
        with capture_duration() as duration:
            html_mgraph = self.html_to_mgraph(request.html)
            config      = self.create_config(request)
            exporter    = Html_MGraph__To__Cytoscape(mgraph=html_mgraph.mgraph, config=config)
            data        = exporter.export()
            stats       = self.get_stats(html_mgraph)

            return { 'elements' : data['elements']    ,
                     'rootId'   : data.get('rootId')  ,
                     'stats'    : stats.json()        ,
                     'duration' : duration.seconds    ,
                     'format'   : 'cytoscape'         }

    # ═══════════════════════════════════════════════════════════════════════════
    # Mermaid Export (NEW)
    # ═══════════════════════════════════════════════════════════════════════════

    def to_mermaid(self, request: Schema__Graph__From_Html__Request) -> dict:
        with capture_duration() as duration:
            html_mgraph = self.html_to_mgraph(request.html)
            config      = self.create_config(request)
            exporter    = Html_MGraph__To__Mermaid(mgraph=html_mgraph.mgraph, config=config)
            mermaid_str = exporter.export()
            stats       = self.get_stats(html_mgraph)

            return { 'mermaid'      : mermaid_str          ,
                     'mermaid_size' : len(mermaid_str)     ,
                     'stats'        : stats.json()         ,
                     'duration'     : duration.seconds     ,
                     'format'       : 'mermaid'            }
