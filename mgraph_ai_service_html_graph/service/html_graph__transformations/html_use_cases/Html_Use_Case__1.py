from typing                                                                                         import Any
from mgraph_db.mgraph.MGraph                                                                        import MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base    import Graph_Transformation__Base

# ═══════════════════════════════════════════════════════════════════════════
# Color Palette - Depth-based element colors
# ═══════════════════════════════════════════════════════════════════════════

DEPTH_COLORS = [
    '#E3F2FD',  # Depth 0 - lightest blue
    '#BBDEFB',  # Depth 1
    '#90CAF9',  # Depth 2
    '#64B5F6',  # Depth 3
    '#42A5F5',  # Depth 4
    '#2196F3',  # Depth 5+ - darker blue
]

TEXT_NODE_COLOR    = '#FFF9C4'   # Light yellow for text content
ELEMENT_NODE_COLOR = '#E8F4F8'   # Default element color

EDGE_CHILD_COLOR   = '#666666'   # Gray for structural edges
EDGE_TEXT_COLOR    = '#FFA726'   # Orange for text edges

class Html_Use_Case__1(Graph_Transformation__Base):

    name        : str    = "html-use-case-1"
    label       : str    = "Html Use Case #1 - Semantic DOM View"
    description : str    = "DOM structure with depth-based coloring and semantic edge labels"
    mgraph      : MGraph = None     # store for phase 5
    dot_code    : str

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 3: Transform MGraph - Apply MGraph-DB native DOT styling
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_mgraph(self, mgraph: MGraph) -> MGraph:
        if mgraph is None:
            return mgraph

        # Access MGraph's export system and configure DOT rendering
        with mgraph.export().export_dot() as dot:
            # ─────────────────────────────────────────────────────────────────
            # Layout Configuration
            # ─────────────────────────────────────────────────────────────────
            dot.set_graph__rank_dir__tb()              # Top-to-bottom hierarchy
            dot.set_graph__node_sep(0.4)               # Horizontal spacing
            dot.set_graph__rank_sep(0.6)               # Vertical spacing
            #dot.set_graph__splines__ortho()            # Right-angle edges
            dot.set_graph__splines__polyline()

            # ─────────────────────────────────────────────────────────────────
            # Node Display Options
            # ─────────────────────────────────────────────────────────────────
            dot.show_node__value()                     # Show node values/labels
            dot.show_node__path()
            dot.show_edge__predicate()                 # Show edge predicates (child, text)


            # ─────────────────────────────────────────────────────────────────
            # Global Node Styling
            # ─────────────────────────────────────────────────────────────────
            dot.set_node__shape__type__box()           # Box shape for all nodes
            dot.set_node__shape__rounded()             # Rounded corners
            dot.set_node__fill_color(ELEMENT_NODE_COLOR)

            # ─────────────────────────────────────────────────────────────────
            # Value Node Styling (text content nodes)
            # ─────────────────────────────────────────────────────────────────
            dot.set_value_type_fill_color(str, TEXT_NODE_COLOR)
            dot.set_value_type_font_color(str, '#333333')

            # ─────────────────────────────────────────────────────────────────
            # Edge Styling
            # ─────────────────────────────────────────────────────────────────
            dot.set_edge__color(EDGE_CHILD_COLOR)
            dot.set_edge__arrow_head__vee()

            self.dot_code = dot.process_graph()
        #self.mgraph = mgraph
        return mgraph

    def transform_export(self, output: Any) -> Any:
        return self.dot_code
        # dot_code = self.mgraph.export().to__dot()
        #
        # return dot_code