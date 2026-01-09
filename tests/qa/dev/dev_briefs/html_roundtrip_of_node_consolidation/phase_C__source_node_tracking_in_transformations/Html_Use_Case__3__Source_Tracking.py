# ═══════════════════════════════════════════════════════════════════════════════
# Html Use Case #3 - Flatten Transformation with Source Node Tracking
# Subclass that adds source tracking with MINIMAL overrides
# Only overrides methods that need tracking logic
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                           import List, Set, Dict
from mgraph_ai_service_html_graph.service.html_graph__transformations.html_use_cases.Html_Use_Case__3 import Html_Use_Case__3
from mgraph_db.mgraph.MGraph                                                                          import MGraph



class Html_Use_Case__3__Source_Tracking(Html_Use_Case__3):

    name           : str  = "html-use-case-3-flatten-source-tracking"
    label          : str  = "Html Use Case #3 - Flatten with Source Tracking"
    description    : str  = "Flatten transformation with source node tracking"
    source_mapping : Dict = None                                                # merged_node_id → [source_node_ids]
    wrapper_mapping: Dict = None                                                # wrapper_node_id → {parent_id, child_id}

    # ═══════════════════════════════════════════════════════════════════════════
    # Override: transform_mgraph - Reset mappings at start
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_mgraph(self, mgraph: MGraph) -> MGraph:
        self.source_mapping  = {}                                               # Reset for new transformation
        self.wrapper_mapping = {}
        return super().transform_mgraph(mgraph)                                 # Delegate to base class

    # ═══════════════════════════════════════════════════════════════════════════
    # Override: step_1 - Add wrapper tracking
    # ═══════════════════════════════════════════════════════════════════════════

    def step_1___add_shortcut_edges(self, mgraph: MGraph) -> Set:
        index            = mgraph.index()
        edges_to_add     = []
        wrapper_node_ids = set()

        for domain_node in mgraph.data().nodes():
            node_id   = domain_node.node.data.node_id
            node_path = domain_node.node.data.node_path
            tag       = self.extract_tag(str(node_path) if node_path else '')

            if tag.lower() not in {'a', 'abbr', 'b', 'bdo', 'big', 'cite', 'code', 'dfn', 'em', 'i',
                                   'kbd', 'mark', 'q', 'samp', 'small', 'span', 'strong', 'sub', 'sup',
                                   'tt', 'u', 'var'}:
                continue

            outgoing_edges = index.get_node_id_outgoing_edges(node_id)
            if len(outgoing_edges) != 1:
                continue

            child_edge_id  = next(iter(outgoing_edges))
            child_node_id  = index.edges_index.get_edge_to_node(child_edge_id)

            incoming_edges = index.get_node_id_incoming_edges(node_id)
            for parent_edge_id in incoming_edges:
                parent_node_id = index.edges_index.get_edge_from_node(parent_edge_id)

                edges_to_add.append({'from_node_id': parent_node_id,
                                     'to_node_id'  : child_node_id ,
                                     'wrapper_id'  : node_id       })

            wrapper_node_ids.add(node_id)

        for edge_info in edges_to_add:
            self.create_shortcut_edge(mgraph, edge_info)

            wrapper_id = edge_info.get('wrapper_id')                            # ← TRACKING ADDITION
            self.wrapper_mapping[str(wrapper_id)] = {                           # ← TRACKING ADDITION
                'parent_id': str(edge_info['from_node_id']),                    # ← TRACKING ADDITION
                'child_id' : str(edge_info['to_node_id'])                       # ← TRACKING ADDITION
            }                                                                   # ← TRACKING ADDITION

        return wrapper_node_ids

    # ═══════════════════════════════════════════════════════════════════════════
    # Override: step_3 - Add source tracking
    # ═══════════════════════════════════════════════════════════════════════════

    def step_3___merge_text_nodes(self, mgraph: MGraph):
        parents_to_process = self.find_parents_with_multiple_text_children(mgraph)

        for parent_node_id, text_children in parents_to_process.items():
            if len(text_children) < 2:
                continue

            source_node_ids = [str(child['node_id']) for child in text_children]  # ← TRACKING: Collect BEFORE merge

            merged_text = self.merge_text_values(text_children)
            merged_node = self.create_merged_text_node(mgraph, merged_text)
            merged_node_id = str(merged_node.node.data.node_id)

            self.source_mapping[merged_node_id] = source_node_ids               # ← TRACKING ADDITION

            mgraph.edit().new_edge(from_node_id = parent_node_id,
                                   to_node_id   = merged_node.node.data.node_id)

            for text_info in text_children:
                mgraph.edit().delete_node(text_info['node_id'])

    # ═══════════════════════════════════════════════════════════════════════════
    # NEW: Source Tracking Query Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def get_source_node_ids(self, merged_node_id: str) -> List[str]:            # Get original Node_Ids merged into this node
        if self.source_mapping is None:
            return []
        return self.source_mapping.get(str(merged_node_id), [])

    def get_wrapper_info(self, wrapper_node_id: str) -> Dict:                   # Get info about a collapsed wrapper element
        if self.wrapper_mapping is None:
            return {}
        return self.wrapper_mapping.get(str(wrapper_node_id), {})

    def get_all_source_mappings(self) -> Dict[str, List[str]]:                  # Get all source mappings
        if self.source_mapping is None:
            return {}
        return self.source_mapping.copy()

    def get_all_wrapper_mappings(self) -> Dict[str, Dict]:                      # Get all wrapper mappings
        if self.wrapper_mapping is None:
            return {}
        return self.wrapper_mapping.copy()