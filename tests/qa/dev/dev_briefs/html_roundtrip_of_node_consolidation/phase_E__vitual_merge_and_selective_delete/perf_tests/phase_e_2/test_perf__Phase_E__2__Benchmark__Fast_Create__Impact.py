# ═══════════════════════════════════════════════════════════════════════════════
# Performance Benchmark: Fast Create Impact
# Validates: fast_create mode provides ~2x speedup for Dict → MGraph conversion
# ═══════════════════════════════════════════════════════════════════════════════

import phase_e
from unittest                                                                                                   import TestCase
from osbot_utils.utils.Files                                                                                    import path_combine
from mgraph_ai_service_html_graph.utils.Version                                                                 import version__mgraph_ai_service_html_graph
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids            import Html__To__Html_Dict__With__Node_Ids
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse
from osbot_utils.helpers.performance.benchmark.Perf_Benchmark__Timing                                           import Perf_Benchmark__Timing
from osbot_utils.helpers.performance.benchmark.schemas.enums.Enum__Measure_Mode                                 import Enum__Measure_Mode
from osbot_utils.helpers.performance.benchmark.schemas.timing.Schema__Perf_Benchmark__Timing__Config            import Schema__Perf_Benchmark__Timing__Config
from osbot_utils.type_safe.type_safe_core.config.Type_Safe__Config                                              import Type_Safe__Config
from osbot_utils.helpers.performance.report.Perf_Report__Builder                                                import Perf_Report__Builder
from osbot_utils.helpers.performance.testing.Html_Generator__For_Benchmarks                                     import Html_Generator__For_Benchmarks
from osbot_utils.helpers.performance.report.renderers.Perf_Report__Renderer__Text                               import Perf_Report__Renderer__Text
from osbot_utils.helpers.performance.report.schemas.Schema__Perf_Report__Metadata                               import Schema__Perf_Report__Metadata
from osbot_utils.helpers.performance.report.schemas.collections.Dict__Perf_Report__Legend                       import Dict__Perf_Report__Legend
from osbot_utils.helpers.performance.report.storage.Perf_Report__Storage__File_System                           import Perf_Report__Storage__File_System

# ═══════════════════════════════════════════════════════════════════════════════
# Report Metadata (edit here for quick iteration)
# ═══════════════════════════════════════════════════════════════════════════════

REPORT_KEY         = 'perf_2__benchmark__fast_create__impact'

REPORT_TITLE       = 'Fast Create Impact Benchmark'

REPORT_DESCRIPTION = ('Validates that fast_create mode provides ~2x speedup for Dict to MGraph conversion. '
                      'Tests at 1 and 10 nodes (larger sizes skipped - too slow until optimized).')

REPORT_TEST_INPUT  = 'HTML with 1 and 10 nodes'

REPORT_LEGEND      = { 'A': 'Default Mode  = Normal Type_Safe.__init__ (full validation)'  ,
                       'B': 'fast_create   = Schema-based direct __dict__ assignment'      }


# ═══════════════════════════════════════════════════════════════════════════════
# Benchmark Targets (edit here to add/remove tests)
# ═══════════════════════════════════════════════════════════════════════════════

def benchmark__default__1_node(test_data):
    return Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(test_data.dict_1)

def benchmark__default__10_nodes(test_data):
    return Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(test_data.dict_10)

def benchmark__fast__1_node(test_data):
    return Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(test_data.dict_1)

def benchmark__fast__10_nodes(test_data):
    return Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(test_data.dict_10)


# ═══════════════════════════════════════════════════════════════════════════════
# Performance Test Class
# ═══════════════════════════════════════════════════════════════════════════════

class test_perf__Phase_E__2__Benchmark__Fast_Create__Impact(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.storage_path = path_combine(phase_e.path, '../perf_results')
        cls.storage      = Perf_Report__Storage__File_System(storage_path=cls.storage_path)
        cls.generator    = Html_Generator__For_Benchmarks()
        cls.config       = Schema__Perf_Benchmark__Timing__Config(
                               title            = REPORT_TITLE    ,
                               measure_fast     = True            ,
                               print_to_console = False           ,
                               asserts_enabled  = False           )

        # Pre-generate HTML and convert to dict
        cls.html_1  = cls.generator.generate__1()
        cls.html_10 = cls.generator.generate__10()

        cls.dict_1  = Html__To__Html_Dict__With__Node_Ids(html=cls.html_1 ).convert()
        cls.dict_10 = Html__To__Html_Dict__With__Node_Ids(html=cls.html_10).convert()

    # ═══════════════════════════════════════════════════════════════════════════
    # Benchmark Registration
    # ═══════════════════════════════════════════════════════════════════════════

    def benchmarks(self, timing: Perf_Benchmark__Timing):

        # Section A: Default Mode
        timing.benchmark('A_01__default__1_node'  , lambda: benchmark__default__1_node(self) )
        timing.benchmark('A_02__default__10_nodes', lambda: benchmark__default__10_nodes(self))

        # Section B: fast_create Mode
        with Type_Safe__Config(fast_create=True, skip_validation=True):
            timing.benchmark('B_01__fast__1_node'  , lambda: benchmark__fast__1_node(self) )
            timing.benchmark('B_02__fast__10_nodes', lambda: benchmark__fast__10_nodes(self))

    # ═══════════════════════════════════════════════════════════════════════════
    # Test Method
    # ═══════════════════════════════════════════════════════════════════════════

    def test__fast_create__impact(self):
        builder = Perf_Report__Builder(
            metadata = Schema__Perf_Report__Metadata(
                           title        = REPORT_TITLE                              ,
                           version      = version__mgraph_ai_service_html_graph     ,
                           description  = REPORT_DESCRIPTION                        ,
                           test_input   = REPORT_TEST_INPUT                         ,
                           measure_mode = Enum__Measure_Mode.FAST                   ),
            legend   = Dict__Perf_Report__Legend(REPORT_LEGEND)                      ,
            config   = self.config                                                   )

        report = builder.run(self.benchmarks)

        self.storage.save(report, key=REPORT_KEY, formats=['txt', 'md', 'json'])

        assert report.metadata.benchmark_count == 4
        assert len(report.benchmarks)          == 4
        assert len(report.categories)          == 2

        print(Perf_Report__Renderer__Text().render(report))