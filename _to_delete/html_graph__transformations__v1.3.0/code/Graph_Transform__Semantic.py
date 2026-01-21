# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Semantic View Transformation
# v0.3.0 - Semantic content view with merged text
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                      import Dict, Any, List
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base


class Graph_Transform__Semantic(Graph_Transformation__Base):
    """Semantic content view with merged text.

    Transforms the graph for content-focused analysis:
        - Collapses single-child chains (div→div→p becomes just p)
        - Merges multiple text nodes under same parent
        - Removes structural noise

    Ideal for:
        - Content extraction
        - Text analysis
        - Understanding semantic structure
        - NLP preprocessing
    """

    name        : str = "semantic"
    label       : str = "Semantic View"
    description : str = "Content-focused view with merged text and collapsed wrappers"

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 2: Transform MGraph - Collapse and merge
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_mgraph(self, html_mgraph: Html_MGraph) -> Html_MGraph:
        """Apply semantic transformations to body graph."""

        if html_mgraph.document and html_mgraph.body_graph:
            self._collapse_single_child_parents(html_mgraph.body_graph.mgraph)
            self._merge_text_children(html_mgraph.body_graph.mgraph)

        return html_mgraph

    # ═══════════════════════════════════════════════════════════════════════════
    # Graph Traversal Utilities
    # ═══════════════════════════════════════════════════════════════════════════

    def _get_parent_node_id(self, mgraph, node_id):
        """Get parent node ID via incoming edge."""
        index = mgraph.index()
        incoming_edges = index.get_node_id_incoming_edges(node_id)

        if incoming_edges:
            edge_id = next(iter(incoming_edges))
            from_node_id, _ = index.edges_to_nodes()[edge_id]
            return from_node_id
        return None

    def _get_incoming_edge_path(self, mgraph, node_id):
        """Get the edge_path of incoming edge to node."""
        index = mgraph.index()
        incoming_edges = index.get_node_id_incoming_edges(node_id)

        if incoming_edges:
            edge_id = next(iter(incoming_edges))
            edge = mgraph.data().edge(edge_id)
            return edge.edge_path
        return None

    def _get_outgoing_edge_count(self, mgraph, node_id):
        """Count outgoing edges from node."""
        index = mgraph.index()
        outgoing_edges = index.get_node_id_outgoing_edges(node_id)
        return len(outgoing_edges) if outgoing_edges else 0

    def _is_single_child_parent(self, mgraph, node_id):
        """Check if node has exactly one child."""
        return self._get_outgoing_edge_count(mgraph, node_id) == 1

    # ═══════════════════════════════════════════════════════════════════════════
    # Graph Modification Utilities
    # ═══════════════════════════════════════════════════════════════════════════

    def _create_edge_with_path(self, mgraph, from_node_id, to_node_id, edge_path):
        """Create new edge with specified path."""
        edit = mgraph.edit()
        edit.new_edge(from_node_id=from_node_id,
                      to_node_id=to_node_id,
                      edge_path=edge_path)

    def _delete_nodes(self, mgraph, node_ids):
        """Delete multiple nodes from graph."""
        edit = mgraph.edit()
        for node_id in set(node_ids):
            edit.delete_node(node_id)

    # ═══════════════════════════════════════════════════════════════════════════
    # Text Node Utilities
    # ═══════════════════════════════════════════════════════════════════════════

    def _get_text_nodes(self, mgraph) -> List:
        """Get all text nodes from graph."""
        text_nodes = []
        nodes = mgraph.graph.model.data.nodes.values()
        for node in nodes:
            if node.node_path == 'text':
                text_nodes.append(node)
        return text_nodes

    def _get_text_children_ordered(self, mgraph, parent_node_id) -> List[Dict]:
        """Get all text child nodes of a parent, sorted by edge_path."""
        index = mgraph.index()
        outgoing_edges = index.get_node_id_outgoing_edges(parent_node_id)

        if not outgoing_edges:
            return []

        children = []
        for edge_id in outgoing_edges:
            edge = mgraph.data().edge(edge_id)
            _, to_node_id = index.edges_to_nodes()[edge_id]
            node = mgraph.data().node(to_node_id)

            # Check if it's a text/value node
            if hasattr(node, 'node_data') and hasattr(node.node_data, 'value'):
                edge_path = edge.edge_path or '0'
                children.append({
                    'node_id'  : to_node_id                                    ,
                    'node'     : node                                          ,
                    'value'    : node.node_data.value                          ,
                    'edge_path': int(edge_path) if str(edge_path).isdigit() else 0,
                })

        return sorted(children, key=lambda x: x['edge_path'])

    def _get_parent_nodes_with_text_children(self, mgraph) -> List:
        """Find all non-text nodes that have text children."""
        parent_ids = set()
        for node in self._get_text_nodes(mgraph):
            parent_id = self._get_parent_node_id(mgraph, node.node_id)
            if parent_id:
                parent_ids.add(parent_id)
        return sorted(parent_ids)

    def _create_merged_text_node(self, mgraph, parent_node_id, merged_value):
        """Create a new text node with merged value and link to parent."""
        edit = mgraph.edit()
        new_node = edit.new_value(merged_value, node_path='text')
        edit.new_edge(from_node_id=parent_node_id,
                      to_node_id=new_node.node_id,
                      edge_path='0')
        return new_node

    # ═══════════════════════════════════════════════════════════════════════════
    # Transform Operations
    # ═══════════════════════════════════════════════════════════════════════════

    def _collapse_single_child_parents(self, mgraph):
        """Remove pass-through parent nodes that have only one child.

        Connects grandparent directly to grandchild, removing
        intermediate single-child wrapper elements.
        """
        nodes_to_delete = []

        for node in self._get_text_nodes(mgraph):
            node_id              = node.node_id
            parent_node_id       = self._get_parent_node_id(mgraph, node_id)
            grand_parent_node_id = self._get_parent_node_id(mgraph, parent_node_id)

            if parent_node_id and grand_parent_node_id:
                if self._is_single_child_parent(mgraph, parent_node_id):
                    edge_path = self._get_incoming_edge_path(mgraph, parent_node_id)
                    self._create_edge_with_path(mgraph, grand_parent_node_id, node_id, edge_path)
                    nodes_to_delete.append(parent_node_id)

        self._delete_nodes(mgraph, nodes_to_delete)

    def _merge_text_children(self, mgraph):
        """Merge all text children of each parent into a single text node.

        Concatenates multiple text fragments in order,
        creating cleaner semantic units.
        """
        parent_ids = self._get_parent_nodes_with_text_children(mgraph)

        for parent_id in parent_ids:
            children = self._get_text_children_ordered(mgraph, parent_id)

            if len(children) <= 1:
                continue                                                            # Nothing to merge

            # Concatenate values in order
            merged_value = ''.join(child['value'] for child in children)
            merged_value = merged_value.strip()

            # Collect node IDs to delete
            nodes_to_delete = [child['node_id'] for child in children]

            # Delete old text nodes
            self._delete_nodes(mgraph, nodes_to_delete)

            # Create new merged node
            if merged_value:                                                        # Only if there's actual content
                self._create_merged_text_node(mgraph, parent_id, merged_value)

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 3: Transform Export - Clean up output
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_export(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter export to element and text nodes only."""

        allowed_types = {'element', 'text'}

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

        return export_data