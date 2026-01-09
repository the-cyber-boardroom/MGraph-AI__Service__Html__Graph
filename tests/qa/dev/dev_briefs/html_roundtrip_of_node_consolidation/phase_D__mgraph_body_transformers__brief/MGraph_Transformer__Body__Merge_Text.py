# ═══════════════════════════════════════════════════════════════════════════════
# MGraph_Transformer__Body__Merge_Text - Merge adjacent text nodes
# Part of Phase D: MGraph Body Transformers
#
# Combines multiple text nodes under the same parent into a single text node.
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                         import Dict, List
from mgraph_db.mgraph.MGraph                        import MGraph
from MGraph_Transformer__Body__Base                 import MGraph_Transformer__Body__Base


class MGraph_Transformer__Body__Merge_Text(MGraph_Transformer__Body__Base):
    """Merge multiple text nodes under the same parent into one.

    Before:
        parent ──text──► "Hello "
               ──text──► "World!"

    After:
        parent ──text──► "Hello World!"

    Usage:
        transformer = MGraph_Transformer__Body__Merge_Text()
        transformer.transform(body_graph)
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Transform
    # ═══════════════════════════════════════════════════════════════════════════

    def transform(self, mgraph: MGraph) -> MGraph:
        """Merge text nodes that share the same parent."""

        parents_with_text = self.find_parents_with_multiple_text_children(mgraph)

        for parent_id, text_children in parents_with_text.items():
            if len(text_children) < 2:                                          # Need at least 2 to merge
                continue
            
            self.merge_text_children(mgraph, parent_id, text_children)

        return mgraph

    # ═══════════════════════════════════════════════════════════════════════════
    # Find Parents with Multiple Text Children
    # ═══════════════════════════════════════════════════════════════════════════

    def find_parents_with_multiple_text_children(self, mgraph: MGraph) -> Dict[str, List[Dict]]:
        """Find all parent nodes that have multiple text children.

        Returns: {parent_id: [{node_id, value, position, domain_node}, ...]}
        """
        index   = mgraph.index()
        parents = {}                                                            # parent_id → list of text child info

        for domain_node in mgraph.data().nodes():                               # Find all text nodes
            if not self.is_text_node(domain_node):
                continue

            node_id    = self.get_node_id(domain_node)
            text_value = self.get_text_value(domain_node)

            incoming_edges = self.get_incoming_edges(mgraph, node_id)           # Get parent(s)

            for edge_id in incoming_edges:
                parent_id = index.edges_index.get_edge_from_node(edge_id)

                if parent_id is None:
                    continue

                parent_id_str = str(parent_id)
                position      = self.get_edge_position(mgraph, edge_id)

                if parent_id_str not in parents:
                    parents[parent_id_str] = []

                parents[parent_id_str].append({'node_id'    : node_id    ,
                                               'value'      : text_value ,
                                               'position'   : position   ,
                                               'domain_node': domain_node})

        return parents

    def get_edge_position(self, mgraph: MGraph, edge_id: str) -> int:
        """Extract position from edge_path for ordering."""
        edge_path = self.get_edge_path(mgraph, edge_id)

        if edge_path:
            try:
                return int(edge_path)
            except ValueError:
                pass

        predicate = self.get_edge_predicate(mgraph, edge_id)                    # Try predicate
        if predicate and ':' in predicate:
            try:
                return int(predicate.split(':')[-1])
            except ValueError:
                pass

        return 0

    # ═══════════════════════════════════════════════════════════════════════════
    # Merge Text Children
    # ═══════════════════════════════════════════════════════════════════════════

    def merge_text_children(self, mgraph: MGraph, parent_id: str, text_children: List[Dict]):
        """Merge multiple text children into one.

        1. Sort by position
        2. Concatenate values
        3. Keep first node, update its value
        4. Delete other nodes
        """
        sorted_children = sorted(text_children, key=lambda x: x.get('position', 0))
        merged_value    = ''.join(child['value'] for child in sorted_children)

        first_child   = sorted_children[0]                                      # Keep first, update value
        first_node    = first_child['domain_node']
        self.set_text_value(first_node, merged_value)

        for child in sorted_children[1:]:                                       # Delete remaining nodes
            self.delete_node(mgraph, child['node_id'])