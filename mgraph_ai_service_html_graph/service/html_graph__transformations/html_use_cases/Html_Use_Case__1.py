from typing                                                                                         import Any
from mgraph_db.mgraph.MGraph                                                                        import MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base    import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Dot       import MGraph__Engine__Config__Dot
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__D3        import MGraph__Engine__Config__D3
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Cytoscape import MGraph__Engine__Config__Cytoscape
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__VisJs     import MGraph__Engine__Config__VisJs
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Mermaid   import MGraph__Engine__Config__Mermaid
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Tree      import MGraph__Engine__Config__Tree


class Html_Use_Case__1(Graph_Transformation__Base):
    """HTML DOM Visualization with semantic styling.

    This transformation demonstrates leveraging MGraph-DB's powerful DOT export
    capabilities to create a semantically-styled visualization of HTML structure.

    Features:
    - Color-coded nodes by DOM depth
    - Distinct styling for text nodes vs element nodes
    - Predicate-labeled edges (child, text)
    - Clean hierarchical layout
    """

    name        : str = "html-use-case-1"
    label       : str = "Html Use Case #1 - Semantic DOM View"
    description : str = "DOM structure with depth-based coloring and semantic edge labels"

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

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 3: Transform MGraph - Apply MGraph-DB native DOT styling
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_mgraph(self, mgraph: MGraph) -> MGraph:
        """Apply MGraph-DB's powerful DOT export configuration.

        This leverages the native export_dot() context manager to configure
        node/edge styling based on types, values, and relationships.
        """
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
            dot.set_graph__splines__ortho()            # Right-angle edges

            # ─────────────────────────────────────────────────────────────────
            # Node Display Options
            # ─────────────────────────────────────────────────────────────────
            dot.show_node__value()                     # Show node values/labels
            dot.show_edge__predicate()                 # Show edge predicates (child, text)

            # ─────────────────────────────────────────────────────────────────
            # Global Node Styling
            # ─────────────────────────────────────────────────────────────────
            dot.set_node__shape__type__box()           # Box shape for all nodes
            dot.set_node__shape__rounded()             # Rounded corners
            dot.set_node__fill_color(self.ELEMENT_NODE_COLOR)

            # ─────────────────────────────────────────────────────────────────
            # Value Node Styling (text content nodes)
            # ─────────────────────────────────────────────────────────────────
            dot.set_value_type_fill_color(str, self.TEXT_NODE_COLOR)
            dot.set_value_type_font_color(str, '#333333')

            # ─────────────────────────────────────────────────────────────────
            # Edge Styling
            # ─────────────────────────────────────────────────────────────────
            dot.set_edge__color(self.EDGE_CHILD_COLOR)
            dot.set_edge__arrow_head__vee()

        return mgraph