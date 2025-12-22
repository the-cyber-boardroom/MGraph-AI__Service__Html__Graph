# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Graph Transformation Base Class
# v0.3.0 - Updated for multi-graph architecture
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                       import Dict, Any
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph import Html_MGraph
from osbot_utils.type_safe.Type_Safe                              import Type_Safe


class Graph_Transformation__Base(Type_Safe):
    """Base class for all graph transformations.

    Override any phase method to customize that step.
    Default implementation passes through unchanged.

    Pipeline:
        HTML String
            → Phase 1: transform_html()
        Html_MGraph (multi-graph)
            → Phase 2: transform_mgraph()
        Export data
            → Phase 3: transform_export()
        Response
    """

    name        : str = "default"
    label       : str = "Default"
    description : str = "Standard HTML to MGraph conversion with full detail"

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 1: Raw HTML Manipulation
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_html(self, html: str) -> str:                                     # Modify raw HTML string before parsing
        """Override to manipulate raw HTML before parsing.

        Use cases:
            - Remove script/style tags
            - Inject wrapper elements
            - Normalize whitespace
        """
        return html

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 2: MGraph Transformation
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_mgraph(self, html_mgraph: Html_MGraph) -> Html_MGraph:            # Modify Html_MGraph after creation
        """Override to manipulate the Html_MGraph graph structure.

        The Html_MGraph contains multiple sub-graphs:
            - document: Root document structure
            - head_graph: Head element content
            - body_graph: Body element content
            - attrs_graph: All attributes
            - scripts_graph: Script elements
            - styles_graph: Style elements

        Use cases:
            - Collapse nodes
            - Filter by depth
            - Add computed properties
            - Merge related nodes
            - Filter specific sub-graphs
        """
        return html_mgraph

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 3: Export Data Manipulation
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_export(self, export_data: Dict[str, Any]) -> Dict[str, Any]:      # Modify exported data before sending to client
        """Override to manipulate final export data.

        Use cases:
            - Add custom metadata
            - Filter output fields
            - Post-process colors/labels
        """
        return export_data

    # ═══════════════════════════════════════════════════════════════════════════
    # Metadata
    # ═══════════════════════════════════════════════════════════════════════════

    def to_dict(self) -> Dict[str, str]:                                            # Return transformation metadata
        return dict(name        = self.name       ,
                    label       = self.label      ,
                    description = self.description)