# ═══════════════════════════════════════════════════════════════════════════════
# Test: Phase E_2 Conversion Detailed Breakdown
# Uses the new Perf_Report framework for structured reporting
# ═══════════════════════════════════════════════════════════════════════════════
from unittest import TestCase

import phase_e
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html import Html_MGraph__Document__To__Html
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids import Html__To__Html_Dict__With__Node_Ids
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse
from osbot_utils.helpers.performance.benchmark.Perf_Benchmark__Timing import Perf_Benchmark__Timing
from osbot_utils.helpers.performance.benchmark.schemas.enums.Enum__Measure_Mode import Enum__Measure_Mode
from osbot_utils.helpers.performance.benchmark.schemas.timing.Schema__Perf_Benchmark__Timing__Config import Schema__Perf_Benchmark__Timing__Config
from osbot_utils.utils.Files import path_combine
from phase_e.report.builder.Perf_Report__Builder import Perf_Report__Builder
from phase_e.report.collections.Dict__Perf_Report__Legend import Dict__Perf_Report__Legend
from phase_e.report.renderers.Perf_Report__Renderer__Text import Perf_Report__Renderer__Text
from phase_e.report.schemas.Schema__Perf_Report__Metadata import Schema__Perf_Report__Metadata
from phase_e.report.storage.Perf_Report__Storage__File_System import Perf_Report__Storage__File_System

# Assuming these exist in your project - replace with actual imports
# from mgraph_ai_service_html_graph                                                                             import version__mgraph_ai_service_html_graph
# from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids          import Html__To__Html_Dict__With__Node_Ids
# from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse
# from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html              import Html_MGraph__Document__To__Html


# ═══════════════════════════════════════════════════════════════════════════════
# Test HTML
# ═══════════════════════════════════════════════════════════════════════════════

HTML_SIMPLE = "<html><body><div><p>Hello World</p></div></body></html>"


# ═══════════════════════════════════════════════════════════════════════════════
# Test Class
# ═══════════════════════════════════════════════════════════════════════════════

class test_perf__Phase_E_2__Conversion__Detailed(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.html         = HTML_SIMPLE
        cls.storage_path = path_combine(phase_e.path, '../perf_results')
        cls.storage      = Perf_Report__Storage__File_System(storage_path=cls.storage_path)
        cls.config       = Schema__Perf_Benchmark__Timing__Config(
            title            = 'Phase E_2 Conversion Detailed'    ,
            measure_fast     = True                               ,
            print_to_console = False                              ,
            asserts_enabled  = False                              )

        # Pre-compute intermediate values (uncomment when real converters available)
        cls.html_dict = Html__To__Html_Dict__With__Node_Ids(html=cls.html).convert()
        cls.document  = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(cls.html_dict)

    # ═══════════════════════════════════════════════════════════════════════════
    # Benchmark Definition - THE ONLY THING USER WRITES
    # ═══════════════════════════════════════════════════════════════════════════

    def benchmarks(self, timing: Perf_Benchmark__Timing):         # User's benchmark function
        # ───────────────────────────────────────────────────────────────────────
        # Section A: Full Operations (create converter + convert)
        # ───────────────────────────────────────────────────────────────────────
        timing.benchmark('A_01__html_to_dict__full',
            lambda: Html__To__Html_Dict__With__Node_Ids(html=self.html).convert())
        timing.benchmark('A_02__dict_to_mgraph__full',
            lambda: Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(self.html_dict))
        timing.benchmark('A_03__mgraph_to_html__full',
            lambda: Html_MGraph__Document__To__Html().convert(self.document))

        # ───────────────────────────────────────────────────────────────────────
        # Section B: Converter Creation Only
        # ───────────────────────────────────────────────────────────────────────
        timing.benchmark('B_01__converter_1_create',
            lambda: Html__To__Html_Dict__With__Node_Ids(html=self.html))
        timing.benchmark('B_02__converter_2_create',
            Html__To__Html_MGraph__Document__Node_Id_Reuse)
        timing.benchmark('B_03__converter_3_create',
            Html_MGraph__Document__To__Html)

        # ───────────────────────────────────────────────────────────────────────
        # Section C: Conversion Only (pre-created converters)
        # ───────────────────────────────────────────────────────────────────────
        converter_1 = Html__To__Html_Dict__With__Node_Ids(html=self.html)
        timing.benchmark('C_01__html_to_dict__convert_only', converter_1.convert)

        converter_2 = Html__To__Html_MGraph__Document__Node_Id_Reuse()
        timing.benchmark('C_02__dict_to_mgraph__convert_only',
            lambda: converter_2.convert_from_dict(self.html_dict))

        converter_3 = Html_MGraph__Document__To__Html()
        timing.benchmark('C_03__mgraph_to_html__convert_only',
            lambda: converter_3.convert(self.document))

        # ───────────────────────────────────────────────────────────────────────
        # Mock benchmarks for testing the framework
        # ───────────────────────────────────────────────────────────────────────
        # import time
        # timing.benchmark('A_01__html_to_dict__full'    , lambda: time.sleep(0.00002))
        # timing.benchmark('A_02__dict_to_mgraph__full'  , lambda: time.sleep(0.014))
        # timing.benchmark('A_03__mgraph_to_html__full'  , lambda: time.sleep(0.0006))
        #
        # timing.benchmark('B_01__converter_1_create'    , lambda: time.sleep(0.0000005))
        # timing.benchmark('B_02__converter_2_create'    , lambda: time.sleep(0.000001))
        # timing.benchmark('B_03__converter_3_create'    , lambda: time.sleep(0.0000008))
        #
        # timing.benchmark('C_01__html_to_dict__convert' , lambda: time.sleep(0.00002))
        # timing.benchmark('C_02__dict_to_mgraph__convert', lambda: time.sleep(0.014))
        # timing.benchmark('C_03__mgraph_to_html__convert', lambda: time.sleep(0.0006))

    # ═══════════════════════════════════════════════════════════════════════════
    # Test Method - Uses the Framework
    # ═══════════════════════════════════════════════════════════════════════════

    def test__conversion_detailed_breakdown(self):
        """
        Detailed breakdown of HTML conversion pipeline.
        Uses the new Phase E_2 report framework.
        """
        builder = Perf_Report__Builder(
            metadata = Schema__Perf_Report__Metadata(
                title       = 'Phase E: Conversion Pipeline - Detailed Breakdown',
                version     = '0.8.5'                                            ,  # Replace with actual version
                description = 'Isolates converter creation from conversion logic to identify bottleneck.',
                test_input  = HTML_SIMPLE[:50] + '...'                           ,
                measure_mode = Enum__Measure_Mode.FAST                           ),
            legend = Dict__Perf_Report__Legend({
                'A': 'Full Operation      = Create converter instance + call convert()',
                'B': 'Converter Creation  = Only create converter instance (no conversion)',
                'C': 'Convert Only        = Call convert() on pre-created instance'}),
            config = self.config)

        # Run benchmarks and get structured report
        report = builder.run(self.benchmarks)

        # Save in multiple formats
        self.storage.save(report                             ,
                          key     = 'conversion__detailed'   ,
                          formats = ['txt', 'md', 'json']    )

        # Verify report structure
        assert report.metadata.benchmark_count == 9
        assert len(report.benchmarks)          == 9
        assert len(report.categories)          == 3            # A, B, C

        # Print report to console for verification

        # renderer = Perf_Report__Renderer__Text()
        # print(renderer.render(report))
