# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Perf__Phase_E__Scalability (Refactored)
# Part of Phase E_1: Performance Analysis
#
# Tests scaling behavior analysis and default vs fast_create comparison
# ═══════════════════════════════════════════════════════════════════════════════

import phase_e
from unittest                                                                   import TestCase
from osbot_utils.helpers.performance.testing.Html_Generator__For_Benchmarks     import Html_Generator__For_Benchmarks
from osbot_utils.testing.Pytest                                                 import skip_pytest
from osbot_utils.utils.Files                                                    import path_combine
from phase_e.performance.Perf__Phase_E__Scalability                             import Perf__Phase_E__Scalability
from phase_e.performance.Perf__Phase_E__Scalability                             import Schema__Scaling_Analysis
from phase_e.performance.Perf__Phase_E__Scalability                             import Schema__Scaling_Comparison
from phase_e.performance.Perf__Phase_E__Scalability                             import Schema__Scale_Point
from phase_e.performance.Perf__Phase_E__Scalability                             import SIZES_QUICK, SIZES_STANDARD
from phase_e.performance.Perf__Phase_E__Conversion                              import Perf__Phase_E__Conversion
from phase_e.storage.backends.Perf__Storage__Local                              import Perf__Storage__Local


#from phase_e.performance.Perf__Storage__Local                                   import Perf__Storage__Local


class test_Perf__Phase_E__Scalability(TestCase):

    @classmethod
    def setUpClass(cls):
        skip_pytest("takes to long to run")
        cls.storage_path = path_combine(phase_e.path, '../perf_results')
        cls.storage      = Perf__Storage__Local(storage_path=cls.storage_path)
        cls.generator    = Html_Generator__For_Benchmarks()
        cls.converter    = Perf__Phase_E__Conversion()
        cls.scalability  = Perf__Phase_E__Scalability(generator = cls.generator,
                                                       converter = cls.converter,
                                                       storage   = cls.storage  )

    # ═══════════════════════════════════════════════════════════════════════════
    # Quick Analysis Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__run_quick_analysis__default(self):                                # Quick analysis in default mode
        with self.scalability as _:
            analysis = _.run_quick_analysis()

            assert type(analysis) is Schema__Scaling_Analysis
            assert len(analysis.points) == len(SIZES_QUICK)
            assert str(analysis.mode) == 'default'
            assert str(analysis.bottleneck_stage) != ''
            assert str(analysis.scaling_behavior) != ''

            report = _.build_report(analysis)
            self.storage.save_report(key='scaling__quick__default', report=report)

    def test__run_quick_analysis__fast_create(self):                            # Quick analysis with fast_create
        with self.scalability as _:
            analysis = _.run_quick_analysis__fast_create()

            assert type(analysis) is Schema__Scaling_Analysis
            assert len(analysis.points) == len(SIZES_QUICK)
            assert str(analysis.mode) == 'fast_create'

            report = _.build_report(analysis)
            self.storage.save_report(key='scaling__quick__fast_create', report=report)

    # ═══════════════════════════════════════════════════════════════════════════
    # Standard Analysis Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__run_standard_analysis__default(self):                             # Standard analysis in default mode
        with self.scalability as _:
            analysis = _.run_standard_analysis()

            assert type(analysis) is Schema__Scaling_Analysis
            assert len(analysis.points) == len(SIZES_STANDARD)
            assert str(analysis.mode) == 'default'

            report = _.build_report(analysis)
            self.storage.save_report(key='scaling__standard__default', report=report)

    def test__run_standard_analysis__fast_create(self):                         # Standard analysis with fast_create
        with self.scalability as _:
            analysis = _.run_standard_analysis__fast_create()

            assert type(analysis) is Schema__Scaling_Analysis
            assert len(analysis.points) == len(SIZES_STANDARD)
            assert str(analysis.mode) == 'fast_create'

            report = _.build_report(analysis)
            self.storage.save_report(key='scaling__standard__fast_create', report=report)

    # ═══════════════════════════════════════════════════════════════════════════
    # Comparison Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__run_comparison__quick(self):                                      # Quick comparison: default vs fast_create
        with self.scalability as _:
            comparison = _.run_comparison__quick()

            assert type(comparison) is Schema__Scaling_Comparison
            assert type(comparison.before) is Schema__Scaling_Analysis
            assert type(comparison.after) is Schema__Scaling_Analysis
            assert str(comparison.before.mode) == 'default'
            assert str(comparison.after.mode) == 'fast_create'
            assert float(comparison.improvement_pct) > 0                        # Should see improvement

            report = _.build_full_comparison_report(comparison)
            self.storage.save_report(key='scaling__comparison__quick', report=report)

    def test__run_comparison__standard(self):                                   # Standard comparison: default vs fast_create
        with self.scalability as _:
            comparison = _.run_comparison__standard()

            assert type(comparison) is Schema__Scaling_Comparison
            assert float(comparison.improvement_pct) > 0                        # Should see improvement

            report = _.build_full_comparison_report(comparison)
            self.storage.save_report(key='scaling__comparison__standard', report=report)

    # ═══════════════════════════════════════════════════════════════════════════
    # Individual Benchmark Test
    # ═══════════════════════════════════════════════════════════════════════════

    def test__benchmark_size(self):                                             # Single size benchmark
        with self.scalability as _:
            point = _.benchmark_size('test', 50)

            assert type(point) is Schema__Scale_Point
            assert str(point.name) == 'test'
            assert int(point.target_nodes) == 50
            assert int(point.actual_html_bytes) > 0
            assert float(point.ns_per_node) > 0

    # ═══════════════════════════════════════════════════════════════════════════
    # Analysis Method Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__identify_bottleneck(self):                                        # Bottleneck identification
        with self.scalability as _:
            analysis = _.run_quick_analysis()
            bottleneck = str(analysis.bottleneck_stage)

            assert bottleneck in ['HTML→Dict', 'Dict→MGraph', 'MGraph→HTML']
            assert bottleneck == 'Dict→MGraph'                                  # Expected based on prior analysis

    def test__analyze_scaling_behavior(self):                                   # Scaling behavior detection
        with self.scalability as _:
            analysis = _.run_quick_analysis()
            scaling = str(analysis.scaling_behavior)

            assert 'O(n)' in scaling or 'O(n²)' in scaling or 'O(n log n)' in scaling

    # ═══════════════════════════════════════════════════════════════════════════
    # Report Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__build_report(self):                                               # Single analysis report
        with self.scalability as _:
            analysis = _.run_quick_analysis()
            report   = _.build_report(analysis)

            assert 'SCALING ANALYSIS' in report
            assert 'Nodes'            in report
            assert 'ns/node'          in report
            assert 'Bottleneck'       in report
            assert 'Scaling'          in report

    def test__build_comparison_report(self):                                    # Comparison report
        with self.scalability as _:
            comparison = _.run_comparison__quick()
            report     = _.build_comparison_report(comparison.before, comparison.after)

            assert 'SCALING COMPARISON' in report
            assert 'Default'            in report
            assert 'Fast Create'        in report
            assert 'Speedup'            in report

    def test__build_full_comparison_report(self):                               # Full comparison report
        with self.scalability as _:
            comparison = _.run_comparison__quick()
            report     = _.build_full_comparison_report(comparison)

            assert 'DEFAULT MODE'     in report
            assert 'FAST CREATE MODE' in report
            assert 'COMPARISON'       in report
            assert 'Overall'          in report

    # ═══════════════════════════════════════════════════════════════════════════
    # ns_per_node Analysis
    # ═══════════════════════════════════════════════════════════════════════════

    def test__ns_per_node__decreases_with_fast_create(self):                    # fast_create improves efficiency
        with self.scalability as _:
            comparison = _.run_comparison__quick()

            for i, before_point in enumerate(comparison.before.points):
                after_point = comparison.after.points[i]

                before_ns = float(before_point.ns_per_node)
                after_ns  = float(after_point.ns_per_node)

                assert after_ns < before_ns, f"Expected {after_ns} < {before_ns} for {before_point.name}"

    def test__ns_per_node__scaling_behavior(self):                              # ns_per_node should be relatively stable (O(n))
        with self.scalability as _:
            analysis = _.run_quick_analysis__fast_create()

            first_ns = float(analysis.points[0].ns_per_node)
            last_ns  = float(analysis.points[-1].ns_per_node)

            ratio = last_ns / first_ns if first_ns > 0 else 0

            # For O(n) behavior, ratio should be < 1.5
            # For O(n²) behavior, ratio would be > 3
            assert ratio < 10, f"Ratio {ratio} suggests worse than O(n²) scaling"

    # ═══════════════════════════════════════════════════════════════════════════
    # Storage Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__save_and_load_analysis(self):                                     # Round-trip save/load
        with self.scalability as _:
            analysis = _.run_quick_analysis()
            key = _.save_analysis(analysis, key='test__save_load')

            loaded = _.load_analysis(key)

            assert loaded is not None
            assert len(loaded.points) == len(analysis.points)
            assert str(loaded.bottleneck_stage) == str(analysis.bottleneck_stage)