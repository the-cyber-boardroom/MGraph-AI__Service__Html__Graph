# ═══════════════════════════════════════════════════════════════════════════════
# Performance Benchmark: convert_from_dict Breakdown
# Analyzes: Where time is spent inside the 95% bottleneck
# ═══════════════════════════════════════════════════════════════════════════════
#
# convert_from_dict breakdown:
#   1. Html_MGraph__Document().setup()     - Create document with graphs
#   2. process_attrs__html_tag()           - Process <html> attributes
#   3. _extract_head_body()                - Find head/body dicts
#   4. _process_head()                     - Process <head> section
#   5. _process_body()                     - Process <body> section
#
# SECTIONS:
#   A_xx - Stages of convert_from_dict (setup, extract, attrs, head, body, full)
#
# ═══════════════════════════════════════════════════════════════════════════════

import phase_e
from unittest                                                                                                   import TestCase
from mgraph_ai_service_html_graph.utils.Version                                                                 import version__mgraph_ai_service_html_graph
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids            import Html__To__Html_Dict__With__Node_Ids
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document                              import Html_MGraph__Document
from osbot_utils.helpers.performance.benchmark.Perf_Benchmark__Timing                                           import Perf_Benchmark__Timing
from osbot_utils.helpers.performance.benchmark.schemas.enums.Enum__Measure_Mode                                 import Enum__Measure_Mode
from osbot_utils.helpers.performance.benchmark.schemas.timing.Schema__Perf_Benchmark__Timing__Config            import Schema__Perf_Benchmark__Timing__Config
from osbot_utils.type_safe.type_safe_core.config.type_safe_fast_create                                          import type_safe_fast_create
from osbot_utils.utils.Files                                                                                    import path_combine
from phase_e.performance.Html_Generator__For_Benchmarks                                                         import Html_Generator__For_Benchmarks
from phase_e.report.builder.Perf_Report__Builder                                                                import Perf_Report__Builder
from phase_e.report.collections.Dict__Perf_Report__Legend                                                       import Dict__Perf_Report__Legend
from phase_e.report.renderers.Perf_Report__Renderer__Text                                                       import Perf_Report__Renderer__Text
from phase_e.report.schemas.Schema__Perf_Report__Metadata                                                       import Schema__Perf_Report__Metadata
from phase_e.report.storage.Perf_Report__Storage__File_System                                                   import Perf_Report__Storage__File_System


# ═══════════════════════════════════════════════════════════════════════════════
# Report Metadata
# ═══════════════════════════════════════════════════════════════════════════════

REPORT_KEY         = 'perf_4__benchmark__convert_from_dict__breakdown'
REPORT_TITLE       = 'convert_from_dict: Internal Breakdown'
REPORT_DESCRIPTION = ('Breaks down the 95% bottleneck (convert_from_dict) into its component stages. '
                      'Each stage is measured in isolation with exact pre-computed state.')
REPORT_TEST_INPUT  = 'HTML with 10 nodes'
REPORT_LEGEND      = { 'A': 'convert_from_dict stages = Document setup, extract, attrs, head, body, full' }


# ═══════════════════════════════════════════════════════════════════════════════
# Benchmark Targets - Each receives exact state from previous stage
# ═══════════════════════════════════════════════════════════════════════════════

def benchmark__document_setup():                                                # Stage 1: Create document with graphs
    return Html_MGraph__Document().setup()

def benchmark__extract_head_body(converter, html_dict):                         # Stage 2: Find head/body in dict
    return converter._extract_head_body(html_dict)

def benchmark__process_attrs_html_tag(converter, html_dict, document):          # Stage 3: Process <html> attributes
    return converter.process_attrs__html_tag(html_dict, document)

def benchmark__process_head(converter, document, head_dict):                    # Stage 4: Process <head> section
    return converter._process_head(document, head_dict)

def benchmark__process_body(converter, document, body_dict):                    # Stage 5: Process <body> section
    return converter._process_body(document, body_dict)

def benchmark__full_convert_from_dict(converter, html_dict):                    # Full method for reference
    return converter.convert_from_dict(html_dict)


# ═══════════════════════════════════════════════════════════════════════════════
# State Factory - Creates exact state at each stage of convert_from_dict
# ═══════════════════════════════════════════════════════════════════════════════

class Convert_From_Dict__State_Factory:                                         # Creates state at each pipeline stage

    def __init__(self, html_dict):
        self.html_dict = html_dict

    def state_for_stage_1(self):                                                # Before document_setup
        return {}                                                               # No prior state needed

    def state_for_stage_2(self):                                                # After document_setup, before extract
        document = Html_MGraph__Document().setup()
        return {'document': document}

    def state_for_stage_3(self):                                                # After extract, before process_attrs
        document               = Html_MGraph__Document().setup()
        converter              = Html__To__Html_MGraph__Document__Node_Id_Reuse()
        head_dict, body_dict   = converter._extract_head_body(self.html_dict)
        return {'document' : document ,
                'head_dict': head_dict,
                'body_dict': body_dict}

    def state_for_stage_4(self):                                                # After attrs, before process_head
        document               = Html_MGraph__Document().setup()
        converter              = Html__To__Html_MGraph__Document__Node_Id_Reuse()
        head_dict, body_dict   = converter._extract_head_body(self.html_dict)
        converter.process_attrs__html_tag(self.html_dict, document)
        return {'document' : document ,
                'head_dict': head_dict,
                'body_dict': body_dict}

    def state_for_stage_5(self):                                                # After head, before process_body
        document               = Html_MGraph__Document().setup()
        converter              = Html__To__Html_MGraph__Document__Node_Id_Reuse()
        head_dict, body_dict   = converter._extract_head_body(self.html_dict)
        converter.process_attrs__html_tag(self.html_dict, document)
        if head_dict:
            converter._process_head(document, head_dict)
        return {'document' : document ,
                'body_dict': body_dict}


# ═══════════════════════════════════════════════════════════════════════════════
# Performance Test Class
# ═══════════════════════════════════════════════════════════════════════════════

class test_perf__Phase_E__4__Benchmark__Convert_From_Dict__Breakdown(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.storage_path  = path_combine(phase_e.path, '../perf_results')
        cls.storage       = Perf_Report__Storage__File_System(storage_path=cls.storage_path)
        cls.generator     = Html_Generator__For_Benchmarks()
        cls.config        = Schema__Perf_Benchmark__Timing__Config(title            = REPORT_TITLE,
                                                                   measure_fast     = True        ,
                                                                   print_to_console = False       ,
                                                                   asserts_enabled  = False       )
        # Pre-generate test data
        cls.html_1        = cls.generator.generate__1()
        cls.html_10        = cls.generator.generate__10()
        cls.html_50        = cls.generator.generate__50()
        cls.html_100       = cls.generator.generate__100()
        cls.html_500       = cls.generator.generate__500()
        cls.html_1_000     = cls.generator.generate__1_000()
        cls.html_10_000    = cls.generator.generate__10_000()
        cls.html           = cls.html_10_000

        cls.html_dict       = Html__To__Html_Dict__With__Node_Ids(html=cls.html).convert()

        # Create state factory
        cls.state_factory = Convert_From_Dict__State_Factory(cls.html_dict)

        # Pre-extract head/body for conditional benchmark
        converter                    = Html__To__Html_MGraph__Document__Node_Id_Reuse()
        cls.head_dict, cls.body_dict = converter._extract_head_body(cls.html_dict)

    # ═══════════════════════════════════════════════════════════════════════════
    # Benchmark Registration
    # ═══════════════════════════════════════════════════════════════════════════

    def benchmarks(self, timing: Perf_Benchmark__Timing):

        # Stage 1: Document setup (no prior state needed)
        timing.benchmark('A_01__document_setup',
            lambda: benchmark__document_setup())

        # Stage 2: Extract head/body (needs document from stage 1)
        timing.benchmark('A_02__extract_head_body',
            lambda: benchmark__extract_head_body(Html__To__Html_MGraph__Document__Node_Id_Reuse(),
                                                 self.html_dict))

        # Stage 3: Process <html> attrs (needs state from stage 2)
        state_3 = self.state_factory.state_for_stage_3()
        timing.benchmark('A_03__process_attrs_html_tag',
            lambda: benchmark__process_attrs_html_tag(Html__To__Html_MGraph__Document__Node_Id_Reuse(),
                                                      self.html_dict        ,
                                                      state_3['document']))

        # Stage 4: Process head (needs state from stage 3)
        if self.head_dict:
            state_4 = self.state_factory.state_for_stage_4()
            timing.benchmark('A_04__process_head',
                lambda: benchmark__process_head(Html__To__Html_MGraph__Document__Node_Id_Reuse(),
                                                state_4['document'] ,
                                                state_4['head_dict']))

        # Stage 5: Process body (needs state from stage 4)
        state_5 = self.state_factory.state_for_stage_5()
        timing.benchmark('A_05__process_body',
            lambda: benchmark__process_body(Html__To__Html_MGraph__Document__Node_Id_Reuse(),
                                            state_5['document'] ,
                                            state_5['body_dict']))

        # Full method for comparison (A_01 + A_02 + A_03 + A_04 + A_05 should ≈ A_06)
        timing.benchmark('A_06__full_convert_from_dict',
            lambda: benchmark__full_convert_from_dict(Html__To__Html_MGraph__Document__Node_Id_Reuse(),
                                                      self.html_dict))

    # ═══════════════════════════════════════════════════════════════════════════
    # Test Method
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test__convert_from_dict__breakdown(self):
        builder = Perf_Report__Builder(metadata = Schema__Perf_Report__Metadata(title        = REPORT_TITLE                         ,
                                                                                version      = version__mgraph_ai_service_html_graph,
                                                                                description  = REPORT_DESCRIPTION                   ,
                                                                                test_input   = REPORT_TEST_INPUT                    ,
                                                                                measure_mode = Enum__Measure_Mode.FAST              ),
                                       legend   = Dict__Perf_Report__Legend(REPORT_LEGEND)                                           ,
                                       config   = self.config                                                                        )

        report = builder.run(self.benchmarks)

        self.storage.save(report, key=REPORT_KEY, formats=['txt', 'md', 'json'])

        expected_count = 6 if self.head_dict else 5
        assert report.metadata.benchmark_count == expected_count
        assert len(report.benchmarks)          == expected_count
        assert len(report.categories)          == 1

        print(Perf_Report__Renderer__Text().render(report))