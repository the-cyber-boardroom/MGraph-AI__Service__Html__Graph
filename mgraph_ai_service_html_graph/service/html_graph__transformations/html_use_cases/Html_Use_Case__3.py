# ═══════════════════════════════════════════════════════════════════════════════
# Html Use Case #3 - Flatten Transformation
# Step 1: Add shortcut edges from grandparent to grandchild for inline wrappers
# Step 2: Remove the inline wrapper nodes
# Step 3: Merge text nodes into single consolidated node per parent
# Step 4: Collapse single-parent nodes (nodes with 1 parent and 1 child)
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                         import Any, List, Set, Dict
from mgraph_db.mgraph.MGraph                                                                        import MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base    import Graph_Transformation__Base
from mgraph_db.mgraph.schemas.Schema__MGraph__Node__Data                                            import Schema__MGraph__Node__Data
from mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value                                           import Schema__MGraph__Node__Value
from mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value__Data                                     import Schema__MGraph__Node__Value__Data

TEXT_NODE_COLOR    = '#FFF9C4'
ELEMENT_NODE_COLOR = '#E8F4F8'
EDGE_CHILD_COLOR   = '#666666'

# Inline tags that should be collapsed (formatting wrappers)
INLINE_TAGS = {'a', 'abbr', 'b', 'bdo', 'big', 'cite', 'code', 'dfn', 'em', 'i',
               'kbd', 'mark', 'q', 'samp', 'small', 'span', 'strong', 'sub', 'sup',
               'tt', 'u', 'var'}


class Html_Use_Case__3(Graph_Transformation__Base):

    name        : str    = "html-use-case-3"
    label       : str    = "Html Use Case #3"
    description : str    = "Flatten transformation - Collapse wrappers, merge text, consolidate parents"
    dot_code    : str    = None

    def transform_mgraph(self, mgraph: MGraph) -> MGraph:

        wrapper_node_ids = self.step_1___add_shortcut_edges(mgraph)                         # Step 1: Add shortcut edges
        self.step_2___remove_wrapper_nodes(mgraph, wrapper_node_ids)                        # Step 2: Remove wrapper nodes
        self.step_3___merge_text_nodes(mgraph)                                              # Step 3: Merge text nodes
        self.step_4___collapse_single_parents(mgraph)                                       # Step 4: Collapse single-parent nodes
        self.update_node_labels(mgraph)                                                     # Update labels for display

        self.dot_code = self.create_dot_code(mgraph)
        return mgraph

    # ═══════════════════════════════════════════════════════════════════════════
    # Step 1: Add Shortcut Edges
    # ═══════════════════════════════════════════════════════════════════════════

    def step_1___add_shortcut_edges(self, mgraph: MGraph) -> Set:                           # Add shortcuts, return wrapper node IDs
        index            = mgraph.index()
        edges_to_add     = []
        wrapper_node_ids = set()

        for domain_node in mgraph.data().nodes():                                           # Find single-child inline wrappers
            node_id   = domain_node.node.data.node_id
            node_path = domain_node.node.data.node_path
            tag       = self.extract_tag(str(node_path) if node_path else '')

            if tag.lower() not in INLINE_TAGS:                                              # Skip non-inline tags
                continue

            outgoing_edges = index.get_node_id_outgoing_edges(node_id)                      # Check if single-child wrapper
            if len(outgoing_edges) != 1:
                continue

            child_edge_id  = next(iter(outgoing_edges))                                     # Get the single child
            child_node_id  = index.edges_index.get_edge_to_node(child_edge_id)

            incoming_edges = index.get_node_id_incoming_edges(node_id)                      # Get parents of this wrapper
            for parent_edge_id in incoming_edges:
                parent_node_id = index.edges_index.get_edge_from_node(parent_edge_id)

                edges_to_add.append({'from_node_id': parent_node_id,                        # Queue shortcut edge
                                     'to_node_id'  : child_node_id })

            wrapper_node_ids.add(node_id)                                                   # Track wrapper for removal

        for edge_info in edges_to_add:                                                      # Create shortcut edges
            self.create_shortcut_edge(mgraph, edge_info)

        return wrapper_node_ids

    def create_shortcut_edge(self, mgraph: MGraph, edge_info: dict):                        # Create a shortcut edge
        from_node_id = edge_info['from_node_id']
        to_node_id   = edge_info['to_node_id']

        mgraph.edit().new_edge(from_node_id = from_node_id,
                               to_node_id   = to_node_id  )

    # ═══════════════════════════════════════════════════════════════════════════
    # Step 2: Remove Wrapper Nodes
    # ═══════════════════════════════════════════════════════════════════════════

    def step_2___remove_wrapper_nodes(self, mgraph: MGraph, wrapper_node_ids: Set):         # Remove inline wrapper nodes
        for node_id in wrapper_node_ids:
            mgraph.edit().delete_node(node_id)

    # ═══════════════════════════════════════════════════════════════════════════
    # Step 3: Merge Text Nodes
    # ═══════════════════════════════════════════════════════════════════════════

    def step_3___merge_text_nodes(self, mgraph: MGraph):                                    # Merge text children into single node
        index              = mgraph.index()
        parents_to_process = self.find_parents_with_multiple_text_children(mgraph)

        for parent_node_id, text_children in parents_to_process.items():
            if len(text_children) < 2:                                                      # Need at least 2 to merge
                continue

            merged_text     = self.merge_text_values(text_children)                         # Concatenate text values
            merged_node     = self.create_merged_text_node(mgraph, merged_text)             # Create new merged node
            merged_node_id  = merged_node.node.data.node_id

            mgraph.edit().new_edge(from_node_id = parent_node_id,                           # Connect parent to merged node
                                   to_node_id   = merged_node_id)

            for text_info in text_children:                                                 # Remove original text nodes
                mgraph.edit().delete_node(text_info['node_id'])

    # ═══════════════════════════════════════════════════════════════════════════
    # Step 4: Collapse Single-Parent Nodes
    # ═══════════════════════════════════════════════════════════════════════════

    def step_4___collapse_single_parents(self, mgraph: MGraph):                             # Collapse nodes with 1 parent and 1 child
        changed = True
        while changed:                                                                      # Iterate until no more changes
            changed = self.collapse_single_parents_pass(mgraph)

    def collapse_single_parents_pass(self, mgraph: MGraph) -> bool:                         # Single pass of collapsing
        index            = mgraph.index()
        collapse_info    = []                                                               # Collect candidates first

        for domain_node in mgraph.data().nodes():
            node_id   = domain_node.node.data.node_id
            node_path = domain_node.node.data.node_path

            if str(node_path) == 'text':                                                    # Skip text nodes
                continue

            incoming_edges = index.get_node_id_incoming_edges(node_id)
            outgoing_edges = index.get_node_id_outgoing_edges(node_id)

            if len(incoming_edges) != 1 or len(outgoing_edges) != 1:                        # Must have exactly 1 parent and 1 child
                continue

            parent_edge_id = next(iter(incoming_edges))
            child_edge_id  = next(iter(outgoing_edges))

            parent_node_id = index.edges_index.get_edge_from_node(parent_edge_id)
            child_node_id  = index.edges_index.get_edge_to_node(child_edge_id)

            if parent_node_id is None or child_node_id is None:                             # Safety check
                continue

            parent_incoming = index.get_node_id_incoming_edges(parent_node_id)              # Don't collapse if parent is root
            if len(parent_incoming) == 0:
                continue

            collapse_info.append({'node_id'       : node_id       ,
                                  'parent_node_id': parent_node_id,
                                  'child_node_id' : child_node_id })

        if not collapse_info:                                                               # No candidates
            return False

        nodes_to_collapse = {info['node_id'] for info in collapse_info}                     # Filter out nodes whose child is also collapsing
        safe_collapses    = [info for info in collapse_info
                             if info['child_node_id'] not in nodes_to_collapse]

        if not safe_collapses:                                                              # All candidates have chain conflicts
            return False

        for info in safe_collapses:                                                         # Create shortcut edges
            mgraph.edit().new_edge(from_node_id = info['parent_node_id'],
                                   to_node_id   = info['child_node_id'] )

        for info in safe_collapses:                                                         # Remove intermediate nodes
            mgraph.edit().delete_node(info['node_id'])

        return True

    def find_parents_with_multiple_text_children(self, mgraph: MGraph) -> Dict:             # Find parents that have multiple text children
        index   = mgraph.index()
        parents = {}                                                                        # parent_id → list of {node_id, value, position}

        for domain_node in mgraph.data().nodes():                                           # Find all text nodes
            node_id   = domain_node.node.data.node_id
            node_path = domain_node.node.data.node_path

            if str(node_path) != 'text':                                                    # Skip non-text nodes
                continue

            text_value     = self.get_text_value(domain_node)
            incoming_edges = index.get_node_id_incoming_edges(node_id)

            for edge_id in incoming_edges:                                                  # Get parent(s) of this text node
                parent_node_id = index.edges_index.get_edge_from_node(edge_id)
                position       = self.get_edge_position(mgraph, edge_id)

                if parent_node_id not in parents:
                    parents[parent_node_id] = []

                parents[parent_node_id].append({'node_id' : node_id   ,
                                                'value'   : text_value,
                                                'position': position  })

        return parents

    def get_text_value(self, domain_node) -> str:                                           # Extract text value from node
        node_data = domain_node.node.data.node_data
        if node_data and hasattr(node_data, 'value'):
            return str(node_data.value) if node_data.value else ''
        return ''

    def get_edge_position(self, mgraph: MGraph, edge_id) -> int:                            # Get edge position for ordering
        domain_edge = mgraph.data().edge(edge_id)
        if domain_edge and domain_edge.edge.data.edge_label:
            predicate = domain_edge.edge.data.edge_label.predicate
            if predicate:
                predicate_str = str(predicate)                                              # Try to extract position from predicate
                if ':' in predicate_str:
                    try:
                        return int(predicate_str.split(':')[-1])
                    except ValueError:
                        pass
        return 0

    def merge_text_values(self, text_children: List[Dict]) -> str:                          # Sort by position and concatenate
        sorted_children = sorted(text_children, key=lambda x: x.get('position', 0))
        return ''.join(child['value'] for child in sorted_children)

    def create_merged_text_node(self, mgraph: MGraph, text_value: str):                     # Create new text node with merged value

        node_data = Schema__MGraph__Node__Value__Data(value      = text_value,
                                                      value_type = str       )

        return mgraph.edit().new_node(node_type = Schema__MGraph__Node__Value,
                                      node_path = 'text'                     ,
                                      node_data = node_data                  )

    # ═══════════════════════════════════════════════════════════════════════════
    # Utility Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def extract_tag(self, node_path: str) -> str:                                           # Extract tag from path like 'body.div[0].a' → 'a'
        if not node_path:
            return ''
        last_part = node_path.split('.')[-1] if '.' in node_path else node_path
        if '[' in last_part:
            last_part = last_part[:last_part.index('[')]
        return last_part

    # ═══════════════════════════════════════════════════════════════════════════
    # Node Label Updates
    # ═══════════════════════════════════════════════════════════════════════════

    def update_node_labels(self, mgraph: MGraph):                                           # Update labels for display
        for domain_node in mgraph.data().nodes():
            if domain_node.node_data is None:
                domain_node.node_data = Schema__MGraph__Node__Data()

            node_path = domain_node.node.data.node_path
            if str(node_path) == 'text':
                value = self.get_text_value(domain_node)
                domain_node.node_data.value = self.wrap_text(value, width=30)               # Wrap text for display
            else:
                domain_node.node_data.value = str(node_path) if node_path else '[element]'

    def wrap_text(self, text: str, width: int = 30) -> str:                                 # Wrap text to multiple lines
        if not text or len(text) <= width:
            return text

        words  = text.split(' ')
        lines  = []
        line   = ''

        for word in words:
            if len(line) + len(word) + 1 <= width:
                line = f"{line} {word}" if line else word
            else:
                if line:
                    lines.append(line)
                line = word

        if line:
            lines.append(line)

        return '\\n'.join(lines)                                                            # DOT uses \n for newlines

    # ═══════════════════════════════════════════════════════════════════════════
    # DOT Code Generation
    # ═══════════════════════════════════════════════════════════════════════════

    def create_dot_code(self, mgraph: MGraph) -> str:
        with mgraph.export().export_dot() as dot:
            dot.set_graph__splines__polyline()
            dot.show_node__value()
            dot.show_edge__predicate__str()
            dot.set_node__shape__type__box()
            dot.set_node__shape__rounded()
            dot.set_node__fill_color(ELEMENT_NODE_COLOR)
            dot.set_value_type_fill_color(str, TEXT_NODE_COLOR)
            dot.set_value_type_font_color(str, '#333333')
            dot.set_edge__color(EDGE_CHILD_COLOR)
            dot.set_edge__arrow_head__vee()
            return dot.process_graph()

    def transform_export(self, output: Any) -> Any:
        return self.dot_code