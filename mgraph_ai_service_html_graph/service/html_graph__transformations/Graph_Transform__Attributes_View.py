# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Attributes View Transformation
# v0.3.0 - Focus on attributes and tag metadata
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                      import Dict, Any
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base


class Graph_Transform__Attributes_View(Graph_Transformation__Base):
    """Focus on attributes and tag metadata.

    Shows:
        - Tag nodes (element type info)
        - Attribute nodes (class, id, href, src, etc.)
        - Relationships between tags and attributes

    Useful for:
        - CSS class analysis
        - Attribute pattern discovery
        - Finding all links/images
        - Understanding page metadata
    """

    name        : str = "attributes_view"
    label       : str = "Attributes View"
    description : str = "Focus on attributes and tag metadata"

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 3: Transform Export - Filter to attrs source
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_export(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter export to show attributes graph content."""

        # For formats with nodes array (vis.js, D3)
        if 'nodes' in export_data:
            export_data['nodes'] = [
                node for node in export_data['nodes']
                if node.get('graph_source') == 'attrs'                              # Only attrs graph
                or node.get('nodeType') in ('tag', 'attribute')                     # Or tag/attr types
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
                    node for node in elements['nodes']
                    if node.get('data', {}).get('graph_source') == 'attrs'
                    or node.get('data', {}).get('nodeType') in ('tag', 'attribute')
                ]

                node_ids = {node.get('data', {}).get('id') for node in elements['nodes']}

                if 'edges' in elements:
                    elements['edges'] = [
                        edge for edge in elements['edges']
                        if edge.get('data', {}).get('source') in node_ids
                        and edge.get('data', {}).get('target') in node_ids
                    ]

        return export_data