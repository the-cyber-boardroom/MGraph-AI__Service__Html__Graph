# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Graph Transformation Base Class
# v0.2.5 - Phase-based transformation pipeline
# ═══════════════════════════════════════════════════════════════════════════════

from typing                          import Dict, Any

from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph import Html_MGraph
from osbot_utils.type_safe.Type_Safe import Type_Safe


class Graph_Transformation__Base(Type_Safe):
    """Base class for all graph transformations.
    
    Override any phase method to customize that step.
    Default implementation passes through unchanged.
    
    Pipeline:
        HTML String
            → Phase 1: transform_html()
        Html_Dict  
            → Phase 2: transform_dict()
        Html_MGraph creation
            → Phase 3: create_mgraph()
        Html_MGraph
            → Phase 4: transform_mgraph()
        Export data
            → Phase 5: transform_export()
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
    # Phase 2: Html_Dict Manipulation
    # ═══════════════════════════════════════════════════════════════════════════
    
    def transform_dict(self, html_dict: Dict[str, Any]) -> Dict[str, Any]:          # Modify parsed HTML dict before MGraph creation
        """Override to manipulate Html_Dict structure.
        
        Use cases:
            - Filter attributes
            - Remove certain tag types
            - Restructure child relationships
        """
        return html_dict
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 3: MGraph Creation
    # ═══════════════════════════════════════════════════════════════════════════
    
    def create_mgraph(self, html_dict: Dict[str, Any], config: Any):                # Create Html_MGraph from dict
        """Override for completely custom MGraph creation.
        
        Default uses Html_MGraph.from_html_dict().
        
        Use cases:
            - Custom node types
            - Alternative graph structures
            - Specialized indexing
        """

        return Html_MGraph.from_html_dict(html_dict)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 4: MGraph Transformation
    # ═══════════════════════════════════════════════════════════════════════════
    
    def transform_mgraph(self, html_mgraph):                                        # Modify Html_MGraph after creation
        """Override to manipulate the Html_MGraph graph structure.
        
        Use cases:
            - Collapse nodes
            - Filter by depth
            - Add computed properties
            - Merge related nodes
        """
        return html_mgraph
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 5: Export Data Manipulation
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
