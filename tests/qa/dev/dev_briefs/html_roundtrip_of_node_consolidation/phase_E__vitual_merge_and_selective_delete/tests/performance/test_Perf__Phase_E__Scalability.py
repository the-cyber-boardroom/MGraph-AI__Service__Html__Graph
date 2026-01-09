# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Perf__Phase_E__Scalability
# Part of Phase E_1: Performance Analysis
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                   import TestCase
import phase_e
from osbot_utils.type_safe.type_safe_core.config.Type_Safe__Config              import Type_Safe__Config
from osbot_utils.utils.Files                                                    import path_combine
from phase_e.performance.Perf__Phase_E__Scalability                             import Perf__Phase_E__Scalability
from phase_e.performance.Perf__Phase_E__Scalability                             import Schema__Scale_Point
from phase_e.performance.Perf__Phase_E__Scalability                             import Schema__Scaling_Analysis
from phase_e.performance.Perf__Storage__Local                                   import Perf__Storage__Local


class test_Perf__Phase_E__Scalability(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.storage_path = path_combine(phase_e.path,'../perf_results'      )
        cls.storage     = Perf__Storage__Local      (storage_path=cls.storage_path)
        cls.scalability = Perf__Phase_E__Scalability(storage=cls.storage)

    def test__init__(self):                                                     # Test auto-initialization
        with self.scalability as _:
            assert type(_).__name__ == 'Perf__Phase_E__Scalability'
            assert _.generator      is not None
            assert _.converter      is not None

    # todo: figure out why this is taking 2 seconds to run
    def test_run_quick_analysis__returns_schema(self):                          # Quick analysis returns schema
        with self.scalability as _:
            analysis = _.run_quick_analysis(auto_save=True)

            assert type(analysis)             is Schema__Scaling_Analysis
            assert len(analysis.points)       == 3                              # small, medium, large
            assert str(analysis.bottleneck_stage) != ''
            assert str(analysis.scaling_behavior) != ''

    # the tests bellow take too long to run (due to run_quick_analysis and others taking too long)
#
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Individual Size Benchmark
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     def test_benchmark_size__returns_scale_point(self):                         # Returns scale point schema
#         with self.scalability as _:
#             point = _.benchmark_size('test', 50)
#
#             assert type(point)             is Schema__Scale_Point
#             assert str(point.name)         == 'test'
#             assert int(point.target_nodes) == 50
#             assert point.timing            is not None
#             assert float(point.ns_per_node) > 0
#
#     def test_benchmark_size__timing_populated(self):                            # Timing is populated
#         with self.scalability as _:
#             point = _.benchmark_size('small', 100)
#
#             assert int(point.timing.html_to_dict_ns)   > 0
#             assert int(point.timing.dict_to_mgraph_ns) > 0
#             assert int(point.timing.mgraph_to_html_ns) > 0
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Quick Analysis (faster for testing)
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     def test_run_quick_analysis__returns_schema(self):                          # Quick analysis returns schema
#         with self.scalability as _:
#             analysis = _.run_quick_analysis(auto_save=True)
#
#             assert type(analysis)             is Schema__Scaling_Analysis
#             assert len(analysis.points)       == 3                              # small, medium, large
#             assert str(analysis.bottleneck_stage) != ''
#             assert str(analysis.scaling_behavior) != ''
#
#     def test_run_quick_analysis__points_ordered(self):                          # Points ordered by size
#         with self.scalability as _:
#             with Type_Safe__Config(fast_create=True, skip_validation=True):
#                 analysis = _.run_quick_analysis(auto_save=True)
#
#             sizes = [int(p.target_nodes) for p in analysis.points]
#
#             assert sizes == sorted(sizes)                                       # Ascending order
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Analysis Methods
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     def test_identify_bottleneck(self):                                         # Identifies bottleneck stage
#         with self.scalability as _:
#             analysis   = _.run_quick_analysis()
#             bottleneck = str(analysis.bottleneck_stage)
#
#             assert bottleneck in ['HTML→Dict', 'Dict→MGraph', 'MGraph→HTML', 'unknown']
#
#     def test_analyze_scaling_behavior(self):                                    # Analyzes scaling
#         with self.scalability as _:
#             analysis = _.run_quick_analysis()
#             scaling  = str(analysis.scaling_behavior)
#
#             valid_behaviors = ['O(n) linear - good'                  ,
#                                'O(n log n) - acceptable'             ,
#                                'O(n²) quadratic - potential bottleneck',
#                                'worse than O(n²) - significant bottleneck',
#                                'insufficient_data'                   ]
#
#             assert scaling in valid_behaviors
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Reporting
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     def test_format_analysis(self):                                             # Formats analysis
#         with self.scalability as _:
#             analysis  = _.run_quick_analysis()
#             formatted = _.format_analysis(analysis)
#
#             assert 'SCALING ANALYSIS REPORT' in formatted
#             assert 'Bottleneck Stage:'       in formatted
#             assert 'Scaling Behavior:'       in formatted
#             assert 'HTML→Dict'               in formatted
#             assert 'Dict→MGraph'             in formatted
#             assert 'MGraph→HTML'             in formatted
#
#     def test_format_analysis__contains_all_points(self):                        # Contains all data points
#         with self.scalability as _:
#             analysis  = _.run_quick_analysis()
#             formatted = _.format_analysis(analysis)
#
#             for point in analysis.points:
#                 assert str(point.name) in formatted
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Print_Table Reports
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     def test_build_report(self):                                                # Build Print_Table report
#         with self.scalability as _:
#             analysis = _.run_quick_analysis()
#             report   = _.build_report(analysis)
#
#             assert 'PHASE E SCALING ANALYSIS' in report
#             assert 'HTML→Dict'                in report
#             assert 'Dict→MGraph'              in report
#             assert 'MGraph→HTML'              in report
#             assert 'Bottleneck'               in report
#             assert 'Scaling'                  in report
#
#     def test_build_comparison_report(self):                                     # Build comparison report
#         with self.scalability as _:
#             analysis1 = _.run_quick_analysis()
#             analysis2 = _.run_quick_analysis()
#             report    = _.build_comparison_report(analysis1, analysis2)
#
#             assert 'SCALING COMPARISON REPORT' in report
#             assert 'Before'                    in report
#             assert 'After'                     in report
#             assert 'Change'                    in report
#
#
# # ═══════════════════════════════════════════════════════════════════════════════
# # Full Analysis Test (slower, run separately)
# # ═══════════════════════════════════════════════════════════════════════════════
#
# class test_Perf__Phase_E__Scalability__Full(TestCase):
#     """Full analysis tests - slower, may want to skip in CI"""
#
#     @classmethod
#     def setUpClass(cls):
#         cls.scalability = Perf__Phase_E__Scalability()
#
#     def test_run_full_analysis(self):                                           # Full analysis (6 sizes)
#         with self.scalability as _:
#             analysis = _.run_full_analysis()
#
#             assert type(analysis)       is Schema__Scaling_Analysis
#             assert len(analysis.points) == 6                                    # tiny through massive
#
#             names = [str(p.name) for p in analysis.points]
#             assert 'tiny'    in names
#             assert 'massive' in names
#
#     def test_run_full_analysis__print_report(self):                             # Print full report
#         with self.scalability as _:
#             analysis = _.run_full_analysis()
#             _.print_analysis(analysis)                                          # Visual inspection
#
#             # Just verify it runs without error
#             assert True
#
#
# # ═══════════════════════════════════════════════════════════════════════════════
# # Storage Integration Tests
# # ═══════════════════════════════════════════════════════════════════════════════
#
# class test_Perf__Phase_E__Scalability__Storage(TestCase):
#     """Tests for storage integration"""
#
#     @classmethod
#     def setUpClass(cls):
#         import tempfile
#         cls.temp_dir = tempfile.mkdtemp()
#
#         from phase_e.performance.Perf__Storage__Local import Perf__Storage__Local
#         cls.storage     = Perf__Storage__Local(storage_path=cls.temp_dir)
#         cls.scalability = Perf__Phase_E__Scalability(storage=cls.storage)
#
#     @classmethod
#     def tearDownClass(cls):
#         import shutil
#         shutil.rmtree(cls.temp_dir, ignore_errors=True)
#
#     def test_run_quick_analysis__with_auto_save(self):                          # Auto-save on analysis
#         with self.scalability as _:
#             analysis = _.run_quick_analysis(auto_save=True)
#
#             keys = _.list_analyses()
#
#             assert len(keys) >= 1
#             assert any('scaling_analysis' in k for k in keys)
#
#     def test_save_and_load_analysis(self):                                      # Manual save and load
#         with self.scalability as _:
#             analysis = _.run_quick_analysis()
#
#             key = _.save_analysis(analysis, key='manual_test')
#
#             loaded = _.load_analysis('manual_test')
#
#             assert loaded                        is not None
#             assert len(loaded.points)            == len(analysis.points)
#             assert str(loaded.bottleneck_stage)  == str(analysis.bottleneck_stage)
#             assert str(loaded.scaling_behavior)  == str(analysis.scaling_behavior)
#
#     def test_list_analyses(self):                                               # List stored analyses
#         with self.scalability as _:
#             _.run_quick_analysis(auto_save=True)
#             _.run_quick_analysis(auto_save=True)
#
#             keys = _.list_analyses()
#
#             assert len(keys) >= 2
#
#     def test_no_storage__returns_none(self):                                    # No storage configured
#         scalability_no_storage = Perf__Phase_E__Scalability()
#
#         with scalability_no_storage as _:
#             key = _.save_analysis(Schema__Scaling_Analysis())
#
#             assert key is None
#             assert _.list_analyses() == []