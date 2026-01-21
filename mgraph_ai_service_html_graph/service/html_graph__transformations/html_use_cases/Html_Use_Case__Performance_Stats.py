from typing                                                                                         import Any
from mgraph_db.mgraph.MGraph                                                                        import MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base    import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                   import Html_MGraph
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document    import Html__To__Html_MGraph__Document
from osbot_utils.helpers.timestamp_capture.Timestamp_Collector                                      import Timestamp_Collector
from osbot_utils.helpers.timestamp_capture.actions.Timestamp_Collector__Analysis import Timestamp_Collector__Analysis

from osbot_utils.helpers.timestamp_capture.context_managers.timestamp_block import timestamp_block

# ═══════════════════════════════════════════════════════════════════════════
# Color Configuration
# ═══════════════════════════════════════════════════════════════════════════

COLOR_ROOT          = '#1565C0'    # Dark blue for root
COLOR_METRIC        = '#FFF9C4'    # Yellow for metric values
COLOR_HOTSPOT       = '#FFCDD2'    # Light red for hot methods
COLOR_NORMAL        = '#E3F2FD'    # Light blue for normal methods
COLOR_EDGE          = '#78909C'    # Blue-gray edges


class Html_Use_Case__Performance_Stats(Graph_Transformation__Base):
    """Performance Statistics Visualization using Timestamp_Collector.

    Demonstrates pipeline takeover with proper timing instrumentation:
    - Phase 1: Wraps HTML parsing with Timestamp_Collector
    - Phase 2: Uses Analysis API to extract method timings
    - Phase 3: Builds visualization graph showing hotspots and call hierarchy

    The output shows actual method-level performance data with self-time analysis.
    """

    name        : str                 = "html-use-case-performance-stats"
    label       : str                 = "Performance Stats"
    description : str                 = "Visualize HTML parsing performance with timestamp analysis"

    # Storage for pipeline
    collector             : Timestamp_Collector = None
    _timestamp_collector_ : Timestamp_Collector = None
    dot_code               : str                 = None

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 1: Intercept HTML parsing with Timestamp_Collector
    # ═══════════════════════════════════════════════════════════════════════════

    def html__to__html_mgraph(self, html: str) -> Html_MGraph:
        """Parse HTML with timestamp instrumentation.

        Uses Timestamp_Collector to capture method-level timing data.
        Returns None to signal pipeline takeover.
        """
        self.collector        = Timestamp_Collector(name="html_mgraph_parsing")
        _timestamp_collector_ = self.collector
        with self.collector:
            with timestamp_block("phase.html-to-html_mgraph"):
                with Html__To__Html_MGraph__Document() as converter:
                    converter.convert(html)

        return None  # Signal: skip normal html_mgraph processing

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 2: Build stats visualization graph from collector data
    # ═══════════════════════════════════════════════════════════════════════════

    def html_mgraph__to__mgraph(self, html_mgraph: Html_MGraph) -> MGraph:
        """Build visualization graph from collected timestamps.

        Uses Timestamp_Collector__Analysis to compute method timings,
        then builds a graph showing the performance breakdown.
        """
        if not self.collector:
            return None

        analysis = Timestamp_Collector__Analysis(collector=self.collector)
        timings  = analysis.get_timings_by_total()
        hotspots = analysis.get_hotspots(top_n=5)
        hotspot_names = {h.name for h in hotspots}

        mgraph = MGraph()

        with mgraph.builder() as builder:
            # Root node: Overall stats
            total_ms = self.collector.total_duration_ms()
            builder.add_node(f"Html_MGraph Parsing")

            # Summary predicates
            builder.add_predicate("total_time", f"{total_ms:.2f} ms")
            builder.root()
            builder.add_predicate("methods_traced", str(self.collector.method_count()))
            builder.root()
            builder.add_predicate("entry_count", str(self.collector.entry_count()))
            builder.root()

            # Add method timing nodes (top methods by total time)
            total_ns = self.collector.total_duration_ns()

            for mt in timings[:10]:  # Top 10 methods
                pct = (mt.total_ns / total_ns * 100) if total_ns > 0 else 0

                # Create method node
                is_hotspot = mt.name in hotspot_names
                label = f"{'🔥 ' if is_hotspot else ''}{mt.name}"
                builder.add_connected_node(label)

                # Add timing predicates
                total_ms = mt.total_ns / 1_000_000
                self_ms  = mt.self_ns / 1_000_000

                builder.add_predicate("total", f"{total_ms:.2f} ms ({pct:.1f}%)")
                builder.up()
                builder.add_predicate("self", f"{self_ms:.2f} ms")
                # builder.up()
                # builder.add_predicate("calls", str(mt.call_count))

                builder.root()

        # from osbot_utils.helpers.timestamp_capture.Timestamp_Collector__Report import Timestamp_Collector__Report
        # report = Timestamp_Collector__Report(collector=self.collector)
        # report.print_all()

        return mgraph

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 3: Generate DOT via MGraph-DB's native export
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_mgraph(self, mgraph: MGraph) -> MGraph:
        """Configure MGraph-DB's DOT export and generate the DOT code."""
        if mgraph is None:
            return None

        self.dot_code = self._create_dot_code(mgraph)
        return None  # Signal: skip engine processing

    def _create_dot_code(self, mgraph: MGraph) -> str:
        """Generate DOT using MGraph-DB's native export system."""
        with mgraph.export().export_dot() as dot:
            # Layout
            dot.set_graph__rank_dir__tb()
            #dot.set_graph__splines__ortho()
            dot.set_graph__splines__polyline()

            dot.set_graph__node_sep(0.5)
            dot.set_graph__rank_sep(0.6)

            # Node display
            dot.show_node__value()
            dot.show_edge__predicate__str()

            # Node styling
            dot.set_node__shape__type__box()
            dot.set_node__shape__rounded()
            dot.set_node__fill_color(COLOR_NORMAL)

            # Value nodes (metrics) styling
            dot.set_value_type_fill_color(str, COLOR_METRIC)
            dot.set_value_type_font_color(str, '#333333')

            # Edge styling
            dot.set_edge__color(COLOR_EDGE)
            dot.set_edge__arrow_head__vee()

            return dot.process_graph()

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 5: Return the generated DOT code
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_export(self, output: Any) -> Any:
        """Return our generated DOT code instead of engine output."""
        return self.dot_code