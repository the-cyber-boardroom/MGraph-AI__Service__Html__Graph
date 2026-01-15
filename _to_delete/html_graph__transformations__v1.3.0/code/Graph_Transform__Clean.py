# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Clean View Transformation
# v0.3.0 - Clean DOM tree view
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                      import Dict, Any
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base


class Graph_Transform__Clean(Graph_Transformation__Base):
    """Clean DOM tree view.

    Shows a simplified, readable DOM structure:
        - Element nodes with their text content
        - No separate tag nodes
        - No separate attribute nodes
        - Text displayed inline with parent elements

    Ideal for:
        - Quick understanding of page structure
        - Clean screenshots/exports
        - Presentations
    """

    name        : str = "clean"
    label       : str = "Clean View"
    description : str = "Clean DOM tree without tag/attribute detail nodes"

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 2: Transform MGraph - Clear text node paths for cleaner display
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_mgraph(self, html_mgraph: Html_MGraph) -> Html_MGraph:        # Clean up node paths for better display.
        if html_mgraph.document:
            if html_mgraph.body_graph:                                              # Clear text node paths so they display cleanly
                self._clear_text_node_paths(html_mgraph.body_graph)
        return html_mgraph

    def _clear_text_node_paths(self, html_body) -> None:
        """Set text node paths to empty for cleaner labels."""
        mgraph = html_body.mgraph
        nodes = mgraph.graph.model.data.nodes
        for node_id, node in nodes.items():
            if node.node_path == 'text':
                node.node_path = ''

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 3: Transform Export - Filter out tag/attr nodes
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_export(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter export to show only element and text nodes."""

        allowed_types = {'element', 'text'}

        # For formats with nodes array (vis.js, D3)
        if 'nodes' in export_data:
            export_data['nodes'] = [
                node for node in export_data['nodes']
                if node.get('nodeType') in allowed_types
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
                    if node.get('data', {}).get('nodeType') in allowed_types
                ]

                node_ids = {node.get('data', {}).get('id') for node in elements['nodes']}

                if 'edges' in elements:
                    elements['edges'] = [
                        edge for edge in elements['edges']
                        if edge.get('data', {}).get('source') in node_ids
                        and edge.get('data', {}).get('target') in node_ids
                    ]

        return export_data