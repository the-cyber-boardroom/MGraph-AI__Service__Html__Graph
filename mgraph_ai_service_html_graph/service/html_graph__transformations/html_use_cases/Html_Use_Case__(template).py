# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Graph Transformation Base Class
# v0.3.0 - Updated for multi-graph architecture
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                      import Dict, Any
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                import Html_MGraph


class Html_Use_Case__1(Graph_Transformation__Base):

    name        : str = "html-use-case-1"
    label       : str = "Html Use Case #1"
    description : str = "Html Use Case #1"

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 1: Raw HTML Manipulation
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_html(self, html: str) -> str:                                     # Modify raw HTML string before parsing
        return html

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 2: MGraph Transformation
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_mgraph(self, html_mgraph: Html_MGraph) -> Html_MGraph:            # Modify Html_MGraph after creation
        return html_mgraph

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 3: Export Data Manipulation
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_export(self, export_data: Dict[str, Any]) -> Dict[str, Any]:      # Modify exported data before sending to client
        return export_data

    # ═══════════════════════════════════════════════════════════════════════════
    # Metadata
    # ═══════════════════════════════════════════════════════════════════════════

    def to_dict(self) -> Dict[str, str]:                                            # Return transformation metadata
        return dict(name        = self.name       ,
                    label       = self.label      ,
                    description = self.description)