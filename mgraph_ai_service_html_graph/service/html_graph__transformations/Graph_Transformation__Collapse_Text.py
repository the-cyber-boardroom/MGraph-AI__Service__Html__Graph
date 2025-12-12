# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Collapse Text Transformation
# v0.2.5 - Merge text content into parent element labels
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                      import Dict, Any
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base


class Graph_Transformation__Collapse_Text(Graph_Transformation__Base):
    """Collapse text nodes into their parent element's label.
    
    Instead of:
        <div> ──[text]──► "Hello World"
        
    Shows:
        <div>: Hello World
        
    Useful for seeing text content without separate text nodes.
    """
    
    name        : str = "collapse_text"
    label       : str = "Collapse Text"
    description : str = "Text content merged into parent element labels"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 2: Transform Dict - Remove text_nodes, merge into element
    # ═══════════════════════════════════════════════════════════════════════════
    
    def transform_dict(self, html_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Remove text_nodes from dict, appending text to element labels."""
        return self._collapse_text_recursive(html_dict)
    
    def _collapse_text_recursive(self, node: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(node, dict):
            return node
        
        result = dict(node)                                                         # Copy node
        
        # Extract text content
        text_content = ""
        if 'text_nodes' in result:
            texts = [tn.get('data', '') for tn in result.get('text_nodes', []) if isinstance(tn, dict)]
            text_content = ' '.join(t.strip() for t in texts if t.strip())
            result['text_nodes'] = []                                               # Clear text nodes
        
        # Store collapsed text for label generation
        if text_content:
            result['_collapsed_text'] = text_content
        
        # Recurse into children
        if 'child_nodes' in result:
            result['child_nodes'] = [
                self._collapse_text_recursive(child) 
                for child in result.get('child_nodes', [])
            ]
        
        return result
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 5: Transform Export - Update labels with collapsed text
    # ═══════════════════════════════════════════════════════════════════════════
    
    def transform_export(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update node labels to include collapsed text content."""
        # This could be enhanced to modify labels based on _collapsed_text
        # For now, the dict transformation handles the structural change
        return export_data
