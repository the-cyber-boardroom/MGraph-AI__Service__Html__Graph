# ═══════════════════════════════════════════════════════════════════════════════
# MGraph_Transformer__Body__Unwrap_Inline - Remove inline wrapper elements
# Part of Phase D: MGraph Body Transformers
#
# Unwraps inline elements (<a>, <b>, <i>, <span>, etc.) by:
# 1. Connecting the parent directly to the inline element's children
# 2. Removing the inline element
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                         import Set, List, Dict
from mgraph_db.mgraph.MGraph                        import MGraph
from MGraph_Transformer__Body__Base                 import MGraph_Transformer__Body__Base


# Standard HTML inline tags
INLINE_TAGS = {'a', 'abbr', 'b', 'bdo', 'big', 'cite', 'code', 'dfn', 'em', 'i',
               'kbd', 'mark', 'q', 'samp', 'small', 'span', 'strong', 'sub', 'sup',
               'tt', 'u', 'var'}


class MGraph_Transformer__Body__Unwrap_Inline(MGraph_Transformer__Body__Base):
    """Unwrap inline elements, keeping their children connected to the parent.

    Before:
        parent ──child──► <a> ──text──► "link"

    After:
        parent ──text──► "link"

    Configuration:
        inline_tags: Set of tags to unwrap (default: standard HTML inline tags)

    Usage:
        transformer = MGraph_Transformer__Body__Unwrap_Inline()
        transformer.transform(body_graph)

        # Or with custom tags:
        transformer = MGraph_Transformer__Body__Unwrap_Inline(inline_tags={'span', 'div'})
    """

    inline_tags: set = None                                                     # Tags to unwrap

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.inline_tags is None:
            self.inline_tags = INLINE_TAGS.copy()

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Transform
    # ═══════════════════════════════════════════════════════════════════════════

    def transform(self, mgraph: MGraph) -> MGraph:
        """Unwrap all inline elements in the graph."""

        wrapper_node_ids = self.find_inline_wrappers(mgraph)                    # Find inline wrappers
        edges_to_add     = self.collect_shortcut_edges(mgraph, wrapper_node_ids) # Collect edges to add

        for edge_info in edges_to_add:                                          # Create shortcut edges with predicate + path
            self.create_edge(mgraph,
                             edge_info['from_node_id']    ,
                             edge_info['to_node_id']      ,
                             edge_info.get('predicate')   ,
                             edge_info.get('edge_path')   )

        for node_id in wrapper_node_ids:                                        # Remove wrapper nodes
            self.delete_node(mgraph, node_id)

        return mgraph

    # ═══════════════════════════════════════════════════════════════════════════
    # Find Inline Wrappers
    # ═══════════════════════════════════════════════════════════════════════════

    def find_inline_wrappers(self, mgraph: MGraph) -> Set[str]:
        """Find all inline wrapper nodes that should be unwrapped.

        A node is an inline wrapper if:
        1. Its tag is in inline_tags
        2. It has children (outgoing edges)
        """
        wrappers = set()

        for domain_node in mgraph.data().nodes():
            node_path = self.get_node_path(domain_node)
            tag       = self.get_node_tag(node_path)

            if tag not in self.inline_tags:                                     # Skip non-inline tags
                continue

            node_id        = self.get_node_id(domain_node)
            outgoing_edges = self.get_outgoing_edges(mgraph, node_id)

            if len(outgoing_edges) > 0:                                         # Must have children
                wrappers.add(node_id)

        return wrappers

    # ═══════════════════════════════════════════════════════════════════════════
    # Collect Shortcut Edges
    # ═══════════════════════════════════════════════════════════════════════════

    def collect_shortcut_edges(self, mgraph: MGraph, wrapper_node_ids: Set[str]) -> List[Dict]:
        """Collect all edges that need to be created to bypass wrappers.

        For each wrapper:
        - Find its parent(s)
        - Find its children
        - Create edge: parent → child (preserving edge predicate and edge_path for ordering)
        """
        edges_to_add = []
        index        = mgraph.index()

        for wrapper_id in wrapper_node_ids:
            incoming_edges = self.get_incoming_edges(mgraph, wrapper_id)        # Get parents
            outgoing_edges = self.get_outgoing_edges(mgraph, wrapper_id)        # Get children

            for parent_edge_id in incoming_edges:                               # For each parent
                parent_id       = index.edges_index.get_edge_from_node(parent_edge_id)
                parent_edge_path = self.get_edge_path(mgraph, parent_edge_id)   # Position in parent!

                if parent_id is None:
                    continue

                for child_edge_id in outgoing_edges:                            # Connect to each child
                    child_id  = index.edges_index.get_edge_to_node(child_edge_id)
                    predicate = self.get_edge_predicate(mgraph, child_edge_id)  # Capture predicate!

                    if child_id is None:
                        continue

                    edges_to_add.append({'from_node_id': str(parent_id)  ,
                                         'to_node_id'  : str(child_id)   ,
                                         'predicate'   : predicate       ,
                                         'edge_path'   : parent_edge_path})     # Preserve position!

        return edges_to_add