# ═══════════════════════════════════════════════════════════════════════════════
# Performance Test: Phase E Conversion Detailed Breakdown
# Analyzes: HTML → Dict → MGraph → HTML conversion pipeline
# ═══════════════════════════════════════════════════════════════════════════════
#
# PURPOSE: Isolate WHERE time is spent in each conversion stage
#
# SECTIONS:
#   A_xx - Full operations (create converter + convert)
#   B_xx - Converter creation only
#   C_xx - Conversion only (pre-created converters)
#
# KEY QUESTION: Is the bottleneck in converter creation or conversion logic?
#
# ANSWER FROM DATA:
#   - Converter creation: ~1µs (negligible)
#   - Conversion logic:   ~14ms (the actual bottleneck)
#
# ═══════════════════════════════════════════════════════════════════════════════

import phase_e
from datetime                                                                                                   import datetime
from unittest                                                                                                   import TestCase
from mgraph_ai_service_html_graph.utils.Version                                                                 import version__mgraph_ai_service_html_graph
from osbot_utils.helpers.Print_Table                                                                            import Print_Table
from osbot_utils.helpers.performance.benchmark.Perf_Benchmark__Timing                                           import Perf_Benchmark__Timing
from osbot_utils.helpers.performance.benchmark.schemas.timing.Schema__Perf_Benchmark__Timing__Config            import Schema__Perf_Benchmark__Timing__Config
from osbot_utils.utils.Files                                                                                    import path_combine
from phase_e.performance.Perf__Storage__Local                                                                   import Perf__Storage__Local

from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids            import Html__To__Html_Dict__With__Node_Ids
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html                import Html_MGraph__Document__To__Html


# ═══════════════════════════════════════════════════════════════════════════════
# Test HTML
# ═══════════════════════════════════════════════════════════════════════════════

HTML_SIMPLE = "<html><body><div><p>Hello World</p></div></body></html>"


# ═══════════════════════════════════════════════════════════════════════════════
# Performance Test
# ═══════════════════════════════════════════════════════════════════════════════

class test_perf__Phase_E__Conversion__Detailed(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.storage_path = path_combine(phase_e.path, '../perf_results')
        cls.storage      = Perf__Storage__Local(storage_path=cls.storage_path)
        cls.config       = Schema__Perf_Benchmark__Timing__Config(
            title            = 'Phase E Conversion Detailed',
            measure_fast     = True,
            print_to_console = False,
            asserts_enabled  = False
        )

    def test__conversion_detailed_breakdown(self):
        """
        Detailed breakdown of HTML conversion pipeline.

        Isolates converter creation from conversion logic to identify bottleneck.
        """
        html = HTML_SIMPLE

        # Pre-compute intermediate values for stage isolation
        html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()
        document  = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)

        with Perf_Benchmark__Timing(config=self.config) as timing:

            # ═══════════════════════════════════════════════════════════════════
            # Section A: Full Operations (create converter + convert)
            # ═══════════════════════════════════════════════════════════════════
            timing.benchmark('A_01__html_to_dict__full',
                lambda: Html__To__Html_Dict__With__Node_Ids(html=html).convert())

            timing.benchmark('A_02__dict_to_mgraph__full',
                lambda: Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict))

            timing.benchmark('A_03__mgraph_to_html__full',
                lambda: Html_MGraph__Document__To__Html().convert(document))

            # ═══════════════════════════════════════════════════════════════════
            # Section B: Converter Creation Only
            # ═══════════════════════════════════════════════════════════════════
            timing.benchmark('B_01__converter_1_create',
                lambda: Html__To__Html_Dict__With__Node_Ids(html=html))

            timing.benchmark('B_02__converter_2_create',
                Html__To__Html_MGraph__Document__Node_Id_Reuse)

            timing.benchmark('B_03__converter_3_create',
                Html_MGraph__Document__To__Html)

            # ═══════════════════════════════════════════════════════════════════
            # Section C: Conversion Only (pre-created converters)
            # ═══════════════════════════════════════════════════════════════════
            converter_1 = Html__To__Html_Dict__With__Node_Ids(html=html)
            timing.benchmark('C_01__html_to_dict__convert_only',
                converter_1.convert)

            converter_2 = Html__To__Html_MGraph__Document__Node_Id_Reuse()
            timing.benchmark('C_02__dict_to_mgraph__convert_only',
                lambda: converter_2.convert_from_dict(html_dict))

            converter_3 = Html_MGraph__Document__To__Html()
            timing.benchmark('C_03__mgraph_to_html__convert_only',
                lambda: converter_3.convert(document))

        # Build and save report
        report = self.build_report(timing.results)
        self.storage.save_report(key='perf__conversion__detailed', report=report)

    # ═══════════════════════════════════════════════════════════════════════════
    # Report Builder
    # ═══════════════════════════════════════════════════════════════════════════

    def build_report(self, results: dict) -> str:
        """Build formatted report with detailed analysis."""

        lines = []

        # ───────────────────────────────────────────────────────────────────────
        # Report Header
        # ───────────────────────────────────────────────────────────────────────
        lines.append('═' * 80)
        lines.append('PHASE E: CONVERSION PIPELINE - DETAILED PERFORMANCE BREAKDOWN')
        lines.append('═' * 80)
        lines.append('')

        # ───────────────────────────────────────────────────────────────────────
        # Metadata Table
        # ───────────────────────────────────────────────────────────────────────
        meta_table = Print_Table()
        meta_table.set_title('BENCHMARK METADATA')
        meta_table.add_headers('Property', 'Value')
        meta_table.add_row(['Date'            , datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        meta_table.add_row(['Version'         , version__mgraph_ai_service_html_graph       ])
        meta_table.add_row(['Test HTML'       , HTML_SIMPLE[:50] + '...'                    ])
        meta_table.add_row(['Measurement Mode', 'measure_fast (87 iterations)'              ])
        meta_table.add_row(['Total Benchmarks', str(len(results))                           ])
        lines.append(meta_table.text())

        # ───────────────────────────────────────────────────────────────────────
        # Description
        # ───────────────────────────────────────────────────────────────────────
        lines.append('')
        lines.append('DESCRIPTION')
        lines.append('─' * 60)
        lines.append('This benchmark isolates converter creation from conversion')
        lines.append('logic to identify where time is spent in the HTML→MGraph')
        lines.append('conversion pipeline.')
        lines.append('')
        lines.append('Pipeline: HTML String → Dict → MGraph → HTML String')
        lines.append('')

        # ───────────────────────────────────────────────────────────────────────
        # Legend
        # ───────────────────────────────────────────────────────────────────────
        lines.append('LEGEND')
        lines.append('─' * 60)
        lines.append('  A_xx  Full Operation      = Create converter instance + call convert()')
        lines.append('  B_xx  Converter Creation  = Only create converter instance (no conversion)')
        lines.append('  C_xx  Convert Only        = Call convert() on pre-created instance')
        lines.append('')
        lines.append('  Overhead = Full - (Creation + Convert)')
        lines.append('           → Should be ~0 if no hidden costs')
        lines.append('')

        # ───────────────────────────────────────────────────────────────────────
        # Main Table
        # ───────────────────────────────────────────────────────────────────────
        table = Print_Table()
        table.set_title('DETAILED CONVERSION BREAKDOWN')
        table.add_headers('Benchmark', 'Time', 'Category', '% of Full')

        # Category mapping
        categories = {
            'A': 'Full Operation'     ,
            'B': 'Converter Creation' ,
            'C': 'Convert Only'       ,
        }

        # Track values by category
        full_total    = 0
        create_total  = 0
        convert_total = 0

        # Track individual values for percentage calc
        full_values    = {}
        create_values  = {}
        convert_values = {}

        # First pass: collect all values
        for benchmark_id in sorted(results.keys()):
            result      = results[benchmark_id]
            section     = benchmark_id[0]
            final_score = int(result.final_score)

            if section == 'A':
                full_total += final_score
                full_values[benchmark_id] = final_score
            elif section == 'B':
                create_total += final_score
                create_values[benchmark_id] = final_score
            elif section == 'C':
                convert_total += final_score
                convert_values[benchmark_id] = final_score

        # Second pass: build table with percentages
        current_section = None
        for benchmark_id in sorted(results.keys()):
            result      = results[benchmark_id]
            section     = benchmark_id[0]
            final_score = int(result.final_score)
            category    = categories.get(section, 'Unknown')

            # Add section separator
            if section != current_section:
                if current_section is not None:
                    table.add_row(['─' * 32, '─' * 10, '─' * 18, '─' * 10])
                current_section = section

            # Calculate percentage of full operation
            if section == 'A':
                pct_str = f'{final_score / full_total * 100:.1f}%' if full_total > 0 else '-'
            elif section == 'B':
                pct_str = f'{final_score / full_total * 100:.2f}%' if full_total > 0 else '-'
            elif section == 'C':
                pct_str = f'{final_score / full_total * 100:.1f}%' if full_total > 0 else '-'
            else:
                pct_str = '-'

            table.add_row([benchmark_id                   ,
                           self.format_ns(final_score)    ,
                           category                       ,
                           pct_str                        ])

        # Calculate overhead
        overhead = full_total - create_total - convert_total

        table.set_footer(f'Total: {len(results)} benchmarks')

        lines.append(table.text())

        # ───────────────────────────────────────────────────────────────────────
        # Category Summary
        # ───────────────────────────────────────────────────────────────────────
        lines.append('')
        lines.append('=' * 60)
        lines.append('CATEGORY SUMMARY')
        lines.append('=' * 60)
        lines.append(f'  Full Operations:    {self.format_ns(full_total):>12}  (A_xx benchmarks)')
        lines.append(f'  Converter Creation: {self.format_ns(create_total):>12}  (B_xx benchmarks)')
        lines.append(f'  Convert Only:       {self.format_ns(convert_total):>12}  (C_xx benchmarks)')
        lines.append(f'  ─────────────────────────────────────────────')
        lines.append(f'  Overhead:           {self.format_ns(overhead):>12}  (full - create - convert)')

        # ───────────────────────────────────────────────────────────────────────
        # Percentage Analysis
        # ───────────────────────────────────────────────────────────────────────
        lines.append('')
        lines.append('=' * 60)
        lines.append('PERCENTAGE ANALYSIS')
        lines.append('=' * 60)
        if full_total > 0:
            create_pct  = create_total / full_total * 100
            convert_pct = convert_total / full_total * 100
            lines.append(f'  Converter Creation: {create_pct:>6.2f}% of total time')
            lines.append(f'  Convert Only:       {convert_pct:>6.1f}% of total time')
            lines.append(f'  Overhead:           {(full_total - create_total - convert_total) / full_total * 100:>6.2f}% of total time')

        # ───────────────────────────────────────────────────────────────────────
        # Stage Breakdown
        # ───────────────────────────────────────────────────────────────────────
        lines.append('')
        lines.append('=' * 60)
        lines.append('STAGE BREAKDOWN (Full Operations)')
        lines.append('=' * 60)
        if full_total > 0:
            for benchmark_id, value in sorted(full_values.items()):
                stage_name = benchmark_id.replace('A_01__', '').replace('A_02__', '').replace('A_03__', '').replace('__full', '')
                pct = value / full_total * 100
                bar_len = int(pct / 2)  # Scale to ~50 chars max
                bar = '█' * bar_len
                lines.append(f'  {stage_name:<20} {self.format_ns(value):>10} ({pct:>5.1f}%) {bar}')

        # ───────────────────────────────────────────────────────────────────────
        # Bottleneck Identification
        # ───────────────────────────────────────────────────────────────────────
        lines.append('')
        lines.append('=' * 60)
        lines.append('BOTTLENECK ANALYSIS')
        lines.append('=' * 60)
        if full_values:
            bottleneck_id = max(full_values, key=full_values.get)
            bottleneck_val = full_values[bottleneck_id]
            bottleneck_pct = bottleneck_val / full_total * 100 if full_total > 0 else 0
            bottleneck_name = bottleneck_id.replace('__full', '')
            lines.append(f'  Primary Bottleneck: {bottleneck_name}')
            lines.append(f'  Time:               {self.format_ns(bottleneck_val)}')
            lines.append(f'  Percentage:         {bottleneck_pct:.1f}% of total')

        # ───────────────────────────────────────────────────────────────────────
        # Key Insight
        # ───────────────────────────────────────────────────────────────────────
        lines.append('')
        lines.append('=' * 60)
        lines.append('KEY INSIGHT')
        lines.append('=' * 60)
        if full_total > 0 and create_total > 0:
            create_pct = create_total / full_total * 100
            if create_pct < 1:
                lines.append(f'  Converter creation is {create_pct:.2f}% of total time → NEGLIGIBLE')
                lines.append(f'  The bottleneck is INSIDE the conversion logic, not object creation.')
            else:
                lines.append(f'  Converter creation is {create_pct:.1f}% of total time.')

        # ───────────────────────────────────────────────────────────────────────
        # Footer
        # ───────────────────────────────────────────────────────────────────────
        lines.append('')
        lines.append('═' * 80)
        lines.append(f'Report generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        lines.append(f'Version: {version__mgraph_ai_service_html_graph}')
        lines.append('═' * 80)

        return '\n'.join(lines)

    def format_ns(self, ns: int) -> str:
        """Format nanoseconds for readability."""
        if ns >= 1_000_000_000:
            return f"{ns / 1_000_000_000:.2f}s"
        elif ns >= 1_000_000:
            return f"{ns / 1_000_000:.2f}ms"
        elif ns >= 1_000:
            return f"{ns / 1_000:.2f}µs"
        else:
            return f"{ns}ns"