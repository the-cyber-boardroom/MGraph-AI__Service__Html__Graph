from typing                                                                                         import Any
from mgraph_db.mgraph.MGraph                                                                        import MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base    import Graph_Transformation__Base
from mgraph_db.mgraph.schemas.Schema__MGraph__Node__Data                                            import Schema__MGraph__Node__Data
from mgraph_db.utils.testing.mgraph_test_ids import mgraph_test_ids
from osbot_utils.utils.Json                                                                         import json_to_str

# ═══════════════════════════════════════════════════════════════════════════
# Color Palette - Depth-based element colors
# ═══════════════════════════════════════════════════════════════════════════

TEXT_NODE_COLOR    = '#FFF9C4'   # Light yellow for text content
ELEMENT_NODE_COLOR = '#E8F4F8'   # Default element color

EDGE_CHILD_COLOR   = '#666666'   # Gray for structural edges
EDGE_TEXT_COLOR    = '#FFA726'   # Orange for text edges

class Html_Use_Case__2(Graph_Transformation__Base):

    name        : str    = "html-use-case-2"
    label       : str    = "Html Use Case #2"
    description : str    = "Html Use Case #2"
    mgraph      : MGraph = None     # store for phase 5
    dot_code    : str

    # ═══════════════════════════════════════════════════════════════════════════════════
    # Phase 1: HTML → Html_MGraph
    # ═══════════════════════════════════════════════════════════════════════════════════
    def html__to__html_mgraph(self, html: str):                                          # Convert HTML to Html_MGraph
        with mgraph_test_ids():
            mgraph = super().html__to__html_mgraph(html=html)
        return mgraph

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 3: Transform MGraph - Apply MGraph-DB native DOT styling
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_mgraph(self, mgraph: MGraph) -> MGraph:

        for domain_node in mgraph.data().nodes():
            if domain_node.node_data is None:                               # make sure there is an node_data
                domain_node.node_data = Schema__MGraph__Node__Data()

            node_json = domain_node.node.data.json()                        # get the json value of the current data
            del node_json['node_type']                                      # remove this field which doesn't add much value

            value = json_to_str(node_json).replace('"', '\'').replace('\n', '\l') + '\l'    # format the json data (using \l so that it shows left aligned)
            domain_node.node_data.value = f"{value}"                                        # overwrite the value of node_data

        self.dot_code = self.create_dot_code(mgraph)


    def create_dot_code(self, mgraph: MGraph) -> str:

        # Access MGraph's export system and configure DOT rendering
        with mgraph.export().export_dot() as dot:
            dot.set_graph__splines__polyline()


            # ─────────────────────────────────────────────────────────────────
            # Node Display Options
            # ─────────────────────────────────────────────────────────────────
            dot.show_node__value()                          # Show node values/labels
            dot.show_edge__predicate__str()                 # Show edge predicates (child, text)


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

            return dot.process_graph()


    def transform_export(self, output: Any) -> Any:
        return self.dot_code