# ═══════════════════════════════════════════════════════════════════════════════
# Phase_E__Virtual_Merger - Compute merged text per parent (read-only)
# Part of Phase E: Virtual Merge and Selective Delete
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import Dict, List
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                             import Safe_Str__Text


class MergedTextInfo(Type_Safe):                                                # Info about merged text
    merged_text      : Safe_Str__Text                                                 # Combined text content
    source_node_ids  : List[str]                                                # Original text node_ids


class Phase_E__Virtual_Merger(Type_Safe):                                       # Compute merged text per parent (read-only)

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Merge Method
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def merge(self                            ,                                 # Group text nodes by parent and merge
              text_nodes : Dict[str, object]  ,                                 # Output from Phase_E__Text_Extractor
              document                        ) -> Dict[str, MergedTextInfo]:   # Dict mapping parent_id → merged info
        by_parent = self.group_by_parent(text_nodes, document)                  # Group by parent
        merged    = self.merge_groups(by_parent)                                # Merge each group

        return merged

    # ═══════════════════════════════════════════════════════════════════════════
    # Grouping
    # ═══════════════════════════════════════════════════════════════════════════

    def group_by_parent(self                            ,                       # Group text nodes by their parent_id
                        text_nodes : Dict[str, object]  ,
                        document                        ) -> Dict[str, List[dict]]:
        by_parent = {}

        for node_id, info in text_nodes.items():
            parent_id = str(info.parent_id)
            position  = self.get_position(document, node_id)

            if parent_id not in by_parent:
                by_parent[parent_id] = []

            by_parent[parent_id].append({'node_id' : node_id       ,
                                         'text'    : str(info.text),
                                         'position': position      })

        return by_parent

    # ═══════════════════════════════════════════════════════════════════════════
    # Merging
    # ═══════════════════════════════════════════════════════════════════════════

    def merge_groups(self                                  ,                    # Merge text nodes for each parent
                     by_parent: Dict[str, List[dict]]      ) -> Dict[str, MergedTextInfo]:
        merged = {}

        for parent_id, children in by_parent.items():
            sorted_children = sorted(children, key=lambda x: x['position'])     # Sort by position

            merged[parent_id] = MergedTextInfo(
                merged_text     = ''.join(c['text'] for c in sorted_children),
                source_node_ids = [c['node_id'] for c in sorted_children]    )

        return merged

    # ═══════════════════════════════════════════════════════════════════════════
    # Position Lookup
    # ═══════════════════════════════════════════════════════════════════════════

    def get_position(self, document, node_id: str) -> int:                      # Get position from edge_path for ordering
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