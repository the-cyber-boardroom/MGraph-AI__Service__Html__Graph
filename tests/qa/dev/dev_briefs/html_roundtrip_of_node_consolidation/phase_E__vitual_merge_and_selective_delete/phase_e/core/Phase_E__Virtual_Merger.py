# ═══════════════════════════════════════════════════════════════════════════════
# Phase_E__Virtual_Merger - Compute merged text per parent (read-only)
# Part of Phase E: Virtual Merge and Selective Delete
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import Dict, List
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id import Node_Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from phase_e.schemas.Schema__Phase_E__Merged_Text_Info                          import Schema__Phase_E__Merged_Text_Info
from phase_e.schemas.Schema__Phase_E__Text_Node_Info import Schema__Phase_E__Text_Node_Info


class Phase_E__Virtual_Merger(Type_Safe):                                       # Compute merged text per parent (read-only)

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Merge Method
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def merge(self                            ,                                 # Group text nodes by parent and merge
              text_nodes : Dict[Node_Id, object]  ,                                 # Output from Phase_E__Text_Extractor
              document                        ) -> Dict[Node_Id, Schema__Phase_E__Merged_Text_Info]:   # Dict mapping parent_id → merged info
        by_parent = self.group_by_parent(text_nodes, document)                  # Group by parent
        merged    = self.merge_groups(by_parent)                                # Merge each group

        return merged

    # ═══════════════════════════════════════════════════════════════════════════
    # Grouping
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def group_by_parent(self                            ,                       # Group text nodes by their parent_id
                        text_nodes : Dict[Node_Id, Schema__Phase_E__Text_Node_Info]  ,
                        document                        ) -> Dict[Node_Id, List[dict]]:
        by_parent = {}

        for node_id, info in text_nodes.items():
            parent_id = info.parent_id
            position  = self.get_position(document, node_id)

            if parent_id not in by_parent:
                by_parent[parent_id] = []

            by_parent[parent_id].append({'node_id' : node_id       ,
                                         'text'    : info.text,
                                         'position': position      })

        return by_parent

    # ═══════════════════════════════════════════════════════════════════════════
    # Merging
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def merge_groups(self                                  ,                    # Merge text nodes for each parent
                     by_parent: Dict[Node_Id, List[dict]]      ) -> Dict[Node_Id, Schema__Phase_E__Merged_Text_Info]:
        merged = {}

        for parent_id, children in by_parent.items():
            sorted_children = sorted(children, key=lambda x: x['position'])     # Sort by position

            merged[parent_id] = Schema__Phase_E__Merged_Text_Info(
                merged_text     = ''.join(c['text'] for c in sorted_children),
                source_node_ids = [c['node_id'] for c in sorted_children]    )

        return merged

    # ═══════════════════════════════════════════════════════════════════════════
    # Position Lookup
    # ═══════════════════════════════════════════════════════════════════════════

    def get_position(self, document, node_id: Node_Id) -> int:                      # Get position from edge_path for ordering
        body_graph = document.body_graph
        mgraph     = body_graph.mgraph
        index      = mgraph.index()

        incoming_edges = index.get_node_id_incoming_edges(node_id)

        for edge_id in incoming_edges:
            edge_data = mgraph.data().edge(edge_id)

            if edge_data and hasattr(edge_data, 'edge_path'):
                try:
                    return int(str(edge_data.edge_path))
                except (ValueError, TypeError):
                    pass

        return 0