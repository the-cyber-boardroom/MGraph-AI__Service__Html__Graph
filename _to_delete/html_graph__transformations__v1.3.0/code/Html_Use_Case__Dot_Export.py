# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Use Case DOT Export Helper
# v0.3.0 - DOT export configuration for use case transformations
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                              import Type_Safe
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph import Html_MGraph


class Html_Use_Case__Dot_Export(Type_Safe):
    """Helper for DOT export with use-case-specific configurations."""

    html_mgraph: Html_MGraph

    def mgraph(self):
        """Get the body graph's underlying MGraph for DOT export."""
        if self.html_mgraph.document and self.html_mgraph.body_graph:
            return self.html_mgraph.body_graph.mgraph
        return None

    def dot_string(self, transformation: str) -> str:
        """Generate DOT string based on transformation type."""
        if transformation == "clean":
            return self.dot_string__clean()
        elif transformation == "semantic":
            return self.dot_string__semantic()
        return ""

    def dot_string__clean(self) -> str:
        """DOT export for clean view."""
        mgraph = self.mgraph()
        if not mgraph:
            return ""

        with mgraph.export().export_dot() as _:
            self._apply_config__clean(_)
            return _.process_graph()

    def dot_string__semantic(self) -> str:
        """DOT export for semantic view."""
        mgraph = self.mgraph()
        if not mgraph:
            return ""

        with mgraph.export().export_dot() as _:
            self._apply_config__semantic(_)
            return _.process_graph()

    def _apply_config__clean(self, export_dot):
        """Configure DOT export for clean view."""
        (export_dot
            .show_node__value()
            .show_node__path()
            .show_edge__path__str()
            .set_graph__rank_dir__lr()
            .set_node__shape__type__box()
            .set_node__shape__rounded()
            .set_value_type_fill_color(str, '#B3D1F8'))
        return self

    def _apply_config__semantic(self, export_dot):
        """Configure DOT export for semantic view."""
        (export_dot
            .show_node__value()
            .show_node__path()
            .set_node__font__size(20)
            .show_edge__path__str()
            .set_graph__splines__polyline()
            .set_graph__rank_dir__tb()
            .set_node__shape__type__box()
            .set_node__shape__rounded()
            .set_value_type_fill_color(str, '#B3D1F8'))
        return self