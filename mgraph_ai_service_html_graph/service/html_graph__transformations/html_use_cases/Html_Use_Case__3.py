from typing                                                                                         import Any
from mgraph_db.mgraph.MGraph                                                                        import MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base    import Graph_Transformation__Base
from mgraph_db.mgraph.schemas.Schema__MGraph__Node__Data                                            import Schema__MGraph__Node__Data

TEXT_NODE_COLOR    = '#FFF9C4'
ELEMENT_NODE_COLOR = '#E8F4F8'
EDGE_CHILD_COLOR   = '#666666'

class Html_Use_Case__3(Graph_Transformation__Base):

    name        : str    = "html-use-case-3"
    label       : str    = "Html Use Case #3"
    description : str    = "Clean DOM view with semantic labels"
    dot_code    : str    = None

    def transform_mgraph(self, mgraph: MGraph) -> MGraph:
        # Simplify node labels to just show path or text value
        for domain_node in mgraph.data().nodes():
            if domain_node.node_data is None:
                domain_node.node_data = Schema__MGraph__Node__Data()

            node_path = domain_node.node.data.node_path
            if node_path == 'text':
                # For text nodes, show the actual text content
                value = getattr(domain_node.node.data.node_data, 'value', '') or ''
                domain_node.node_data.value = value[:40] + '...' if len(value) > 40 else value
            else:
                # For element nodes, show just the path
                domain_node.node_data.value = str(node_path) if node_path else '[element]'

        self.dot_code = self.create_dot_code(mgraph)
        return mgraph

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