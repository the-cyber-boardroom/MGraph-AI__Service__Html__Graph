# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Elements Only Transformation
# v0.2.5 - Show only HTML element hierarchy, hide tags/attrs/text
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                      import Dict, Any
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base


class Graph_Transformation__Elements_Only(Graph_Transformation__Base):
    """Show only HTML elements, hiding tag names, attributes, and text nodes.
    
    Creates a simplified view showing just the element hierarchy:
        html → body → div → p
        
    Useful for understanding document structure without details.
    """
    
    name        : str = "elements_only"
    label       : str = "Elements Only"
    description : str = "Simplified element hierarchy without tags, attrs, or text"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 2: Transform Dict - Strip attrs and text_nodes
    # ═══════════════════════════════════════════════════════════════════════════
    
    def transform_dict(self, html_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Remove attributes and text nodes from the dict structure."""
        return self._simplify_recursive(html_dict)
    
    def _simplify_recursive(self, node: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(node, dict):
            return node
        
        result = {
            'tag'        : node.get('tag', 'unknown'),
            'attrs'      : {},                                                      # Empty attrs
            'child_nodes': [],
            'text_nodes' : [],                                                      # No text nodes
        }
        
        # Preserve position if present
        if 'position' in node:
            result['position'] = node['position']
        
        # Recurse into children
        for child in node.get('child_nodes', []):
            if isinstance(child, dict):
                result['child_nodes'].append(self._simplify_recursive(child))
        
        return result
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 5: Transform Export - Filter node types
    # ═══════════════════════════════════════════════════════════════════════════
    
    def transform_export(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter export to only include element nodes."""
        
        # For vis.js/D3/Cytoscape formats with nodes/edges or nodes/links
        if 'nodes' in export_data:
            export_data['nodes'] = [
                node for node in export_data['nodes']
                if node.get('nodeType') == 'element'
            ]
            
            # Filter edges to only connect remaining nodes
            node_ids = {node.get('id') for node in export_data['nodes']}
            
            if 'edges' in export_data:
                export_data['edges'] = [
                    edge for edge in export_data['edges']
                    if edge.get('from') in node_ids and edge.get('to') in node_ids
                ]
            
            if 'links' in export_data:
                export_data['links'] = [
                    link for link in export_data['links']
                    if link.get('source') in node_ids and link.get('target') in node_ids
                ]
        
        # For Cytoscape format with elements.nodes/elements.edges
        if 'elements' in export_data:
            elements = export_data['elements']
            if 'nodes' in elements:
                elements['nodes'] = [
                    node for node in elements['nodes']
                    if node.get('data', {}).get('nodeType') == 'element'
                ]
                
                node_ids = {node.get('data', {}).get('id') for node in elements['nodes']}
                
                if 'edges' in elements:
                    elements['edges'] = [
                        edge for edge in elements['edges']
                        if edge.get('data', {}).get('source') in node_ids 
                        and edge.get('data', {}).get('target') in node_ids
                    ]
        
        return export_data
