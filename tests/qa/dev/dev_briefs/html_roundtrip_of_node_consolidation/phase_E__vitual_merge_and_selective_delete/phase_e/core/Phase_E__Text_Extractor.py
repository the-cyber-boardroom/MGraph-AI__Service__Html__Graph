# ═══════════════════════════════════════════════════════════════════════════════
# Phase_E__Text_Extractor - Extract text nodes from body_graph with parent_id
# Part of Phase E: Virtual Merge and Selective Delete
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import Dict
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id               import Node_Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from phase_e.schemas.Schema__Phase_E__Text_Node_Info                            import Schema__Phase_E__Text_Node_Info


class Phase_E__Text_Extractor(Type_Safe):                                       # Extract text nodes from body_graph

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Extract Method
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def extract(self, document) -> Dict[Node_Id, Schema__Phase_E__Text_Node_Info]:                     # Extract text nodes indexed by node_id
        text_nodes = {}
        body_graph = document.body_graph
        mgraph     = body_graph.mgraph

        for domain_node in mgraph.data().nodes():
            node_path = domain_node.node.data.node_path

            if str(node_path) != 'text':                                        # Skip non-text nodes
                continue

            node_id   = str(domain_node.node.data.node_id)
            text      = self.get_text_value(domain_node)
            parent_id = self.get_parent_id(mgraph, node_id)

            if text.strip():                                                    # Only non-empty text
                text_nodes[node_id] = Schema__Phase_E__Text_Node_Info(text      = text,
                                                                      parent_id = parent_id)

        return text_nodes

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def get_text_value(self, domain_node) -> str:                               # Extract text value from node_data
        node_data = domain_node.node.data.node_data

        if node_data and hasattr(node_data, 'value'):
            return str(node_data.value) if node_data.value else ''

        return ''

    def get_parent_id(self, mgraph, node_id: Node_Id) -> Node_Id:                       # Find parent node_id via incoming edge
        index          = mgraph.index()
        incoming_edges = index.get_node_id_incoming_edges(node_id)

        for edge_id in incoming_edges:
            parent_id = index.edges_index.get_edge_from_node(edge_id)
            if parent_id:
                return str(parent_id)

        return ''