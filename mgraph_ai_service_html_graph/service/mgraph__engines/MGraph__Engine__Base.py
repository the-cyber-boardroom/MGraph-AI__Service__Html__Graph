# ═══════════════════════════════════════════════════════════════════════════════
# MGraph Engine - Base Class for all rendering engines
#
# Provides common functionality for converting MGraph to visualization formats.
# Each engine (DOT, D3, Cytoscape, etc.) extends this base with format-specific
# export logic.
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                     import Any, List, Optional
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Base  import MGraph__Engine__Config__Base
from mgraph_db.mgraph.MGraph         import MGraph
from osbot_utils.type_safe.Type_Safe import Type_Safe


class MGraph__Engine__Base(Type_Safe):                              # Base class for all MGraph rendering engines
    mgraph : MGraph                         = None                                                      # The MGraph to render
    config : MGraph__Engine__Config__Base   = None                                                      # Engine-specific configuration

    def export(self) -> Any:                                                    # Export MGraph to engine-specific format
        raise NotImplementedError("Subclasses must implement export()")

    # ═══════════════════════════════════════════════════════════════════════════
    # Node/Edge Iteration Helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def nodes(self) -> List:                                                    # Get all nodes from MGraph
        if self.mgraph and self.mgraph.data():
            return self.mgraph.data().nodes()
        return []

    def edges(self) -> List:                                                    # Get all edges from MGraph
        if self.mgraph and self.mgraph.data():
            return self.mgraph.data().edges()
        return []

    def node_ids(self) -> List:                                                 # Get all node IDs
        if self.mgraph and self.mgraph.data():
            return self.mgraph.data().nodes_ids()
        return []

    def edge_ids(self) -> List:                                                 # Get all edge IDs
        if self.mgraph and self.mgraph.data():
            return self.mgraph.data().edges_ids()
        return []

    # ═══════════════════════════════════════════════════════════════════════════
    # Node Data Access Helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def node_path(self, node) -> Optional[str]:                                 # Get node_path from node
        if hasattr(node, 'node') and hasattr(node.node, 'data'):
            path = node.node.data.node_path
            return str(path) if path else None
        return None

    def node_value(self, node) -> Optional[str]:                                # Get value from value node
        if hasattr(node, 'node') and hasattr(node.node, 'data'):
            node_data = node.node.data
            if hasattr(node_data, 'node_data') and hasattr(node_data.node_data, 'value'):
                return str(node_data.node_data.value)
        return None

    def node_id_str(self, node) -> str:                                         # Get node ID as string
        if hasattr(node, 'node_id'):
            return str(node.node_id)
        return str(id(node))

    # ═══════════════════════════════════════════════════════════════════════════
    # Edge Data Access Helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def edge_from_id(self, edge) -> str:                                        # Get source node ID from edge
        if hasattr(edge, 'edge') and hasattr(edge.edge, 'data'):
            return str(edge.edge.data.from_node_id)
        return ''

    def edge_to_id(self, edge) -> str:                                          # Get target node ID from edge
        if hasattr(edge, 'edge') and hasattr(edge.edge, 'data'):
            return str(edge.edge.data.to_node_id)
        return ''

    def edge_predicate(self, edge) -> Optional[str]:                            # Get predicate from edge label
        if hasattr(edge, 'edge') and hasattr(edge.edge, 'data'):
            label = edge.edge.data.edge_label
            if label and hasattr(label, 'predicate') and label.predicate:
                return str(label.predicate)
        return None

    def edge_path(self, edge) -> Optional[str]:                                 # Get edge_path from edge
        if hasattr(edge, 'edge') and hasattr(edge.edge, 'data'):
            path = edge.edge.data.edge_path
            return str(path) if path else None
        return None

    # ═══════════════════════════════════════════════════════════════════════════
    # Styling Metadata Access
    # ═══════════════════════════════════════════════════════════════════════════

    # todo: review this use of metadata, since this pattern is reall node currently used in the way we use graphs
    #       idea: what about using a different type of mgraph to hold these styling data?
    def get_node_style(self, node, key: str, default: Any = None) -> Any:       # Get styling metadata from node
        if hasattr(node, 'node') and hasattr(node.node, 'data'):
            node_data = node.node.data
            if hasattr(node_data, 'node_data'):
                data = node_data.node_data
                if hasattr(data, 'metadata') and isinstance(data.metadata, dict):
                    return data.metadata.get(key, default)
        return default

    def get_edge_style(self, edge, key: str, default: Any = None) -> Any:       # Get styling metadata from edge
        if hasattr(edge, 'edge') and hasattr(edge.edge, 'data'):
            edge_data = edge.edge.data
            if hasattr(edge_data, 'metadata') and isinstance(edge_data.metadata, dict):
                return edge_data.metadata.get(key, default)
        return default

    # ═══════════════════════════════════════════════════════════════════════════
    # Common Utility Methods
    # ═══════════════════════════════════════════════════════════════════════════

    # see if we can use a Type_Safe primitive for this
    def truncate(self, text: str, max_length: int) -> str:                      # Truncate text with ellipsis
        if not text:
            return ''
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + '...'

    # see if we can use a Type_Safe primitive for this
    def escape_quotes(self, text: str) -> str:                                  # Escape double quotes in text
        if not text:
            return ''
        return text.replace('"', '\\"')

    # todo: we should be using Type_Safe Safe_Id for this
    def safe_id(self, id_str: str) -> str:                                      # Make ID safe for most formats
        if not id_str:
            return 'unknown'
        return id_str.replace('-', '_').replace(':', '_').replace('.', '_')
