# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Body Only Transformation
# v0.3.0 - Show only content from body graph
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                      import Dict, Any
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base


class Graph_Transform__Body_Only(Graph_Transformation__Base):
    """Show only the body graph content.

    Filters export to only include data from body_graph, excluding:
        - Head content (meta, title, links)
        - Scripts
        - Styles
        - Document-level metadata

    Useful for focusing on visible page content.
    """

    name        : str = "body_only"
    label       : str = "Body Only"
    description : str = "Show only body content, hiding head, scripts, and styles"

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 3: Transform Export - Filter to body source only
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_export(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter export to only include nodes/edges from body graph."""

        # For formats with nodes array (vis.js, D3)
        if 'nodes' in export_data:
            export_data['nodes'] = [
                node for node in export_data['nodes']
                if node.get('graph_source') == 'body'
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

        # For Cytoscape format with elements.nodes/elements.edges
        if 'elements' in export_data:
            elements = export_data['elements']
            if 'nodes' in elements:
                elements['nodes'] = [
                    node for node in elements['nodes']
                    if node.get('data', {}).get('graph_source') == 'body'
                ]

                node_ids = {node.get('data', {}).get('id') for node in elements['nodes']}

                if 'edges' in elements:
                    elements['edges'] = [
                        edge for edge in elements['edges']
                        if edge.get('data', {}).get('source') in node_ids
                        and edge.get('data', {}).get('target') in node_ids
                    ]

        return export_data