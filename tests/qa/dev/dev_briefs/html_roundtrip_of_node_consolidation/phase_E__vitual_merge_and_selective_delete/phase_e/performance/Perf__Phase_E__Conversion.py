# ═══════════════════════════════════════════════════════════════════════════════
# Perf__Phase_E__Conversion - Benchmark the 3 main conversion stages
# Part of Phase E_1: Performance Analysis
#
# Focus Areas:
#   1. HTML → Dict (Phase A parsing)
#   2. Dict → MGraph (graph generation with nodes/edges)
#   3. MGraph → HTML (recreation)
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                                     import Dict
from osbot_utils.helpers.Print_Table                                                                            import Print_Table
from osbot_utils.helpers.performance.Performance_Measure__Session                                               import Perf
from osbot_utils.type_safe.Type_Safe                                                                            import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                  import type_safe
from osbot_utils.type_safe.primitives.core.Safe_Int                                                             import Safe_Int
from osbot_utils.type_safe.primitives.core.Safe_Float                                                           import Safe_Float
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids            import Html__To__Html_Dict__With__Node_Ids
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html                import Html_MGraph__Document__To__Html




class Schema__Conversion_Timing(Type_Safe):                                     # Timing result for one conversion
    html_to_dict_ns   : Safe_Int                                                # HTML → Dict time in nanoseconds
    dict_to_mgraph_ns : Safe_Int                                                # Dict → MGraph time in nanoseconds
    mgraph_to_html_ns : Safe_Int                                                # MGraph → HTML time in nanoseconds
    total_ns          : Safe_Int                                                # Total time
    html_size_bytes   : Safe_Int                                                # Size of input HTML
    node_count        : Safe_Int                                                # Approximate node count


class Schema__Conversion_Breakdown(Type_Safe):                                  # Percentage breakdown
    html_to_dict_pct   : Safe_Float                                             # % time in HTML → Dict
    dict_to_mgraph_pct : Safe_Float                                             # % time in Dict → MGraph
    mgraph_to_html_pct : Safe_Float                                             # % time in MGraph → HTML


class Perf__Phase_E__Conversion(Type_Safe):                                     # Benchmark conversion stages

    session : Perf = None                                                       # Performance session

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.session is None:
            self.session = Perf(assert_enabled=False)

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Benchmark Method
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def benchmark_conversions(self, html: str) -> Schema__Conversion_Timing:    # Benchmark all 3 stages
        html_dict = None
        document  = None

        # Stage 1: HTML → Dict
        def stage_html_to_dict():
            nonlocal html_dict
            html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()

        # Stage 2: Dict → MGraph
        def stage_dict_to_mgraph():
            nonlocal document
            document = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)

        # Stage 3: MGraph → HTML
        def stage_mgraph_to_html():
            Html_MGraph__Document__To__Html().convert(document)

        with self.session as _:
            result_1 = _.measure__fast(stage_html_to_dict  ).result
            result_2 = _.measure__fast(stage_dict_to_mgraph).result
            result_3 = _.measure__fast(stage_mgraph_to_html).result

        html_to_dict_ns   = int(result_1.final_score)
        dict_to_mgraph_ns = int(result_2.final_score)
        mgraph_to_html_ns = int(result_3.final_score)
        total_ns          = html_to_dict_ns + dict_to_mgraph_ns + mgraph_to_html_ns

        return Schema__Conversion_Timing(html_to_dict_ns   = html_to_dict_ns  ,
                                         dict_to_mgraph_ns = dict_to_mgraph_ns,
                                         mgraph_to_html_ns = mgraph_to_html_ns,
                                         total_ns          = total_ns         ,
                                         html_size_bytes   = len(html)        ,
                                         node_count        = self.estimate_nodes(html))

    # ═══════════════════════════════════════════════════════════════════════════
    # Individual Stage Benchmarks
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def benchmark_html_to_dict(self, html: str) -> Safe_Int:                         # Benchmark Stage 1 only
        from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids import Html__To__Html_Dict__With__Node_Ids

        def run():
            Html__To__Html_Dict__With__Node_Ids(html=html).convert()

        with self.session as _:
            result = _.measure__fast(run)
            return _.result.final_score

    @type_safe
    def benchmark_dict_to_mgraph(self, html_dict: dict) -> Safe_Int:                 # Benchmark Stage 2 only

        def run():
            Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)

        with self.session as _:
            _.measure__fast(run)
            return _.result.final_score

    @type_safe
    def benchmark_mgraph_to_html(self, document) -> Safe_Int:                        # Benchmark Stage 3 only
        def run():
            Html_MGraph__Document__To__Html().convert(document)

        with self.session as _:
            result = _.measure__fast(run)
            return _.result.final_score


    # ═══════════════════════════════════════════════════════════════════════════
    # Analysis Methods
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def calculate_breakdown(self                               ,                # Calculate percentage breakdown
                            timing: Schema__Conversion_Timing  ) -> Schema__Conversion_Breakdown:
        total = float(timing.total_ns) or 1.0                                   # Avoid division by zero

        return Schema__Conversion_Breakdown(
            html_to_dict_pct   = round(float(timing.html_to_dict_ns)   / total * 100, 1),
            dict_to_mgraph_pct = round(float(timing.dict_to_mgraph_ns) / total * 100, 1),
            mgraph_to_html_pct = round(float(timing.mgraph_to_html_ns) / total * 100, 1))

    @type_safe
    def benchmark_multiple_sizes(self                  ,                        # Benchmark across multiple HTML sizes
                                 sizes: Dict[str, str] ) -> Dict[str, Schema__Conversion_Timing]:
        results = {}

        for name, html in sizes.items():
            results[name] = self.benchmark_conversions(html)

        return results

    # ═══════════════════════════════════════════════════════════════════════════
    # Reporting (Print_Table based)
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def build_report(self, timing: Schema__Conversion_Timing) -> str:           # Build single timing report
        breakdown = self.calculate_breakdown(timing)
        table     = Print_Table()

        table.set_title('CONVERSION TIMING REPORT')
        table.add_headers('Stage', 'Time', 'Percentage')

        table.add_row(['HTML → Dict'  , self.format_ns(int(timing.html_to_dict_ns))  , f'{float(breakdown.html_to_dict_pct):.1f}%'  ])
        table.add_row(['Dict → MGraph', self.format_ns(int(timing.dict_to_mgraph_ns)), f'{float(breakdown.dict_to_mgraph_pct):.1f}%'])
        table.add_row(['MGraph → HTML', self.format_ns(int(timing.mgraph_to_html_ns)), f'{float(breakdown.mgraph_to_html_pct):.1f}%'])
        table.add_row(['TOTAL'        , self.format_ns(int(timing.total_ns))         , '100%'                                       ])

        footer = f"HTML Size: {int(timing.html_size_bytes):,} bytes | Est. Nodes: {int(timing.node_count):,}"
        table.set_footer(footer)

        return table.text()

    @type_safe
    def build_multi_report(self                                    ,            # Build report for multiple sizes
                           results: Dict[str, Schema__Conversion_Timing]) -> str:

        table = Print_Table()

        table.set_title('CONVERSION TIMING BY SIZE')
        table.add_headers('Size', 'Total', 'HTML→Dict', 'Dict→MGraph', 'MGraph→HTML', 'Bytes')

        for name in sorted(results.keys()):
            timing    = results[name]
            breakdown = self.calculate_breakdown(timing)

            table.add_row([name                                                                  ,
                           self.format_ns(int(timing.total_ns))                                  ,
                           f'{self.format_ns(int(timing.html_to_dict_ns))} ({breakdown.html_to_dict_pct:.0f}%)'    ,
                           f'{self.format_ns(int(timing.dict_to_mgraph_ns))} ({breakdown.dict_to_mgraph_pct:.0f}%)',
                           f'{self.format_ns(int(timing.mgraph_to_html_ns))} ({breakdown.mgraph_to_html_pct:.0f}%)',
                           f'{int(timing.html_size_bytes):,}'                                    ])

        # Find bottleneck across all sizes
        total_html   = sum(int(t.html_to_dict_ns)   for t in results.values())
        total_mgraph = sum(int(t.dict_to_mgraph_ns) for t in results.values())
        total_rebuild = sum(int(t.mgraph_to_html_ns) for t in results.values())

        if total_html >= total_mgraph and total_html >= total_rebuild:
            bottleneck = 'HTML→Dict'
        elif total_mgraph >= total_rebuild:
            bottleneck = 'Dict→MGraph'
        else:
            bottleneck = 'MGraph→HTML'

        table.set_footer(f"Primary Bottleneck: {bottleneck}")

        return table.text()

    def save_report(self                           ,                            # Save report to file
                    timing   : Schema__Conversion_Timing,
                    filepath : str                 ) -> None:
        from osbot_utils.utils.Files import file_create
        file_create(filepath, self.build_report(timing))

    def print_report(self, timing: Schema__Conversion_Timing) -> None:          # Print report to console
        print(self.build_report(timing))

    @type_safe
    def format_timing(self, timing: Schema__Conversion_Timing) -> str:          # Format timing for display (legacy)
        breakdown = self.calculate_breakdown(timing)

        return (f"Total: {self.format_ns(int(timing.total_ns)):>12} | "
                f"HTML→Dict: {self.format_ns(int(timing.html_to_dict_ns)):>10} ({breakdown.html_to_dict_pct:>5.1f}%) | "
                f"Dict→MGraph: {self.format_ns(int(timing.dict_to_mgraph_ns)):>10} ({breakdown.dict_to_mgraph_pct:>5.1f}%) | "
                f"MGraph→HTML: {self.format_ns(int(timing.mgraph_to_html_ns)):>10} ({breakdown.mgraph_to_html_pct:>5.1f}%)")

    def format_ns(self, ns: int) -> str:                                        # Format nanoseconds for readability
        if ns >= 1_000_000_000:
            return f"{ns / 1_000_000_000:.2f}s"
        elif ns >= 1_000_000:
            return f"{ns / 1_000_000:.2f}ms"
        elif ns >= 1_000:
            return f"{ns / 1_000:.2f}µs"
        else:
            return f"{ns}ns"

    # ═══════════════════════════════════════════════════════════════════════════
    # Helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def estimate_nodes(self, html: str) -> int:                                 # Rough node estimate
        return html.count('<') - html.count('</')