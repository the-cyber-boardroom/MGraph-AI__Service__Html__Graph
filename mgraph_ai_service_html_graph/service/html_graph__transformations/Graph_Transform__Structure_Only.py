# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Structure Only Transformation
# v0.3.0 - Page structure view without text content
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                      import Dict, Any
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base


class Graph_Transform__Structure_Only(Graph_Transformation__Base):
    """Show page structure without text content.

    Creates a clean structural view showing:
        - Element hierarchy (html → body → div → p)
        - No text nodes
        - No attribute values (optional: keep attribute names)

    Ideal for:
        - D3 force-directed graphs (less clutter)
        - Understanding page layout
        - Comparing page structures
    """

    name        : str = "structure_only"
    label       : str = "Structure Only"
    description : str = "Page structure without text content - ideal for D3 visualization"

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 3: Transform Export - Remove text nodes, simplify
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_export(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter export to show only structural elements."""

        # For formats with nodes array (vis.js, D3)
        if 'nodes' in export_data:
            export_data['nodes'] = [
                self._simplify_node(node) for node in export_data['nodes']
                if node.get('nodeType') == 'element'                                # Only element nodes
            ]

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

        # For Cytoscape format
        if 'elements' in export_data:
            elements = export_data['elements']
            if 'nodes' in elements:
                elements['nodes'] = [
                    self._simplify_cytoscape_node(node) for node in elements['nodes']
                    if node.get('data', {}).get('nodeType') == 'element'
                ]

                node_ids = {node.get('data', {}).get('id') for node in elements['nodes']}

                if 'edges' in elements:
                    elements['edges'] = [
                        edge for edge in elements['edges']
                        if edge.get('data', {}).get('source') in node_ids
                        and edge.get('data', {}).get('target') in node_ids
                    ]

        # For tree format
        if 'tree' in export_data:
            export_data['tree'] = self._simplify_tree(export_data['tree'])

        return export_data

    def _simplify_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify node for cleaner visualization."""
        return {
            'id'          : node.get('id')                    ,
            'label'       : node.get('tag', node.get('label')),                     # Use tag name as label
            'nodeType'    : 'element'                         ,
            'tag'         : node.get('tag')                   ,
            'graph_source': node.get('graph_source')          ,
            'depth'       : node.get('depth', 0)              ,
            'color'       : node.get('color')                 ,
            'shape'       : node.get('shape', 'box')          ,
        }

    def _simplify_cytoscape_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify Cytoscape node format."""
        data = node.get('data', {})
        return {
            'data': {
                'id'          : data.get('id')                      ,
                'label'       : data.get('tag', data.get('label'))  ,
                'nodeType'    : 'element'                           ,
                'tag'         : data.get('tag')                     ,
                'graph_source': data.get('graph_source')            ,
            }
        }

    def _simplify_tree(self, tree_node: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify tree structure - remove text, keep structure."""
        if not tree_node:
            return tree_node

        result = {
            'id'      : tree_node.get('id')                        ,
            'value'   : tree_node.get('tag', tree_node.get('value')),
            'type'    : 'element'                                  ,
            'children': []                                         ,
        }

        # Only include element children (not text/attr)
        for child in tree_node.get('children', []):
            if type(child) is dict:                                 # todo: review why we need this
                if child.get('type') == 'element' or child.get('nodeType') == 'element':
                    result['children'].append(self._simplify_tree(child))

        return result