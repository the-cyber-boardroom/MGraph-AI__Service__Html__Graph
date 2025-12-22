# Graph Transformation Base
#
# Base class for all HTML graph transformations. Implements the 4-phase pipeline:
#   Phase 1: html__to__html_mgraph(html) → Html_MGraph
#   Phase 2: html_mgraph__to__mgraph(Html_MGraph) → MGraph
#   Phase 3: transform_mgraph(MGraph) → MGraph
#   Phase 4: configure_<engine>(config) callbacks
#   Phase 5: transform_export(output) → output

from typing                                                                                         import Any, Optional

from mgraph_db.mgraph.MGraph import MGraph
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Dot       import MGraph__Engine__Config__Dot
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__D3        import MGraph__Engine__Config__D3
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Cytoscape import MGraph__Engine__Config__Cytoscape
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__VisJs     import MGraph__Engine__Config__VisJs
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Mermaid   import MGraph__Engine__Config__Mermaid
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Tree      import MGraph__Engine__Config__Tree
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                   import Html_MGraph
from osbot_utils.type_safe.type_safe_core.decorators.type_safe import type_safe


class Graph_Transformation__Base(Type_Safe):                                             # Base transformation for HTML graphs

    name        : str = 'default'                                                        # Transformation identifier
    label       : str = 'Default'                                                        # Human-readable label
    description : str = 'Standard body graph visualization'                              # Description

    # ═══════════════════════════════════════════════════════════════════════════════════
    # Phase 1: HTML → Html_MGraph
    # ═══════════════════════════════════════════════════════════════════════════════════

    def html__to__html_mgraph(self, html: str):                                          # Convert HTML to Html_MGraph
        return Html_MGraph.from_html(html)                                               # Default: use Html_MGraph parser

    # ═══════════════════════════════════════════════════════════════════════════════════
    # Phase 2: Html_MGraph → MGraph
    # ═══════════════════════════════════════════════════════════════════════════════════

    @type_safe
    def html_mgraph__to__mgraph(self,                                               # Select which graph to render
                                html_mgraph: Html_MGraph
                                ) -> MGraph:
        body_graph = html_mgraph.body_graph                                         # Use body graph by default
        if body_graph:
            return body_graph.mgraph
        return None


    # ═══════════════════════════════════════════════════════════════════════════════════
    # Phase 3: MGraph → MGraph (transformation)
    # ═══════════════════════════════════════════════════════════════════════════════════

    def transform_mgraph(self, mgraph):                                                  # Transform the graph
        return mgraph                                                                    # Default: no-op passthrough

    # ═══════════════════════════════════════════════════════════════════════════════════
    # Phase 4: Engine Configuration Callbacks
    # ═══════════════════════════════════════════════════════════════════════════════════

    def configure_dot(self, config: MGraph__Engine__Config__Dot                          # Configure DOT engine
                     ) -> MGraph__Engine__Config__Dot:
        return config                                                                    # Default: no changes

    def configure_d3(self, config: MGraph__Engine__Config__D3                            # Configure D3 engine
                    ) -> MGraph__Engine__Config__D3:
        return config

    def configure_cytoscape(self, config: MGraph__Engine__Config__Cytoscape              # Configure Cytoscape engine
                           ) -> MGraph__Engine__Config__Cytoscape:
        return config

    def configure_visjs(self, config: MGraph__Engine__Config__VisJs                      # Configure VisJs engine
                       ) -> MGraph__Engine__Config__VisJs:
        return config

    def configure_mermaid(self, config: MGraph__Engine__Config__Mermaid                  # Configure Mermaid engine
                         ) -> MGraph__Engine__Config__Mermaid:
        return config

    def configure_tree(self, config: MGraph__Engine__Config__Tree                        # Configure Tree engine
                      ) -> MGraph__Engine__Config__Tree:
        return config

    # ═══════════════════════════════════════════════════════════════════════════════════
    # Phase 5: Output Transformation
    # ═══════════════════════════════════════════════════════════════════════════════════

    def transform_export(self, output: Any) -> Any:                                      # Post-process export output
        return output                                                                    # Default: no-op passthrough
