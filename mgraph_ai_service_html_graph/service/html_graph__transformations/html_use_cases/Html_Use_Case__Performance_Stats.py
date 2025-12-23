from typing                                                                                         import Any, Dict
from time                                                                                           import perf_counter
from mgraph_db.mgraph.MGraph                                                                        import MGraph
from mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value                                           import Schema__MGraph__Node__Value
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base    import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                   import Html_MGraph
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document    import Html__To__Html_MGraph__Document
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document                  import Html_MGraph__Document
from osbot_utils.helpers.html.transformers.Html__To__Html_Dict                                      import Html__To__Html_Dict


# ═══════════════════════════════════════════════════════════════════════════
# Custom Value Types for Semantic Coloring
# ═══════════════════════════════════════════════════════════════════════════

class Metric__Time(str):          pass    # For timing values (e.g., "48.96 ms")
class Metric__Count(str):         pass    # For count values (e.g., "38")
class Metric__Graph_Name(str):    pass    # For graph names (e.g., "Body Graph")


# ═══════════════════════════════════════════════════════════════════════════
# Color Configuration
# ═══════════════════════════════════════════════════════════════════════════

COLOR_ROOT          = '#1565C0'    # Dark blue for root node
COLOR_TIME          = '#C8E6C9'    # Light green for timing
COLOR_COUNT         = '#BBDEFB'    # Light blue for counts
COLOR_GRAPH_NAME    = '#E1BEE7'    # Light purple for graph names
COLOR_EDGE          = '#78909C'    # Blue-gray edges

# Per-graph colors
GRAPH_COLORS = {
    'body'   : '#E3F2FD',    # Blue
    'head'   : '#E8F5E9',    # Green
    'attrs'  : '#FFF3E0',    # Orange
    'scripts': '#FCE4EC',    # Pink
    'styles' : '#F3E5F5',    # Purple
}


class Html_Use_Case__Performance_Stats(Graph_Transformation__Base):
    """Performance Statistics Visualization with semantic coloring."""

    name        : str  = "html-use-case-performance-stats"
    label       : str  = "Performance Stats"
    description : str  = "Visualize HTML parsing performance metrics"

    stats       : Dict = None
    dot_code    : str  = None

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 1: Intercept HTML parsing and collect timing stats
    # ═══════════════════════════════════════════════════════════════════════════

    def html__to__html_mgraph(self, html: str) -> Html_MGraph:
        self.stats = self._parse_with_timing(html)
        return None

    def _parse_with_timing(self, html: str) -> Dict:
        stats = {
            'total_time_ms'    : 0,
            'html_dict_time_ms': 0,
            'document_time_ms' : 0,
            'graphs'           : {}
        }

        total_start = perf_counter()

        t0 = perf_counter()
        html_dict = Html__To__Html_Dict(html=html).convert()
        stats['html_dict_time_ms'] = round((perf_counter() - t0) * 1000, 2)

        t0 = perf_counter()
        converter = Html__To__Html_MGraph__Document()
        document  = converter.convert_from_dict(html_dict)
        stats['document_time_ms'] = round((perf_counter() - t0) * 1000, 2)

        stats['graphs'] = self._collect_graph_stats(document)
        stats['total_time_ms'] = round((perf_counter() - total_start) * 1000, 2)

        return stats

    def _collect_graph_stats(self, document: Html_MGraph__Document) -> Dict:
        graphs = {}

        graph_sources = [
            ('body'   , document.body_graph   ),
            ('head'   , document.head_graph   ),
            ('attrs'  , document.attrs_graph  ),
            ('scripts', document.scripts_graph),
            ('styles' , document.styles_graph ),
        ]

        for name, graph in graph_sources:
            if graph and graph.mgraph:
                mg = graph.mgraph
                graphs[name] = {
                    'nodes': len(mg.data().nodes_ids()),
                    'edges': len(mg.data().edges_ids()),
                }

        return graphs

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 2: Build stats visualization graph with typed values
    # ═══════════════════════════════════════════════════════════════════════════

    def html_mgraph__to__mgraph(self, html_mgraph: Html_MGraph) -> MGraph:
        if not self.stats:
            return None

        mgraph = MGraph()

        with mgraph.builder() as builder:
            # Root node
            builder.add_node("Html_MGraph Performance")

            # Timing metrics (green)
            builder.add_predicate("total_time", Metric__Time(f"{self.stats['total_time_ms']} ms"))
            builder.root()
            builder.add_predicate("parse_html", Metric__Time(f"{self.stats['html_dict_time_ms']} ms"))
            builder.root()
            builder.add_predicate("build_graphs", Metric__Time(f"{self.stats['document_time_ms']} ms"))
            builder.root()

            # Total counts (blue)
            total_nodes = sum(g.get('nodes', 0) for g in self.stats['graphs'].values())
            total_edges = sum(g.get('edges', 0) for g in self.stats['graphs'].values())

            builder.add_predicate("total_nodes", Metric__Count(str(total_nodes)))
            builder.root()
            builder.add_predicate("total_edges", Metric__Count(str(total_edges)))
            builder.root()

            # Per-graph breakdown
            for graph_name, graph_stats in self.stats['graphs'].items():
                if graph_stats['nodes'] > 0 or graph_stats['edges'] > 0:
                    # Graph name node (purple)
                    builder.add_connected_node(Metric__Graph_Name(f"{graph_name.title()} Graph"))

                    # Metrics (blue)
                    builder.add_predicate("nodes", Metric__Count(str(graph_stats['nodes'])))
                    builder.up()
                    builder.add_predicate("edges", Metric__Count(str(graph_stats['edges'])))

                    builder.root()

        return mgraph

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 3: Configure DOT with type-based coloring
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_mgraph(self, mgraph: MGraph) -> MGraph:
        if mgraph is None:
            return None

        self.dot_code = self._create_dot_code(mgraph)
        return None

    def _create_dot_code(self, mgraph: MGraph) -> str:
        with mgraph.export().export_dot() as dot:
            # Layout
            dot.set_graph__rank_dir__tb()
            dot.set_graph__splines__ortho()
            dot.set_graph__node_sep(0.4)
            dot.set_graph__rank_sep(0.5)

            # Display
            dot.show_node__value()
            dot.show_edge__predicate__str()

            # Node styling
            dot.set_node__shape__type__box()
            dot.set_node__shape__rounded()
            dot.set_node__fill_color('#E0E0E0')      # Default gray

            # Type-based coloring for our custom metric types
            dot.set_value_type_fill_color(Metric__Time      , COLOR_TIME      )
            dot.set_value_type_fill_color(Metric__Count     , COLOR_COUNT     )
            dot.set_value_type_fill_color(Metric__Graph_Name, COLOR_GRAPH_NAME)

            # Edge styling
            dot.set_edge__color(COLOR_EDGE)
            dot.set_edge__arrow_head__vee()

            return dot.process_graph()

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 5: Return generated DOT
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_export(self, output: Any) -> Any:
        return self.dot_code