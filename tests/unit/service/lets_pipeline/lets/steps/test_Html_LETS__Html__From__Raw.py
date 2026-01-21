# ═══════════════════════════════════════════════════════════════════════════════
# MGraph_Transformer__Body__Base - Base class for body graph transformations
# Part of Phase D: MGraph Body Transformers
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                 import List, Dict, Any, Optional, Set
from osbot_utils.type_safe.Type_Safe        import Type_Safe
from mgraph_db.mgraph.MGraph                import MGraph


class MGraph_Transformer__Body__Base(Type_Safe):
    """Base class for body graph transformations.

    Transformers operate in-place on the MGraph and return
    the same graph reference for chaining.

    Usage:
        transformer = MGraph_Transformer__Body__SomeTransform()
        transformer.transform(body_graph)
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Transform Method (Override in subclasses)
    # ═══════════════════════════════════════════════════════════════════════════

    def transform(self, mgraph: MGraph) -> MGraph:
        """Apply transformation in-place, return same graph for chaining.

        Override this method in subclasses to implement specific transformations.
        """
        raise NotImplementedError("Subclasses must implement transform()")

    # ═══════════════════════════════════════════════════════════════════════════
    # Node Inspection Helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def get_node_tag(self, node_path: str) -> str:
        """Extract tag from node_path: 'body.div.a' → 'a', 'body.div[0]' → 'div'"""
        if not node_path:
            return ''
        last_part = node_path.split('.')[-1] if '.' in node_path else node_path
        if '[' in last_part:
            last_part = last_part[:last_part.index('[')]
        return last_part.lower()

    def is_text_node(self, domain_node) -> bool:
        """Check if node is a text node."""
        node_path = domain_node.node.data.node_path
        return str(node_path) == 'text' if node_path else False

    def get_text_value(self, domain_node) -> str:
        """Get text value from text node."""
        node_data = domain_node.node.data.node_data
        if node_data and hasattr(node_data, 'value'):
            return str(node_data.value) if node_data.value else ''
        return ''

    def set_text_value(self, domain_node, value: str):
        """Set text value on a text node."""
        node_data = domain_node.node.data.node_data
        if node_data and hasattr(node_data, 'value'):
            node_data.value = value

    def get_node_id(self, domain_node) -> str:
        """Get node_id as string."""
        return str(domain_node.node.data.node_id)

    def get_node_path(self, domain_node) -> str:
        """Get node_path as string."""
        node_path = domain_node.node.data.node_path
        return str(node_path) if node_path else ''

    # ═══════════════════════════════════════════════════════════════════════════
    # Graph Traversal Helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def get_all_nodes(self, mgraph: MGraph) -> list:
        """Get all domain nodes from the graph."""
        return list(mgraph.data().nodes())

    def get_node_by_id(self, mgraph: MGraph, node_id: str):
        """Find a domain node by its node_id."""
        for domain_node in mgraph.data().nodes():
            if str(domain_node.node.data.node_id) == str(node_id):
                return domain_node
        return None

    def get_parent_node_ids(self, mgraph: MGraph, node_id: str) -> List[str]:
        """Get parent node_ids via incoming edges."""
        incoming_edges = self.get_incoming_edges(mgraph, node_id)
        parent_ids     = []

        for edge_id in incoming_edges:
            parent_id = self.get_edge_from_node(mgraph, edge_id)
            if parent_id:
                parent_ids.append(str(parent_id))

        return parent_ids

    def get_child_node_ids(self, mgraph: MGraph, node_id: str) -> List[str]:
        """Get child node_ids via outgoing edges."""
        outgoing_edges = self.get_outgoing_edges(mgraph, node_id)
        child_ids      = []

        for edge_id in outgoing_edges:
            child_id = self.get_edge_to_node(mgraph, edge_id)
            if child_id:
                child_ids.append(str(child_id))

        return child_ids

    def get_incoming_edges(self, mgraph: MGraph, node_id: str) -> Set:
        """Get set of incoming edge_ids for a node."""
        incoming = set()
        for edge in mgraph.data().edges():
            edge_data = edge.edge.data
            if str(edge_data.to_node_id) == str(node_id):
                incoming.add(edge_data.edge_id)
        return incoming

    def get_outgoing_edges(self, mgraph: MGraph, node_id: str) -> Set:
        """Get set of outgoing edge_ids for a node."""
        outgoing = set()
        for edge in mgraph.data().edges():
            edge_data = edge.edge.data
            if str(edge_data.from_node_id) == str(node_id):
                outgoing.add(edge_data.edge_id)
        return outgoing

    def get_edge_from_node(self, mgraph: MGraph, edge_id: str) -> str:
        """Get the from_node_id of an edge."""
        edge = mgraph.data().edge(edge_id)
        if edge:
            return str(edge.from_node_id)
        return None

    def get_edge_to_node(self, mgraph: MGraph, edge_id: str) -> str:
        """Get the to_node_id of an edge."""
        edge = mgraph.data().edge(edge_id)
        if edge:
            return str(edge.to_node_id)
        return None

    def get_edge_predicate(self, mgraph: MGraph, edge_id: str) -> str:
        """Get the predicate (label) of an edge."""
        index     = mgraph.index()
        edge_data = index.edges_index.get_edge_data(edge_id)

        if edge_data:
            label = edge_data.edge_label
            if label and hasattr(label, 'predicate'):
                return str(label.predicate) if label.predicate else ''
        return ''

    def get_edge_path(self, mgraph: MGraph, edge_id: str) -> str:
        """Get the edge_path (position) of an edge."""
        index     = mgraph.index()
        edge_data = index.edges_index.get_edge_data(edge_id)

        if edge_data and hasattr(edge_data, 'edge_path'):
            return str(edge_data.edge_path) if edge_data.edge_path else ''
        return ''

    # ═══════════════════════════════════════════════════════════════════════════
    # Graph Modification Helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def delete_node(self, mgraph: MGraph, node_id: str) -> bool:
        """Delete a node and its edges from the graph."""
        try:
            mgraph.edit().delete_node(node_id)
            return True
        except:
            return False

    def create_edge(self, mgraph: MGraph, from_node_id: str, to_node_id: str, predicate: str = None, edge_path: str = None) -> Any:
        """Create a new edge between two nodes, optionally with a predicate and edge_path."""
        from mgraph_db.mgraph.schemas.Schema__MGraph__Edge__Label import Schema__MGraph__Edge__Label
        from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id   import Safe_Id
        from osbot_utils.type_safe.primitives.domains.identifiers.Edge_Path import Edge_Path

        edge_label    = None
        edge_path_obj = None

        if predicate:
            edge_label = Schema__MGraph__Edge__Label(predicate=Safe_Id(predicate))

        if edge_path:
            edge_path_obj = Edge_Path(edge_path)

        return mgraph.edit().new_edge(from_node_id = from_node_id ,
                                      to_node_id   = to_node_id   ,
                                      edge_label   = edge_label   ,
                                      edge_path    = edge_path_obj)

    def create_text_node(self, mgraph: MGraph, text_value: str) -> Any:
        """Create a new text node with the given value."""
        from mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value       import Schema__MGraph__Node__Value
        from mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value__Data import Schema__MGraph__Node__Value__Data
        from osbot_utils.type_safe.primitives.domains.identifiers.Node_Path import Node_Path

        node_data = Schema__MGraph__Node__Value__Data(value      = text_value,
                                                       value_type = str       )

        return mgraph.edit().new_node(node_type = Schema__MGraph__Node__Value,
                                      node_path = Node_Path('text')          ,
                                      node_data = node_data                  )

    # ═══════════════════════════════════════════════════════════════════════════
    # Batch Collection Helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def find_nodes_by_tag(self, mgraph: MGraph, tags: Set[str]) -> List[Dict]:
        """Find all nodes whose tag is in the given set.

        Returns list of dicts with: node_id, node_path, tag, domain_node
        """
        tags_lower = {tag.lower() for tag in tags}
        matches    = []

        for domain_node in mgraph.data().nodes():
            node_path = self.get_node_path(domain_node)
            tag       = self.get_node_tag(node_path)

            if tag in tags_lower:
                matches.append({'node_id'    : self.get_node_id(domain_node),
                                'node_path'  : node_path                    ,
                                'tag'        : tag                          ,
                                'domain_node': domain_node                  })
        return matches

    def find_text_nodes(self, mgraph: MGraph) -> List[Dict]:
        """Find all text nodes.

        Returns list of dicts with: node_id, value, domain_node
        """
        text_nodes = []

        for domain_node in mgraph.data().nodes():
            if self.is_text_node(domain_node):
                text_nodes.append({'node_id'    : self.get_node_id(domain_node)   ,
                                   'value'      : self.get_text_value(domain_node),
                                   'domain_node': domain_node                     })
        return text_nodes

    def find_element_nodes(self, mgraph: MGraph) -> List[Dict]:
        """Find all element (non-text) nodes.

        Returns list of dicts with: node_id, node_path, tag, domain_node
        """
        elements = []

        for domain_node in mgraph.data().nodes():
            if not self.is_text_node(domain_node):
                node_path = self.get_node_path(domain_node)
                elements.append({'node_id'    : self.get_node_id(domain_node),
                                 'node_path'  : node_path                    ,
                                 'tag'        : self.get_node_tag(node_path) ,
                                 'domain_node': domain_node                  })
        return elements