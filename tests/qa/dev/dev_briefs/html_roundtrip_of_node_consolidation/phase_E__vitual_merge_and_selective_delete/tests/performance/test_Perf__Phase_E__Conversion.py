# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Perf__Phase_E__Conversion
# Part of Phase E_1: Performance Analysis
# ═══════════════════════════════════════════════════════════════════════════════

import phase_e
from unittest                                                                   import TestCase
from osbot_utils.testing.Pytest                                                 import skip_pytest
from osbot_utils.type_safe.type_safe_core.config.Type_Safe__Config import Type_Safe__Config
from osbot_utils.utils.Files                                                    import path_combine
from phase_e.performance.Perf__Phase_E__Conversion                              import Perf__Phase_E__Conversion
from phase_e.performance.Perf__Phase_E__Conversion                              import Schema__Conversion_Timing
from phase_e.performance.Perf__Phase_E__Conversion                              import Schema__Conversion_Breakdown
from phase_e.performance.Html_Generator__For_Benchmarks                         import Html_Generator__For_Benchmarks
from phase_e.performance.Perf__Storage__Local import Perf__Storage__Local


class test_Perf__Phase_E__Conversion(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.storage_path = path_combine(phase_e.path,'../perf_results'      )
        cls.storage      = Perf__Storage__Local      (storage_path=cls.storage_path)
        cls.converter    = Perf__Phase_E__Conversion()
        cls.generator    = Html_Generator__For_Benchmarks()
        cls.test_html    = "<html><body><div><p>Hello World</p></div></body></html>"

    def test__init__(self):                                                     # Test auto-initialization
        with self.converter as _:
            assert type(_).__name__ == 'Perf__Phase_E__Conversion'
            assert _.session        is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # Full Conversion Benchmark
    # ═══════════════════════════════════════════════════════════════════════════

    def test_benchmark_conversions__returns_timing(self):                       # Returns timing schema
        with self.converter as _:
            timing = _.benchmark_conversions(self.test_html)

            assert type(timing)                  is Schema__Conversion_Timing
            assert int(timing.html_to_dict_ns)   > 0
            assert int(timing.dict_to_mgraph_ns) > 0
            assert int(timing.mgraph_to_html_ns) > 0
            assert int(timing.total_ns)          > 0

    def test_benchmark_conversions__total_is_sum(self):                         # Total equals sum of stages
        with self.converter as _:
            timing = _.benchmark_conversions(self.test_html)

            expected_total = (int(timing.html_to_dict_ns)   +
                              int(timing.dict_to_mgraph_ns) +
                              int(timing.mgraph_to_html_ns))

            assert int(timing.total_ns) == expected_total

    def test_benchmark_conversions__captures_html_size(self):                   # Captures HTML size
        with self.converter as _:
            timing = _.benchmark_conversions(self.test_html)

            assert int(timing.html_size_bytes) == len(self.test_html)

    # ═══════════════════════════════════════════════════════════════════════════
    # Individual Stage Benchmarks
    # ═══════════════════════════════════════════════════════════════════════════

    def test_benchmark_html_to_dict(self):                                      # Stage 1 benchmark
        with self.converter as _:
            ns = _.benchmark_html_to_dict(self.test_html)

            assert ns > 0

    def test_benchmark_dict_to_mgraph(self):                                    # Stage 2 benchmark
        from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids import Html__To__Html_Dict__With__Node_Ids

        html_dict = Html__To__Html_Dict__With__Node_Ids(html=self.test_html).convert()

        with self.converter as _:
            ns = _.benchmark_dict_to_mgraph(html_dict)

            assert ns > 0

    def test_benchmark_mgraph_to_html(self):                                    # Stage 3 benchmark
        from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids            import Html__To__Html_Dict__With__Node_Ids
        from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse

        html_dict = Html__To__Html_Dict__With__Node_Ids(html=self.test_html).convert()
        document  = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)

        with self.converter as _:
            ns = _.benchmark_mgraph_to_html(document)

            assert ns > 0

    # ═══════════════════════════════════════════════════════════════════════════
    # Analysis Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def test_calculate_breakdown(self):                                         # Percentage breakdown
        with self.converter as _:
            timing    = _.benchmark_conversions(self.test_html)
            breakdown = _.calculate_breakdown(timing)

            assert type(breakdown) is Schema__Conversion_Breakdown

            total_pct = (float(breakdown.html_to_dict_pct)   +
                         float(breakdown.dict_to_mgraph_pct) +
                         float(breakdown.mgraph_to_html_pct))

            assert 99.0 <= total_pct <= 101.0                                   # ~100% (rounding tolerance)

    def test_benchmark_multiple_sizes(self):                                    # Multiple size benchmark
        skip_pytest("currently taking too long")
        sizes = {'small' : self.generator.generate__100(),
                 'medium': self.generator.generate__500()}

        with self.converter as _:
            results = _.benchmark_multiple_sizes(sizes)

            assert 'small'  in results
            assert 'medium' in results
            assert type(results['small'])  is Schema__Conversion_Timing
            assert type(results['medium']) is Schema__Conversion_Timing

    # ═══════════════════════════════════════════════════════════════════════════
    # Reporting
    # ═══════════════════════════════════════════════════════════════════════════

    def test_format_timing(self):                                               # Format timing string
        with self.converter as _:
            timing    = _.benchmark_conversions(self.test_html)
            formatted = _.format_timing(timing)

            assert 'Total:'       in formatted
            assert 'HTML→Dict:'   in formatted
            assert 'Dict→MGraph:' in formatted
            assert 'MGraph→HTML:' in formatted
            assert '%'            in formatted

    def test_format_ns__nanoseconds(self):                                      # Format small values
        with self.converter as _:
            assert _.format_ns(500) == '500ns'

    def test_format_ns__microseconds(self):                                     # Format microseconds
        with self.converter as _:
            assert _.format_ns(5000) == '5.00µs'

    def test_format_ns__milliseconds(self):                                     # Format milliseconds
        with self.converter as _:
            assert _.format_ns(5_000_000) == '5.00ms'

    def test_format_ns__seconds(self):                                          # Format seconds
        with self.converter as _:
            assert _.format_ns(5_000_000_000) == '5.00s'

    # ═══════════════════════════════════════════════════════════════════════════
    # Print_Table Reports
    # ═══════════════════════════════════════════════════════════════════════════

    def test_build_report(self):                                                # Build Print_Table report
        with self.converter as _:
            timing = _.benchmark_conversions(self.test_html)
            report = _.build_report(timing)

            assert 'CONVERSION TIMING REPORT' in report
            assert 'HTML → Dict'              in report
            assert 'Dict → MGraph'            in report
            assert 'MGraph → HTML'            in report
            assert 'TOTAL'                    in report
            assert '%'                        in report
            self.storage.save_report(key='conversion__report', report=report)

    # todo: figure out why this is taking 4 secs to run (in fast create) and 9 secs in default Type_Safe mode
    def test_build_multi_report(self):                                          # Build multi-size report
        # sizes = {'small' : self.generator.generate_small() ,
        #          'medium': self.generator.generate_medium()}
        sizes = { '1'  : self.generator.generate__1   (),
                  '10'  : self.generator.generate__10 (),
                  '100' : self.generator.generate__100()}

        with Type_Safe__Config(fast_create=True, skip_validation=True):
            with self.converter as _:
                results = _.benchmark_multiple_sizes(sizes)
                report  = _.build_multi_report(results)

                assert 'CONVERSION TIMING BY SIZE' in report
                #assert 'small'                     in report
                #assert 'medium'                    in report
                assert 'Primary Bottleneck'        in report
                self.storage.save_report(key='conversion__multi_report (with fast_create)', report=report)
                #print(report)