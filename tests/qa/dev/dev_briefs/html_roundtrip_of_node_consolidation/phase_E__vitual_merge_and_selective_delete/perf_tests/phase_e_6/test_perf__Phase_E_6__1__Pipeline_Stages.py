# ═══════════════════════════════════════════════════════════════════════════════
# Performance Benchmark: Phase E_6 - Pipeline Stages Breakdown
# Analyzes: L1 (Parse) → L2 (Graph) → L3 (Reconstruct) conversion pipeline
# ═══════════════════════════════════════════════════════════════════════════════
#
# Phase E_6 Test 1: Establish baseline performance for each pipeline stage
#
# Pipeline stages measured:
#   L1: Html__To__Html_Dict__With__Node_Ids.convert()       - HTML parsing
#   L2: Html__To__Html_MGraph__Document__Node_Id_Reuse.convert_from_dict()  - Graph construction
#   L3: Html_MGraph__Document__To__Html__With_Original_Head.convert()       - Reconstruction
#
# SECTIONS:
#   A_xx - Individual stage isolation (100 nodes)
#   B_xx - Full pipeline reference
#
# ═══════════════════════════════════════════════════════════════════════════════

import phase_e
from unittest                                                                                               import TestCase
from mgraph_ai_service_html_graph.utils.Version                                                             import version__mgraph_ai_service_html_graph
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids        import Html__To__Html_Dict__With__Node_Ids
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse
from osbot_utils.helpers.performance.benchmark.Perf_Benchmark__Timing                                       import Perf_Benchmark__Timing
from osbot_utils.helpers.performance.benchmark.schemas.enums.Enum__Measure_Mode                             import Enum__Measure_Mode
from osbot_utils.helpers.performance.benchmark.schemas.timing.Schema__Perf_Benchmark__Timing__Config        import Schema__Perf_Benchmark__Timing__Config
from osbot_utils.testing.Graph__Deterministic__Ids                                                          import graph_deterministic_ids
from osbot_utils.type_safe.type_safe_core.config.type_safe_fast_create                                      import type_safe_fast_create
from osbot_utils.utils.Files                                                                                import path_combine
from phase_e.mgraph.Html_MGraph__Document__To__Html__With_Original_Head                                     import Html_MGraph__Document__To__Html__With_Original_Head
from phase_e.performance.Html_Generator__For_Benchmarks                                                     import Html_Generator__For_Benchmarks
from phase_e.report.builder.Perf_Report__Builder                                                            import Perf_Report__Builder
from phase_e.report.collections.Dict__Perf_Report__Legend                                                   import Dict__Perf_Report__Legend
from phase_e.report.renderers.Perf_Report__Renderer__Text                                                   import Perf_Report__Renderer__Text
from phase_e.report.schemas.Schema__Perf_Report__Metadata                                                   import Schema__Perf_Report__Metadata
from phase_e.report.storage.Perf_Report__Storage__File_System                                               import Perf_Report__Storage__File_System


# ═══════════════════════════════════════════════════════════════════════════════
# Report Metadata
# ═══════════════════════════════════════════════════════════════════════════════

REPORT_KEY         = 'perf_6_1__pipeline_stages__100_nodes'
REPORT_TITLE       = 'Phase E_6: Pipeline Stages Breakdown'
REPORT_DESCRIPTION = ('Establishes baseline performance for each LETS pipeline stage. '
                      'Measures L1 (HTML parsing), L2 (MGraph construction), and L3 (HTML reconstruction). '
                      'Validates that sum of parts ≈ full pipeline.')
REPORT_TEST_INPUT  = 'Synthetic HTML with 100 paragraphs (~300 nodes)'
REPORT_LEGEND      = {'A': 'Individual stage isolation  = Each stage measured independently'  ,
                      'B': 'Full pipeline reference     = Complete L1→L2→L3 for validation'  }


# ═══════════════════════════════════════════════════════════════════════════════
# State Factory - Creates exact state at each pipeline stage
# ═══════════════════════════════════════════════════════════════════════════════

class Pipeline__State_Factory:                                                  # Creates state at each pipeline stage

    def __init__(self, html: str):
        self.html = html

    def state_for_L1(self) -> dict:                                             # Before L1 - just raw HTML
        return {'html': self.html}

    def state_for_L2(self) -> dict:                                             # After L1 - HTML parsed to dict
        html_dict = Html__To__Html_Dict__With__Node_Ids(html=self.html).convert()
        return {'html'     : self.html    ,
                'html_dict': html_dict    }

    def state_for_L3(self) -> dict:                                             # After L2 - MGraph document created
        html_dict = Html__To__Html_Dict__With__Node_Ids(html=self.html).convert()
        document  = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)
        return {'html'     : self.html    ,
                'html_dict': html_dict    ,
                'document' : document     }


# ═══════════════════════════════════════════════════════════════════════════════
# Performance Test Class
# ═══════════════════════════════════════════════════════════════════════════════

class test_perf__Phase_E_6__1__Pipeline_Stages(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.storage_path = path_combine(phase_e.path, '../perf_results')
        cls.storage      = Perf_Report__Storage__File_System(storage_path=cls.storage_path)
        cls.generator    = Html_Generator__For_Benchmarks()
        cls.config       = Schema__Perf_Benchmark__Timing__Config(title            = REPORT_TITLE,
                                                                  measure_fast     = True        ,
                                                                  print_to_console = False       ,
                                                                  asserts_enabled  = False       )

        # Pre-generate test HTML
        #with graph_deterministic_ids():
        cls.html_10  = cls.generator.generate__10()
        cls.html_50  = cls.generator.generate__50()
        cls.html_100 = cls.generator.generate__100()
        cls.html_200 = cls.generator.generate__200()
        cls.html     = cls.html_100

        # Create state factory for stage isolation
        cls.state_factory = Pipeline__State_Factory(cls.html)

        # Pre-compute states for benchmarks (outside measurement)
        with graph_deterministic_ids():
            cls.state_L1 = cls.state_factory.state_for_L1()
            cls.state_L2 = cls.state_factory.state_for_L2()
            cls.state_L3 = cls.state_factory.state_for_L3()

    # ═══════════════════════════════════════════════════════════════════════════
    # Benchmark Registration
    # ═══════════════════════════════════════════════════════════════════════════

    def benchmarks(self, timing: Perf_Benchmark__Timing):

        html      = self.state_L1['html']
        html_dict = self.state_L2['html_dict']
        document  = self.state_L3['document']

        # ───────────────────────────────────────────────────────────────────────
        # Section A: Individual Stage Isolation
        # ───────────────────────────────────────────────────────────────────────

        # A_01: L1 - HTML String → Dict (parsing)
        def stage_A_01__L1__html_to_dict():
            return Html__To__Html_Dict__With__Node_Ids(html=html).convert()

        timing.benchmark('A_01__L1__html_to_dict', stage_A_01__L1__html_to_dict)

        # A_02: L2 - Dict → MGraph Document (graph construction)
        def stage_A_02__L2__dict_to_mgraph():
            return Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)

        timing.benchmark('A_02__L2__dict_to_mgraph', stage_A_02__L2__dict_to_mgraph)

        # A_03: L3 - MGraph → HTML String (reconstruction with original head)
        converter_L3 = Html_MGraph__Document__To__Html__With_Original_Head(original_html_dict=html_dict)

        def stage_A_03__L3__mgraph_to_html():
            return converter_L3.convert(document)

        timing.benchmark('A_03__L3__mgraph_to_html', stage_A_03__L3__mgraph_to_html)

        # ───────────────────────────────────────────────────────────────────────
        # Section B: Full Pipeline Reference
        # ───────────────────────────────────────────────────────────────────────

        # B_01: Full L1→L2→L3 pipeline (for validation: should ≈ A_01 + A_02 + A_03)
        def stage_B_01__full_pipeline():
            step_1__html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()
            step_2__document  = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(step_1__html_dict)
            step_3__converter = Html_MGraph__Document__To__Html__With_Original_Head(original_html_dict=step_1__html_dict)
            step_4__html_out  = step_3__converter.convert(step_2__document)
            return step_4__html_out

        timing.benchmark('B_01__full_pipeline__L1_L2_L3', stage_B_01__full_pipeline)

    # ═══════════════════════════════════════════════════════════════════════════
    # Test Method
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test__pipeline_stages__breakdown(self):
        builder = Perf_Report__Builder(metadata = Schema__Perf_Report__Metadata(title        = REPORT_TITLE                         ,
                                                                                version      = version__mgraph_ai_service_html_graph,
                                                                                description  = REPORT_DESCRIPTION                   ,
                                                                                test_input   = REPORT_TEST_INPUT                    ,
                                                                                measure_mode = Enum__Measure_Mode.FAST              ),
                                       legend   = Dict__Perf_Report__Legend(REPORT_LEGEND)                                           ,
                                       config   = self.config                                                                        )

        report = builder.run(self.benchmarks)

        # Save report in multiple formats
        self.storage.save(report, key=REPORT_KEY, formats=['txt'])

        # Validate structure
        assert report.metadata.benchmark_count == 4                             # A_01, A_02, A_03, B_01
        assert len(report.benchmarks)          == 4
        assert len(report.categories)          == 2                             # A and B sections

        # Print report to console (all insights are in the report)
        print(Perf_Report__Renderer__Text().render(report))