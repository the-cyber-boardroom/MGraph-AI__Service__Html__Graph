# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Perf__Phase_E__Conversion (Refactored)
# Part of Phase E_1: Performance Analysis
#
# Uses Perf_Benchmark__Timing for proper Fibonacci-based measurement
# ═══════════════════════════════════════════════════════════════════════════════

import phase_e
from unittest                                                                   import TestCase
from osbot_utils.type_safe.type_safe_core.config.Type_Safe__Config              import Type_Safe__Config
from osbot_utils.utils.Files                                                    import path_combine
from phase_e.performance.Perf__Phase_E__Conversion                              import Perf__Phase_E__Conversion
from phase_e.performance.Perf__Phase_E__Conversion                              import Schema__Conversion_Timing
from phase_e.performance.Perf__Phase_E__Conversion                              import Schema__Conversion_Breakdown
from phase_e.performance.Html_Generator__For_Benchmarks                         import Html_Generator__For_Benchmarks
from phase_e.performance.Perf__Storage__Local                                   import Perf__Storage__Local


class test_Perf__Phase_E__Conversion(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.storage_path = path_combine(phase_e.path, '../perf_results')
        cls.storage      = Perf__Storage__Local(storage_path=cls.storage_path)
        cls.converter    = Perf__Phase_E__Conversion()
        cls.generator    = Html_Generator__For_Benchmarks()
        cls.test_html    = "<html><body><div><p>Hello World</p></div></body></html>"

    # ═══════════════════════════════════════════════════════════════════════════
    # Basic Conversion Benchmark
    # ═══════════════════════════════════════════════════════════════════════════

    def test__benchmark_conversions(self):                                      # Basic 3-stage benchmark
        with self.converter as _:
            timing = _.benchmark_conversions(self.test_html)

            assert type(timing)                  is Schema__Conversion_Timing
            assert int(timing.html_to_dict_ns)   > 0
            assert int(timing.dict_to_mgraph_ns) > 0
            assert int(timing.mgraph_to_html_ns) > 0
            assert int(timing.total_ns)          > 0

            report = _.build_report(timing)
            self.storage.save_report(key='conversion__basic', report=report)

    # ═══════════════════════════════════════════════════════════════════════════
    # Detailed Breakdown - Isolates Converter Creation vs Convert
    # ═══════════════════════════════════════════════════════════════════════════

    def test__benchmark_conversions_detailed(self):                             # Detailed breakdown
        with self.converter as _:
            results = _.benchmark_conversions_detailed(self.test_html)

            assert 'A_01__html_to_dict__full'           in results              # Full operations
            assert 'A_02__dict_to_mgraph__full'         in results
            assert 'A_03__mgraph_to_html__full'         in results

            assert 'B_01__converter_1_create'           in results              # Converter creation
            assert 'B_02__converter_2_create'           in results
            assert 'B_03__converter_3_create'           in results

            assert 'C_01__html_to_dict__convert_only'   in results              # Convert only
            assert 'C_02__dict_to_mgraph__convert_only' in results
            assert 'C_03__mgraph_to_html__convert_only' in results

            report = _.build_detailed_report(results)
            self.storage.save_report(key='conversion__detailed', report=report)

    # ═══════════════════════════════════════════════════════════════════════════
    # Multi-Size Benchmark - Default Mode
    # ═══════════════════════════════════════════════════════════════════════════

    def test__benchmark_multiple_sizes__default(self):                          # Default Type_Safe mode
        sizes = {'1'  : self.generator.generate__1()  ,
                 '10' : self.generator.generate__10() ,
                 '100': self.generator.generate__100()}

        with self.converter as _:
            results = _.benchmark_multiple_sizes(sizes)
            report  = _.build_multi_report(results)

            assert 'CONVERSION TIMING BY SIZE' in report
            assert 'Primary Bottleneck'        in report

            self.storage.save_report(key='conversion__multi__default', report=report)

    # ═══════════════════════════════════════════════════════════════════════════
    # Multi-Size Benchmark - Fast Create Mode
    # ═══════════════════════════════════════════════════════════════════════════

    def test__benchmark_multiple_sizes__fast_create(self):                      # With fast_create optimization
        sizes = {'1'  : self.generator.generate__1()  ,
                 '10' : self.generator.generate__10() ,
                 '100': self.generator.generate__100()}

        with Type_Safe__Config(fast_create=True, skip_validation=True):
            with self.converter as _:
                results = _.benchmark_multiple_sizes(sizes)
                report  = _.build_multi_report(results)

                assert 'CONVERSION TIMING BY SIZE' in report
                assert 'Primary Bottleneck'        in report

                self.storage.save_report(key='conversion__multi__fast_create', report=report)

    # ═══════════════════════════════════════════════════════════════════════════
    # Comparison - Default vs Fast Create
    # ═══════════════════════════════════════════════════════════════════════════

    def test__benchmark_comparison__default_vs_fast_create(self):               # Side-by-side comparison
        sizes = {'1'  : self.generator.generate__1()  ,
                 '10' : self.generator.generate__10() ,
                 '100': self.generator.generate__100()}

        # Run in default mode
        with self.converter as _:
            results_default = _.benchmark_multiple_sizes(sizes)

        # Run with fast_create
        with Type_Safe__Config(fast_create=True, skip_validation=True):
            with self.converter as _:
                results_fast = _.benchmark_multiple_sizes(sizes)

        # Build comparison report
        report_lines = ['=' * 80                                    ,
                        'COMPARISON: Default vs Fast Create'        ,
                        '=' * 80                                    ,
                        ''                                          ,
                        'DEFAULT MODE:'                             ,
                        '-' * 40                                    ]

        with self.converter as _:
            report_lines.append(_.build_multi_report(results_default))
            report_lines.append('')
            report_lines.append('FAST CREATE MODE:')
            report_lines.append('-' * 40)
            report_lines.append(_.build_multi_report(results_fast))
            report_lines.append('')
            report_lines.append('IMPROVEMENT:')
            report_lines.append('-' * 40)

            for size in sorted(results_default.keys()):
                default_ns = int(results_default[size].total_ns)
                fast_ns    = int(results_fast[size].total_ns)

                if default_ns > 0:
                    improvement = ((default_ns - fast_ns) / default_ns) * 100
                    speedup     = default_ns / fast_ns if fast_ns > 0 else 0
                    report_lines.append(f"  {size}: {_.format_ns(default_ns)} → {_.format_ns(fast_ns)} "
                                        f"({improvement:.1f}% faster, {speedup:.1f}x speedup)")

        report = '\n'.join(report_lines)
        self.storage.save_report(key='conversion__comparison__default_vs_fast_create', report=report)

    # ═══════════════════════════════════════════════════════════════════════════
    # Detailed Breakdown Comparison
    # ═══════════════════════════════════════════════════════════════════════════

    def test__benchmark_detailed_comparison(self):                              # Where is time spent?
        # Run detailed in default mode
        with self.converter as _:
            assert type(self.test_html) is str
            results_default = _.benchmark_conversions_detailed(self.test_html)
        return
        # Run detailed with fast_create
        with Type_Safe__Config(fast_create=True, skip_validation=True):
            with self.converter as _:
                results_fast = _.benchmark_conversions_detailed(self.test_html)

        # Build comparison
        report_lines = ['=' * 80                                              ,
                        'DETAILED BREAKDOWN: Default vs Fast Create'          ,
                        '=' * 80                                              ,
                        ''                                                    ,
                        f'{"Benchmark":<40} {"Default":>12} {"Fast":>12} {"Δ":>10}',
                        '-' * 80                                              ]

        with self.converter as _:
            for benchmark_id in sorted(results_default.keys()):
                default_ns = results_default[benchmark_id]
                fast_ns    = results_fast.get(benchmark_id, 0)
                diff       = default_ns - fast_ns

                report_lines.append(f'{benchmark_id:<40} '
                                    f'{_.format_ns(default_ns):>12} '
                                    f'{_.format_ns(fast_ns):>12} '
                                    f'{_.format_ns(diff):>10}')

        report = '\n'.join(report_lines)
        self.storage.save_report(key='conversion__detailed_comparison', report=report)

    # ═══════════════════════════════════════════════════════════════════════════
    # Individual Stage Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__benchmark_html_to_dict(self):                                     # Stage 1 only
        with self.converter as _:
            ns = _.benchmark_html_to_dict(self.test_html)
            assert ns > 0

    def test__benchmark_dict_to_mgraph(self):                                   # Stage 2 only
        from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids import Html__To__Html_Dict__With__Node_Ids

        html_dict = Html__To__Html_Dict__With__Node_Ids(html=self.test_html).convert()

        with self.converter as _:
            ns = _.benchmark_dict_to_mgraph(html_dict)
            assert ns > 0

    def test__benchmark_mgraph_to_html(self):                                   # Stage 3 only
        from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids            import Html__To__Html_Dict__With__Node_Ids
        from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse

        html_dict = Html__To__Html_Dict__With__Node_Ids(html=self.test_html).convert()
        document  = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)

        with self.converter as _:
            ns = _.benchmark_mgraph_to_html(document)
            assert ns > 0

    # ═══════════════════════════════════════════════════════════════════════════
    # Formatting Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__format_ns(self):                                                  # Time formatting
        with self.converter as _:
            assert _.format_ns(500)           == '500ns'
            assert _.format_ns(5_000)         == '5.00µs'
            assert _.format_ns(5_000_000)     == '5.00ms'
            assert _.format_ns(5_000_000_000) == '5.00s'

    def test__calculate_breakdown(self):                                        # Percentage breakdown
        with self.converter as _:
            timing    = _.benchmark_conversions(self.test_html)
            breakdown = _.calculate_breakdown(timing)

            assert type(breakdown) is Schema__Conversion_Breakdown

            total_pct = (float(breakdown.html_to_dict_pct)   +
                         float(breakdown.dict_to_mgraph_pct) +
                         float(breakdown.mgraph_to_html_pct))

            assert 99.0 <= total_pct <= 101.0                                   # ~100% with rounding tolerance