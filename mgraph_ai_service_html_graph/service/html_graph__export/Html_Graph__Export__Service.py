# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Export Service
# v0.2.5 - Unified service with transformation pipeline support
#
# Supports: DOT, vis.js, D3.js, Cytoscape.js, Mermaid
# Transformations: default, collapse_text, elements_only, body_only
# ═══════════════════════════════════════════════════════════════════════════════
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__Cytoscape import Html_MGraph__To__Cytoscape
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__D3 import Html_MGraph__To__D3
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__Mermaid import Html_MGraph__To__Mermaid
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__VisJs import Html_MGraph__To__VisJs
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Registry import transformation_registry
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



class Html_Graph__Export__Service(Type_Safe):                                           # Unified export service with transformation support

    # ═══════════════════════════════════════════════════════════════════════════
    # Transformation Pipeline
    # ═══════════════════════════════════════════════════════════════════════════

    def html_to_mgraph_with_transformation(self, html: str, 
                                           transformation_name: str = "default",
                                           config = None) -> Html_MGraph:               # Full transformation pipeline
        """Execute the 5-phase transformation pipeline.
        
        Phase 1: transform_html()   - Modify raw HTML string
        Phase 2: transform_dict()   - Modify parsed Html_Dict
        Phase 3: create_mgraph()    - Create Html_MGraph (custom or default)
        Phase 4: transform_mgraph() - Modify the MGraph structure
        """
        transformation = transformation_registry.get(transformation_name)
        
        # Phase 1: Transform raw HTML
        html = transformation.transform_html(html)
        
        # Parse HTML to dict
        html_dict__osbot = Html__To__Html_Dict(html=html).convert()
        html_dict        = Html_Dict__OSBot__To__Html_Dict().convert(html_dict__osbot)
        
        # Phase 2: Transform dict
        html_dict = transformation.transform_dict(html_dict)
        
        # Phase 3: Create MGraph (transformation can override)
        html_mgraph = transformation.create_mgraph(html_dict, config)
        
        # Phase 4: Transform MGraph
        html_mgraph = transformation.transform_mgraph(html_mgraph)
        
        return html_mgraph

    def apply_export_transformation(self, export_data: dict, 
                                    transformation_name: str = "default") -> dict:      # Phase 5: Transform export data
        """Apply Phase 5 transformation to export data."""
        transformation = transformation_registry.get(transformation_name)
        return transformation.transform_export(export_data)

    def list_transformations(self) -> list:                                             # Get available transformations
        """Return list of all available transformations with metadata."""
        return transformation_registry.list_all()

    # ═══════════════════════════════════════════════════════════════════════════
    # Core Conversion Methods (legacy - no transformation)
    # ═══════════════════════════════════════════════════════════════════════════

    def html_to_mgraph(self, html: str) -> Html_MGraph:                                 # Convert HTML string to Html_MGraph (no transformation)
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
    # DOT Export
    # ═══════════════════════════════════════════════════════════════════════════

    def to_dot(self, request: Schema__Graph__From_Html__Request, 
               transformation: str = "default") -> Schema__Graph__Dot__Response:
        with capture_duration() as duration:
            config      = self.create_config(request)
            html_mgraph = self.html_to_mgraph_with_transformation(request.html, transformation, config)
            exporter    = Html_MGraph__To__Dot(mgraph=html_mgraph.mgraph, config=config)
            dot_string  = exporter.to_string()
            stats       = self.get_stats(html_mgraph)

            result = Schema__Graph__Dot__Response(dot            = dot_string           ,
                                                  stats          = stats                ,
                                                  dot_size       = len(dot_string)      ,
                                                  duration       = duration.seconds     ,
                                                  transformation = transformation       )
            return result

    # ═══════════════════════════════════════════════════════════════════════════
    # vis.js Export
    # ═══════════════════════════════════════════════════════════════════════════

    def to_visjs(self, request: Schema__Graph__From_Html__Request,
                 transformation: str = "default") -> dict:
        with capture_duration() as duration:
            config      = self.create_config(request)
            html_mgraph = self.html_to_mgraph_with_transformation(request.html, transformation, config)
            exporter    = Html_MGraph__To__VisJs(mgraph=html_mgraph.mgraph, config=config)
            data        = exporter.export()
            stats       = self.get_stats(html_mgraph)

            result = { 'nodes'          : data['nodes']       ,
                       'edges'          : data['edges']       ,
                       'rootId'         : data.get('rootId')  ,
                       'stats'          : stats.json()        ,
                       'duration'       : duration.seconds    ,
                       'format'         : 'visjs'             ,
                       'transformation' : transformation      }
            
            return self.apply_export_transformation(result, transformation)

    # ═══════════════════════════════════════════════════════════════════════════
    # D3.js Export
    # ═══════════════════════════════════════════════════════════════════════════

    def to_d3(self, request: Schema__Graph__From_Html__Request,
              transformation: str = "default") -> dict:
        with capture_duration() as duration:
            config      = self.create_config(request)
            html_mgraph = self.html_to_mgraph_with_transformation(request.html, transformation, config)
            exporter    = Html_MGraph__To__D3(mgraph=html_mgraph.mgraph, config=config)
            data        = exporter.export()
            stats       = self.get_stats(html_mgraph)

            result = { 'nodes'          : data['nodes']       ,
                       'links'          : data['links']       ,
                       'rootId'         : data.get('rootId')  ,
                       'stats'          : stats.json()        ,
                       'duration'       : duration.seconds    ,
                       'format'         : 'd3'                ,
                       'transformation' : transformation      }
            
            return self.apply_export_transformation(result, transformation)

    # ═══════════════════════════════════════════════════════════════════════════
    # Cytoscape.js Export
    # ═══════════════════════════════════════════════════════════════════════════

    def to_cytoscape(self, request: Schema__Graph__From_Html__Request,
                     transformation: str = "default") -> dict:
        with capture_duration() as duration:
            config      = self.create_config(request)
            html_mgraph = self.html_to_mgraph_with_transformation(request.html, transformation, config)
            exporter    = Html_MGraph__To__Cytoscape(mgraph=html_mgraph.mgraph, config=config)
            data        = exporter.export()
            stats       = self.get_stats(html_mgraph)

            result = { 'elements'       : data['elements']    ,
                       'rootId'         : data.get('rootId')  ,
                       'stats'          : stats.json()        ,
                       'duration'       : duration.seconds    ,
                       'format'         : 'cytoscape'         ,
                       'transformation' : transformation      }
            
            return self.apply_export_transformation(result, transformation)

    # ═══════════════════════════════════════════════════════════════════════════
    # Mermaid Export
    # ═══════════════════════════════════════════════════════════════════════════

    def to_mermaid(self, request: Schema__Graph__From_Html__Request,
                   transformation: str = "default") -> dict:
        with capture_duration() as duration:
            config      = self.create_config(request)
            html_mgraph = self.html_to_mgraph_with_transformation(request.html, transformation, config)
            exporter    = Html_MGraph__To__Mermaid(mgraph=html_mgraph.mgraph, config=config)
            mermaid_str = exporter.export()
            stats       = self.get_stats(html_mgraph)

            result = { 'mermaid'        : mermaid_str          ,
                       'mermaid_size'   : len(mermaid_str)     ,
                       'stats'          : stats.json()         ,
                       'duration'       : duration.seconds     ,
                       'format'         : 'mermaid'            ,
                       'transformation' : transformation       }
            
            return self.apply_export_transformation(result, transformation)
