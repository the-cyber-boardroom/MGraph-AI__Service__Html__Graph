# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Body Only Transformation
# v0.2.5 - Show only content inside <body>, skip <head> and metadata
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                      import Dict, Any, Optional
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base


class Graph_Transformation__Body_Only(Graph_Transformation__Base):
    """Extract and show only the <body> content of an HTML document.
    
    Filters out:
        - <head> and its children (meta, title, link, script, style)
        - DOCTYPE declarations
        - Comments outside body
        
    Useful for focusing on visible page content.
    """
    
    name        : str = "body_only"
    label       : str = "Body Only"
    description : str = "Show only body content, hiding head and metadata"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 2: Transform Dict - Extract body element
    # ═══════════════════════════════════════════════════════════════════════════
    
    def transform_dict(self, html_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Find and return only the body element subtree."""
        body = self._find_body(html_dict)
        if body:
            return body
        return html_dict                                                            # Fallback to full dict if no body found
    
    def _find_body(self, node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Recursively search for <body> element."""
        if not isinstance(node, dict):
            return None
        
        tag = node.get('tag', '').lower()
        
        # Found body
        if tag == 'body':
            return node
        
        # Search children
        for child in node.get('child_nodes', []):
            result = self._find_body(child)
            if result:
                return result
        
        return None
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 5: Transform Export - Update root reference
    # ═══════════════════════════════════════════════════════════════════════════
    
    def transform_export(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure export reflects body as root."""
        # The dict transformation already handles this by returning body subtree
        # Export will naturally have body as the root node
        return export_data
