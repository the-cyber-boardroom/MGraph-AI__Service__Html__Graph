# Html Graph Export Service
#
# Unified export service orchestrating the 4-phase pipeline.
# Provides methods to export HTML to various graph formats.
#
# Pipeline Phases:
#   Phase 1: html → Html_MGraph (transformation owns parsing)
#   Phase 2: Html_MGraph → MGraph (transformation selects graph)
#   Phase 3: MGraph → MGraph (transformation filters/styles)
#   Phase 4: MGraph → Output (engine renders with configured config)
#   Phase 5: Output → Output (transformation post-processes)

from typing                                                                                     import Any, Dict, List, Literal, Union

from osbot_utils.helpers.duration.decorators.capture_duration import capture_duration
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base         import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Registry     import transformation_registry
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Schemas        import (
    Schema__Graph__From_Html__Request  ,
    Schema__Graph__Dot__Response       ,
    Schema__Graph__D3__Response        ,
    Schema__Graph__Cytoscape__Response ,
    Schema__Graph__VisJs__Response     ,
    Schema__Graph__Mermaid__Response   ,
    Schema__Graph__Tree__Response      ,
    Schema__Transformations__List__Response,
    Schema__Transformation__Info       ,
    Schema__Engines__List__Response    ,
    Schema__Engine__Info               ,
)
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Dot                           import MGraph__Engine__Dot
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__D3                            import MGraph__Engine__D3
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Cytoscape                     import MGraph__Engine__Cytoscape
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__VisJs                         import MGraph__Engine__VisJs
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Mermaid                       import MGraph__Engine__Mermaid
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Tree                          import MGraph__Engine__Tree
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Dot           import MGraph__Engine__Config__Dot
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__D3            import MGraph__Engine__Config__D3
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Cytoscape     import MGraph__Engine__Config__Cytoscape
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__VisJs         import MGraph__Engine__Config__VisJs
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Mermaid       import MGraph__Engine__Config__Mermaid
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Tree          import MGraph__Engine__Config__Tree


EngineType = Literal['dot', 'd3', 'cytoscape', 'visjs', 'mermaid', 'tree']


class Html_Graph__Export__Service(Type_Safe):                                                   # Unified export service

    # ═══════════════════════════════════════════════════════════════════════════════════════════
    # Engine Registry
    # ═══════════════════════════════════════════════════════════════════════════════════════════

    ENGINES = {                                                                                 # Engine class registry
        'dot'      : MGraph__Engine__Dot      ,
        'd3'       : MGraph__Engine__D3       ,
        'cytoscape': MGraph__Engine__Cytoscape,
        'visjs'    : MGraph__Engine__VisJs    ,
        'mermaid'  : MGraph__Engine__Mermaid  ,
        'tree'     : MGraph__Engine__Tree     ,
    }

    ENGINE_CONFIGS = {                                                                          # Engine config registry
        'dot'      : MGraph__Engine__Config__Dot      ,
        'd3'       : MGraph__Engine__Config__D3       ,
        'cytoscape': MGraph__Engine__Config__Cytoscape,
        'visjs'    : MGraph__Engine__Config__VisJs    ,
        'mermaid'  : MGraph__Engine__Config__Mermaid  ,
        'tree'     : MGraph__Engine__Config__Tree     ,
    }

    CONFIG_METHODS = {                                                                          # Transformation config methods
        'dot'      : 'configure_dot'      ,
        'd3'       : 'configure_d3'       ,
        'cytoscape': 'configure_cytoscape',
        'visjs'    : 'configure_visjs'    ,
        'mermaid'  : 'configure_mermaid'  ,
        'tree'     : 'configure_tree'     ,
    }

    ENGINE_INFO = {                                                                             # Engine descriptions
        'dot'      : ('string', 'Graphviz DOT format for graph visualization'      ),
        'd3'       : ('dict'  , 'D3.js force-directed graph format'                ),
        'cytoscape': ('dict'  , 'Cytoscape.js graph format with styling'           ),
        'visjs'    : ('dict'  , 'vis.js Network hierarchical graph format'         ),
        'mermaid'  : ('string', 'Mermaid diagram syntax for documentation'         ),
        'tree'     : ('any'   , 'Tree view in text, JSON, or nested dict format'   ),
    }

    # ═══════════════════════════════════════════════════════════════════════════════════════════
    # Transformation Registry Access
    # ═══════════════════════════════════════════════════════════════════════════════════════════

    #def list_transformations(self) -> Schema__Transformations__List__Response:                  # List all transformations
    def list_transformations(self)  -> List:
        transforms = transformation_registry.list_all()
        return transforms
        # infos = [Schema__Transformation__Info(name=t['name'], description=t['description'])
        #          for t in transforms]
        #
        #
        # return Schema__Transformations__List__Response(transformations = infos     ,
        #                                                count           = len(infos))


    def list_engines(self) -> Schema__Engines__List__Response:                                  # List all engines
        engines = []
        for name, (output_type, description) in self.ENGINE_INFO.items():
            engines.append(Schema__Engine__Info(
                name        = name       ,
                output_type = output_type,
                description = description,
            ))
        return Schema__Engines__List__Response(
            engines = engines      ,
            count   = len(engines) ,
        )

    def get_transformation(self, name: str) -> Graph_Transformation__Base:                      # Get transformation by name
        return transformation_registry.get(name)

    # ═══════════════════════════════════════════════════════════════════════════════════════════
    # Core Pipeline Execution
    # ═══════════════════════════════════════════════════════════════════════════════════════════

    def execute_pipeline(self, html: str,                                                       # Execute phases 1-3
                               transformation_name: str = 'default'):
        transformation = self.get_transformation(transformation_name)

        html_mgraph = transformation.html__to__html_mgraph(html)                                # Phase 1: HTML → Html_MGraph
        mgraph      = transformation.html_mgraph__to__mgraph(html_mgraph)                       # Phase 2: Html_MGraph → MGraph
        mgraph      = transformation.transform_mgraph(mgraph)                                   # Phase 3: MGraph → MGraph

        return mgraph, transformation

    def render_with_engine(self, mgraph, engine_name: str,                                      # Execute phase 4
                                 transformation: Graph_Transformation__Base) -> Any:

        engine_class  = self.ENGINES.get(engine_name)
        config_class  = self.ENGINE_CONFIGS.get(engine_name)
        config_method = self.CONFIG_METHODS.get(engine_name)

        if not engine_class or not config_class:
            raise ValueError(f"Unknown engine: {engine_name}")

        config = config_class()                                                                 # Create default config

        if config_method and hasattr(transformation, config_method):                            # Apply transformation config
            configure_fn = getattr(transformation, config_method)
            config = configure_fn(config)

        engine = engine_class(mgraph=mgraph, config=config)                                     # Create engine
        output = engine.export()                                                                # Render
        output = transformation.transform_export(output)                                        # Phase 5: Post-process

        return output, engine

    def get_graph_stats(self, engine) -> Dict[str, int]:                                        # Get node/edge counts
        return {
            'node_count': len(engine.nodes()),
            'edge_count': len(engine.edges()),
        }

    # ═══════════════════════════════════════════════════════════════════════════════════════════
    # Engine Export Methods
    # ═══════════════════════════════════════════════════════════════════════════════════════════

    def to_dot(self, request: Schema__Graph__From_Html__Request,                                # Export to DOT format
                     transformation: str = None
              ) -> Schema__Graph__Dot__Response:
        trans_name = transformation or request.transformation or 'default'

        with capture_duration() as duration:
            mgraph, trans = self.execute_pipeline(request.html, trans_name)
            output, engine = self.render_with_engine(mgraph, 'dot', trans)
            stats = self.get_graph_stats(engine)

        return Schema__Graph__Dot__Response(
            dot            = output               ,
            dot_size       = len(output)          ,
            duration       = duration.seconds     ,
            transformation = trans_name           ,
            engine         = 'dot'                ,
            node_count     = stats['node_count']  ,
            edge_count     = stats['edge_count']  ,
        )

    def to_d3(self, request: Schema__Graph__From_Html__Request,                                 # Export to D3.js format
                    transformation: str = None
             ) -> Schema__Graph__D3__Response:
        trans_name = transformation or request.transformation or 'default'

        with capture_duration() as duration:
            mgraph, trans = self.execute_pipeline(request.html, trans_name)
            output, engine = self.render_with_engine(mgraph, 'd3', trans)
            stats = self.get_graph_stats(engine)

        return Schema__Graph__D3__Response(
            nodes          = output.get('nodes' , [])  ,
            links          = output.get('links' , [])  ,
            config         = output.get('config', {})  ,
            duration       = duration.seconds          ,
            transformation = trans_name                ,
            engine         = 'd3'                      ,
            node_count     = stats['node_count']       ,
            edge_count     = stats['edge_count']       ,
        )

    def to_cytoscape(self, request: Schema__Graph__From_Html__Request,                          # Export to Cytoscape.js format
                           transformation: str = None
                    ) -> Schema__Graph__Cytoscape__Response:
        trans_name = transformation or request.transformation or 'default'

        with capture_duration() as duration:
            mgraph, trans = self.execute_pipeline(request.html, trans_name)
            output, engine = self.render_with_engine(mgraph, 'cytoscape', trans)
            stats = self.get_graph_stats(engine)

        return Schema__Graph__Cytoscape__Response(
            elements       = output.get('elements', {'nodes': [], 'edges': []}),
            layout         = output.get('layout'  , {})  ,
            style          = output.get('style'   , [])  ,
            duration       = duration.seconds            ,
            transformation = trans_name                  ,
            engine         = 'cytoscape'                 ,
            node_count     = stats['node_count']         ,
            edge_count     = stats['edge_count']         ,
        )

    def to_visjs(self, request: Schema__Graph__From_Html__Request,                              # Export to vis.js format
                       transformation: str = None
                ) -> Schema__Graph__VisJs__Response:
        trans_name = transformation or request.transformation or 'default'

        with capture_duration() as duration:
            mgraph, trans = self.execute_pipeline(request.html, trans_name)
            output, engine = self.render_with_engine(mgraph, 'visjs', trans)
            stats = self.get_graph_stats(engine)

        return Schema__Graph__VisJs__Response(
            nodes          = output.get('nodes'  , [])  ,
            edges          = output.get('edges'  , [])  ,
            options        = output.get('options', {})  ,
            duration       = duration.seconds           ,
            transformation = trans_name                 ,
            engine         = 'visjs'                    ,
            node_count     = stats['node_count']        ,
            edge_count     = stats['edge_count']        ,
        )

    def to_mermaid(self, request: Schema__Graph__From_Html__Request,                            # Export to Mermaid format
                         transformation: str = None
                  ) -> Schema__Graph__Mermaid__Response:
        trans_name = transformation or request.transformation or 'default'

        with capture_duration() as duration:
            mgraph, trans = self.execute_pipeline(request.html, trans_name)
            output, engine = self.render_with_engine(mgraph, 'mermaid', trans)
            stats = self.get_graph_stats(engine)

        return Schema__Graph__Mermaid__Response(
            mermaid        = output               ,
            mermaid_size   = len(output)          ,
            duration       = duration.seconds     ,
            transformation = trans_name           ,
            engine         = 'mermaid'            ,
            node_count     = stats['node_count']  ,
            edge_count     = stats['edge_count']  ,
        )

    def to_tree(self, request: Schema__Graph__From_Html__Request,                               # Export to Tree format
                      transformation: str = None,
                      output_format: str = 'text'
               ) -> Schema__Graph__Tree__Response:
        trans_name = transformation or request.transformation or 'default'

        with capture_duration() as duration:
            mgraph, trans = self.execute_pipeline(request.html, trans_name)

            config = MGraph__Engine__Config__Tree(output_format=output_format)                  # Set output format
            trans.configure_tree(config)

            engine = MGraph__Engine__Tree(mgraph=mgraph, config=config)
            output = engine.export()
            output = trans.transform_export(output)
            stats  = self.get_graph_stats(engine)

        return Schema__Graph__Tree__Response(
            tree           = output               ,
            output_format  = output_format        ,
            duration       = duration.seconds     ,
            transformation = trans_name           ,
            engine         = 'tree'               ,
            node_count     = stats['node_count']  ,
            edge_count     = stats['edge_count']  ,
        )

    # ═══════════════════════════════════════════════════════════════════════════════════════════
    # Generic Export Method
    # ═══════════════════════════════════════════════════════════════════════════════════════════

    def export(self, html: str,                                                                 # Generic export method
                     engine: EngineType = 'dot',
                     transformation: str = 'default'
              ) -> Any:
        request = Schema__Graph__From_Html__Request(
            html           = html          ,
            transformation = transformation,
        )

        export_methods = {
            'dot'      : self.to_dot      ,
            'd3'       : self.to_d3       ,
            'cytoscape': self.to_cytoscape,
            'visjs'    : self.to_visjs    ,
            'mermaid'  : self.to_mermaid  ,
            'tree'     : self.to_tree     ,
        }

        export_method = export_methods.get(engine)
        if not export_method:
            raise ValueError(f"Unknown engine: {engine}")

        return export_method(request, transformation)
