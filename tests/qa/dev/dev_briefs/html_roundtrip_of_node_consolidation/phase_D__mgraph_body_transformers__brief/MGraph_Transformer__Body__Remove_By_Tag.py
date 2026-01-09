# ═══════════════════════════════════════════════════════════════════════════════
# MGraph_Transformer__Body__Remove_By_Tag - Remove elements by tag name
# Part of Phase D: MGraph Body Transformers
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                         import Set, List
from mgraph_db.mgraph.MGraph                        import MGraph
from MGraph_Transformer__Body__Base                 import MGraph_Transformer__Body__Base


class MGraph_Transformer__Body__Remove_By_Tag(MGraph_Transformer__Body__Base):
    """Remove all elements with specific tags.

    By default, removes the element AND all its children (subtree removal).
    Set remove_children=False to keep children connected to the parent.

    Usage:
        # Remove script and style elements entirely
        transformer = MGraph_Transformer__Body__Remove_By_Tag(tags_to_remove={'script', 'style'})
        transformer.transform(body_graph)

        # Remove nav tags but keep their content
        transformer = MGraph_Transformer__Body__Remove_By_Tag(
            tags_to_remove={'nav'},
            remove_children=False
        )
    """

    tags_to_remove : set  = None                                                # Tags to remove
    remove_children: bool = True                                                # If True, remove subtree; if False, reconnect children

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.tags_to_remove is None:
            self.tags_to_remove = set()

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Transform
    # ═══════════════════════════════════════════════════════════════════════════

    def transform(self, mgraph: MGraph) -> MGraph:
        """Remove all elements with tags in tags_to_remove."""

        if not self.tags_to_remove:
            return mgraph

        nodes_to_remove = self.find_nodes_to_remove(mgraph)

        if self.remove_children:
            self.remove_subtrees(mgraph, nodes_to_remove)                       # Remove entire subtrees
        else:
            self.unwrap_nodes(mgraph, nodes_to_remove)                          # Reconnect children to parent

        return mgraph

    # ═══════════════════════════════════════════════════════════════════════════
    # Find Nodes to Remove
    # ═══════════════════════════════════════════════════════════════════════════

    def find_nodes_to_remove(self, mgraph: MGraph) -> Set[str]:
        """Find all nodes whose tag is in tags_to_remove."""
        tags_lower = {tag.lower() for tag in self.tags_to_remove}
        to_remove  = set()

        for domain_node in mgraph.data().nodes():
            node_path = self.get_node_path(domain_node)
            tag       = self.get_node_tag(node_path)

            if tag in tags_lower:
                to_remove.add(self.get_node_id(domain_node))

        return to_remove

    # ═══════════════════════════════════════════════════════════════════════════
    # Remove Subtrees
    # ═══════════════════════════════════════════════════════════════════════════

    def remove_subtrees(self, mgraph: MGraph, root_node_ids: Set[str]):
        """Remove nodes and all their descendants."""

        all_nodes_to_remove = set()                                             # Collect all nodes in subtrees

        for root_id in root_node_ids:
            subtree = self.collect_subtree(mgraph, root_id)
            all_nodes_to_remove.update(subtree)

        for node_id in all_nodes_to_remove:                                     # Delete all nodes (order doesn't matter for MGraph)
            self.delete_node(mgraph, node_id)

    def collect_subtree(self, mgraph: MGraph, root_id: str) -> Set[str]:
        """Collect all node_ids in subtree rooted at root_id (BFS)."""
        subtree = set()
        queue   = [root_id]

        while queue:
            node_id = queue.pop(0)

            if node_id in subtree:                                              # Already visited
                continue

            subtree.add(node_id)

            child_ids = self.get_child_node_ids(mgraph, node_id)                # Add children to queue
            queue.extend(child_ids)

        return subtree

    # ═══════════════════════════════════════════════════════════════════════════
    # Unwrap Nodes (Keep Children)
    # ═══════════════════════════════════════════════════════════════════════════

    def unwrap_nodes(self, mgraph: MGraph, node_ids: Set[str]):
        """Remove nodes but reconnect their children to their parents."""
        index        = mgraph.index()
        edges_to_add = []

        for node_id in node_ids:                                                # Collect edges to add
            incoming_edges = self.get_incoming_edges(mgraph, node_id)
            outgoing_edges = self.get_outgoing_edges(mgraph, node_id)

            for parent_edge_id in incoming_edges:
                parent_id        = index.edges_index.get_edge_from_node(parent_edge_id)
                parent_edge_path = self.get_edge_path(mgraph, parent_edge_id)   # Position in parent!

                if parent_id is None:
                    continue

                for child_edge_id in outgoing_edges:
                    child_id  = index.edges_index.get_edge_to_node(child_edge_id)
                    predicate = self.get_edge_predicate(mgraph, child_edge_id)

                    if child_id is None:
                        continue
                    if str(child_id) in node_ids:                               # Don't connect to nodes being removed
                        continue

                    edges_to_add.append({'from'     : str(parent_id)  ,
                                         'to'       : str(child_id)   ,
                                         'predicate': predicate       ,
                                         'edge_path': parent_edge_path})

        for edge in edges_to_add:                                               # Create shortcut edges with predicate + path
            self.create_edge(mgraph, edge['from'], edge['to'], edge.get('predicate'), edge.get('edge_path'))

        for node_id in node_ids:                                                # Remove the nodes
            self.delete_node(mgraph, node_id)