from typing                                                                                         import Any, Optional
from mgraph_db.mgraph.MGraph                                                                        import MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base    import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                   import Html_MGraph
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Dot       import MGraph__Engine__Config__Dot
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__D3        import MGraph__Engine__Config__D3
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Cytoscape import MGraph__Engine__Config__Cytoscape
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__VisJs     import MGraph__Engine__Config__VisJs
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Mermaid   import MGraph__Engine__Config__Mermaid
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Tree      import MGraph__Engine__Config__Tree


class Html_Use_Case__1(Graph_Transformation__Base):

    name        : str = "html-use-case-1"
    label       : str = "Html Use Case #1"
    description : str = "Html Use Case #1"

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 1: HTML → Html_MGraph
    # ═══════════════════════════════════════════════════════════════════════════

    def html__to__html_mgraph(self, html: str) -> Html_MGraph:
        return super().html__to__html_mgraph(html)                                  # Default: use Html_MGraph parser

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 2: Html_MGraph → MGraph
    # ═══════════════════════════════════════════════════════════════════════════

    def html_mgraph__to__mgraph(self, html_mgraph: Html_MGraph) -> MGraph:
        return super().html_mgraph__to__mgraph(html_mgraph)                         # Default: use body graph

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 3: MGraph → MGraph (transformation)
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_mgraph(self, mgraph: MGraph) -> MGraph:
        return mgraph                                                               # Default: no-op passthrough

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 4: Engine Configuration Callbacks
    # ═══════════════════════════════════════════════════════════════════════════

    def configure_dot(self, config: MGraph__Engine__Config__Dot) -> MGraph__Engine__Config__Dot:
        return config

    def configure_d3(self, config: MGraph__Engine__Config__D3) -> MGraph__Engine__Config__D3:
        return config

    def configure_cytoscape(self, config: MGraph__Engine__Config__Cytoscape) -> MGraph__Engine__Config__Cytoscape:
        return config

    def configure_visjs(self, config: MGraph__Engine__Config__VisJs) -> MGraph__Engine__Config__VisJs:
        return config

    def configure_mermaid(self, config: MGraph__Engine__Config__Mermaid) -> MGraph__Engine__Config__Mermaid:
        return config

    def configure_tree(self, config: MGraph__Engine__Config__Tree) -> MGraph__Engine__Config__Tree:
        return config

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 5: Output Transformation
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_export(self, output: Any) -> Any:
        #print(output)
        return output                                                               # Default: no-op passthrough