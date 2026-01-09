# ═══════════════════════════════════════════════════════════════════════════════
# MGraph_Transformer__Body__Remove_Empty_Text - Remove whitespace-only text nodes
# Part of Phase D: MGraph Body Transformers
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                         import List
from mgraph_db.mgraph.MGraph                        import MGraph
from MGraph_Transformer__Body__Base                 import MGraph_Transformer__Body__Base


class MGraph_Transformer__Body__Remove_Empty_Text(MGraph_Transformer__Body__Base):
    """Remove text nodes that contain only whitespace.

    Usage:
        transformer = MGraph_Transformer__Body__Remove_Empty_Text()
        transformer.transform(body_graph)

        # Or preserve single spaces:
        transformer = MGraph_Transformer__Body__Remove_Empty_Text(preserve_single_space=True)
    """

    preserve_single_space: bool = False                                         # If True, keep nodes with exactly " "

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Transform
    # ═══════════════════════════════════════════════════════════════════════════

    def transform(self, mgraph: MGraph) -> MGraph:
        """Remove all whitespace-only text nodes."""

        nodes_to_remove = self.find_empty_text_nodes(mgraph)

        for node_id in nodes_to_remove:
            self.delete_node(mgraph, node_id)

        return mgraph

    # ═══════════════════════════════════════════════════════════════════════════
    # Find Empty Text Nodes
    # ═══════════════════════════════════════════════════════════════════════════

    def find_empty_text_nodes(self, mgraph: MGraph) -> List[str]:
        """Find all text nodes that contain only whitespace."""
        empty_nodes = []

        for domain_node in mgraph.data().nodes():
            if not self.is_text_node(domain_node):
                continue

            text_value = self.get_text_value(domain_node)

            if self.is_empty_text(text_value):
                empty_nodes.append(self.get_node_id(domain_node))

        return empty_nodes

    def is_empty_text(self, text_value: str) -> bool:
        """Check if text value should be considered empty."""
        if not text_value:
            return True

        stripped = text_value.strip()

        if not stripped:                                                        # All whitespace
            if self.preserve_single_space and text_value == ' ':
                return False                                                    # Preserve single space
            return True

        return False