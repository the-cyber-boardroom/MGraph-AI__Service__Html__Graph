# ═══════════════════════════════════════════════════════════════════════════════
# Phase_E__Node_Deleter - Delete parent nodes from body_graph
# Part of Phase E: Virtual Merge and Selective Delete
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import List, Dict
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from osbot_utils.type_safe.primitives.core.Safe_Int                             import Safe_Int
from Phase_E__Decision_Engine__Base                                     import DecisionResult


class Phase_E__Node_Deleter(Type_Safe):                                         # Delete parent nodes from body_graph

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Delete Method
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def delete(self                       ,                                     # Delete parent nodes and their subtrees
               document                   ,                                     # Html_MGraph__Document to modify
               parent_ids : List[str]     ) -> int:                             # Number of nodes deleted
        deleted_count = 0
        body_graph    = document.body_graph.mgraph

        for parent_id in parent_ids:
            if self.delete_node(body_graph, parent_id) is True:
                deleted_count += 1

        return deleted_count

    # ═══════════════════════════════════════════════════════════════════════════
    # Single Node Deletion
    # ═══════════════════════════════════════════════════════════════════════════

    def delete_node(self, mgraph, node_id: str) -> bool:                        # Delete a single node from the graph
        try:
            mgraph.edit().delete_node(node_id)
            return True
        except Exception:
            return False                                                        # Node might already be deleted

    # ═══════════════════════════════════════════════════════════════════════════
    # Bulk Operations
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def delete_from_decisions(self                                   ,          # Delete nodes based on decision results
                              document                               ,          # Html_MGraph__Document to modify
                              decisions : Dict[str, DecisionResult]  ) -> int:  # Number of nodes deleted
        parents_to_delete = [parent_id
                             for parent_id, result in decisions.items()
                             if result.keep is False]

        return self.delete(document, parents_to_delete)