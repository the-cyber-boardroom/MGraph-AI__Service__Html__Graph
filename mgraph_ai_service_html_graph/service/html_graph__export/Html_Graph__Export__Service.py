# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Export Service (v3)
# Updated for multi-graph architecture (Html_MGraph facade)
#
# Supports: DOT, vis.js, D3.js, Cytoscape.js, Mermaid, Tree, Tree Text
# Transformations: default, collapse_text, elements_only, body_only
# ═══════════════════════════════════════════════════════════════════════════════

from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__Cytoscape             import Html_MGraph__To__Cytoscape
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__D3                    import Html_MGraph__To__D3
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__Mermaid               import Html_MGraph__To__Mermaid
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__VisJs                 import Html_MGraph__To__VisJs
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__Tree_View             import Html_MGraph__To__Tree_View
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                   import Html_MGraph
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__To__Dot               import Html_MGraph__To__Dot
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config                   import Html_MGraph__Render__Config
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors                   import Html_MGraph__Render__Colors
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Labels                   import Html_MGraph__Render__Labels
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Registry import transformation_registry
from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Html__Request                  import Schema__Graph__From_Html__Request
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Dot__Response                        import Schema__Graph__Dot__Response
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Stats                                import Schema__Graph__Stats
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.helpers.duration.decorators.capture_duration                                       import capture_duration


class Html_Graph__Export__Service(Type_Safe):                                             # Unified export service with transformation support

    # ═══════════════════════════════════════════════════════════════════════════
    # Transformation Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def list_transformations(self) -> list:                                               # Get available transformations
        """Return list of all available transformations with metadata."""
        return transformation_registry.list_all()

    def html_to_mgraph_with_transformation(self,
                                           html: str,
                                           transformation_name: str = "default",
                                           config: Html_MGraph__Render__Config = None
                                           ) -> Html_MGraph:                              # Full transformation pipeline
        """Execute the transformation pipeline."""
        transformation = transformation_registry.get(transformation_name)

        # Phase 1: Transform HTML
        html = transformation.transform_html(html)

        # Phase 2: Create Html_MGraph
        html_mgraph = Html_MGraph.from_html(html)

        # Phase 3: Transform MGraph
        html_mgraph = transformation.transform_mgraph(html_mgraph)

        return html_mgraph

    def apply_export_transformation(self, export_data: dict,
                                    transformation_name: str = "default") -> dict:        # Phase 5: Transform export data
        """Apply transformation to export data."""
        transformation = transformation_registry.get(transformation_name)
        return transformation.transform_export(export_data)

    # ═══════════════════════════════════════════════════════════════════════════
    # Core Conversion Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def html_to_mgraph(self, html: str) -> Html_MGraph:                                   # Convert HTML string to Html_MGraph (no transformation)
        return Html_MGraph.from_html(html)

    def create_config(self, request: Schema__Graph__From_Html__Request                    # Create render config from request
                      ) -> Html_MGraph__Render__Config:
        colors = Html_MGraph__Render__Colors()
        labels = Html_MGraph__Render__Labels()
        config = Html_MGraph__Render__Config(colors=colors, labels=labels)

        config.apply_preset(request.preset)                                               # Apply preset
        config.show_tag_nodes  = request.show_tag_nodes                                   # Node visibility
        config.show_attr_nodes = request.show_attr_nodes
        config.show_text_nodes = request.show_text_nodes
        config.show_tag_edges  = request.show_tag_nodes                                   # Edge visibility follows nodes
        config.show_attr_edges = request.show_attr_nodes
        config.show_text_edges = request.show_text_nodes
        config.set_color_scheme(request.color_scheme)                                     # Color scheme

        return config

    def get_stats(self, html_mgraph: Html_MGraph) -> Schema__Graph__Stats:                # Extract graph statistics
        stats = html_mgraph.stats()

        # Map from new Schema__Html_MGraph__Stats__Document to Schema__Graph__Stats
        total_nodes   = 0
        total_edges   = 0
        element_nodes = 0
        tag_nodes     = 0
        text_nodes    = 0
        attr_nodes    = 0

        if stats.document:
            total_nodes += stats.document.total_nodes
            total_edges += stats.document.total_edges

        if stats.head:
            total_nodes   += stats.head.total_nodes
            total_edges   += stats.head.total_edges
            element_nodes += stats.head.element_nodes
            text_nodes    += stats.head.text_nodes

        if stats.body:
            total_nodes   += stats.body.total_nodes
            total_edges   += stats.body.total_edges
            element_nodes += stats.body.element_nodes
            text_nodes    += stats.body.text_nodes

        if stats.attributes:
            total_nodes += stats.attributes.total_nodes
            total_edges += stats.attributes.total_edges
            tag_nodes   += stats.attributes.unique_tags
            attr_nodes  += stats.attributes.total_attributes

        if stats.scripts:
            total_nodes += stats.scripts.total_nodes
            total_edges += stats.scripts.total_edges

        if stats.styles:
            total_nodes += stats.styles.total_nodes
            total_edges += stats.styles.total_edges

        return Schema__Graph__Stats(total_nodes   = total_nodes   ,
                                    total_edges   = total_edges   ,
                                    element_nodes = element_nodes ,
                                    value_nodes   = text_nodes    ,
                                    tag_nodes     = tag_nodes     ,
                                    text_nodes    = text_nodes    ,
                                    attr_nodes    = attr_nodes    )

    # ═══════════════════════════════════════════════════════════════════════════
    # DOT Export
    # ═══════════════════════════════════════════════════════════════════════════

    def to_dot(self, request: Schema__Graph__From_Html__Request,
               transformation: str = "default") -> Schema__Graph__Dot__Response:
        with capture_duration() as duration:
            config      = self.create_config(request)
            html_mgraph = self.html_to_mgraph_with_transformation(request.html, transformation, config)
            exporter    = Html_MGraph__To__Dot()
            dot_string  = exporter.convert(html_mgraph)
            stats       = self.get_stats(html_mgraph)

        return Schema__Graph__Dot__Response(dot           = dot_string           ,
                                            dot_size      = len(dot_string)      ,
                                            duration      = duration.seconds     ,
                                            stats         = stats                ,
                                            transformation = transformation      )

    # ═══════════════════════════════════════════════════════════════════════════
    # vis.js Export
    # ═══════════════════════════════════════════════════════════════════════════

    def to_visjs(self, request: Schema__Graph__From_Html__Request,
                 transformation: str = "default") -> dict:
        with capture_duration() as duration:
            config      = self.create_config(request)
            html_mgraph = self.html_to_mgraph_with_transformation(request.html, transformation, config)
            exporter    = Html_MGraph__To__VisJs(html_mgraph=html_mgraph, config=config)
            data        = exporter.export()
            stats       = self.get_stats(html_mgraph)

        result = { 'nodes'          : data['nodes']        ,
                   'edges'          : data['edges']        ,
                   'rootId'         : data.get('rootId')   ,
                   'stats'          : stats.json()         ,
                   'duration'       : duration.seconds     ,
                   'format'         : 'visjs'              ,
                   'transformation' : transformation       }

        return self.apply_export_transformation(result, transformation)

    # ═══════════════════════════════════════════════════════════════════════════
    # D3.js Export
    # ═══════════════════════════════════════════════════════════════════════════

    def to_d3(self, request: Schema__Graph__From_Html__Request,
              transformation: str = "default") -> dict:
        with capture_duration() as duration:
            config      = self.create_config(request)
            html_mgraph = self.html_to_mgraph_with_transformation(request.html, transformation, config)
            exporter    = Html_MGraph__To__D3(html_mgraph=html_mgraph, config=config)
            data        = exporter.export()
            stats       = self.get_stats(html_mgraph)

        result = { 'nodes'          : data['nodes']        ,
                   'links'          : data['links']        ,
                   'rootId'         : data.get('rootId')   ,
                   'stats'          : stats.json()         ,
                   'duration'       : duration.seconds     ,
                   'format'         : 'd3'                 ,
                   'transformation' : transformation       }

        return self.apply_export_transformation(result, transformation)

    # ═══════════════════════════════════════════════════════════════════════════
    # Cytoscape.js Export
    # ═══════════════════════════════════════════════════════════════════════════

    def to_cytoscape(self, request: Schema__Graph__From_Html__Request,
                     transformation: str = "default") -> dict:
        with capture_duration() as duration:
            config      = self.create_config(request)
            html_mgraph = self.html_to_mgraph_with_transformation(request.html, transformation, config)
            exporter    = Html_MGraph__To__Cytoscape(html_mgraph=html_mgraph, config=config)
            data        = exporter.export()
            stats       = self.get_stats(html_mgraph)

        result = { 'elements'       : data['elements']     ,
                   'rootId'         : data.get('rootId')   ,
                   'stats'          : stats.json()         ,
                   'duration'       : duration.seconds     ,
                   'format'         : 'cytoscape'          ,
                   'transformation' : transformation       }

        return self.apply_export_transformation(result, transformation)

    # ═══════════════════════════════════════════════════════════════════════════
    # Mermaid Export
    # ═══════════════════════════════════════════════════════════════════════════

    def to_mermaid(self, request: Schema__Graph__From_Html__Request,
                   transformation: str = "default") -> dict:
        with capture_duration() as duration:
            config      = self.create_config(request)
            html_mgraph = self.html_to_mgraph_with_transformation(request.html, transformation, config)
            exporter    = Html_MGraph__To__Mermaid(html_mgraph=html_mgraph, config=config)
            mermaid_str = exporter.export()
            stats       = self.get_stats(html_mgraph)

        result = { 'mermaid'        : mermaid_str          ,
                   'mermaid_size'   : len(mermaid_str)     ,
                   'stats'          : stats.json()         ,
                   'duration'       : duration.seconds     ,
                   'format'         : 'mermaid'            ,
                   'transformation' : transformation       }

        return self.apply_export_transformation(result, transformation)

    # ═══════════════════════════════════════════════════════════════════════════
    # Tree Export (JSON structure)
    # ═══════════════════════════════════════════════════════════════════════════

    def to_tree(self, request: Schema__Graph__From_Html__Request,
                transformation: str = "default") -> dict:
        with capture_duration() as duration:
            config      = self.create_config(request)
            html_mgraph = self.html_to_mgraph_with_transformation(request.html, transformation, config)
            exporter    = Html_MGraph__To__Tree_View(html_mgraph=html_mgraph, config=config)
            tree_data   = exporter.export_tree()
            stats       = self.get_stats(html_mgraph)
            root_id     = str(html_mgraph.root_id()) if html_mgraph.root_id() else None

        result = { 'tree'           : tree_data            ,
                   'rootId'         : root_id              ,
                   'stats'          : stats.json()         ,
                   'duration'       : duration.seconds     ,
                   'format'         : 'tree'               ,
                   'transformation' : transformation       }

        return self.apply_export_transformation(result, transformation)

    # ═══════════════════════════════════════════════════════════════════════════
    # Tree Text Export (formatted string)
    # ═══════════════════════════════════════════════════════════════════════════

    def to_tree_text(self, request: Schema__Graph__From_Html__Request,
                     transformation: str = "default") -> dict:
        with capture_duration() as duration:
            config      = self.create_config(request)
            html_mgraph = self.html_to_mgraph_with_transformation(request.html, transformation, config)
            exporter    = Html_MGraph__To__Tree_View(html_mgraph=html_mgraph, config=config)
            tree_text   = exporter.export_tree__as_text()
            stats       = self.get_stats(html_mgraph)
            root_id     = str(html_mgraph.root_id()) if html_mgraph.root_id() else None

        result = { 'tree_text'      : tree_text            ,
                   'tree_text_size' : len(tree_text)       ,
                   'rootId'         : root_id              ,
                   'stats'          : stats.json()         ,
                   'duration'       : duration.seconds     ,
                   'format'         : 'tree_text'          ,
                   'transformation' : transformation       }

        return self.apply_export_transformation(result, transformation)