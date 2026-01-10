# ═══════════════════════════════════════════════════════════════════════════════
# Performance Benchmark: _process_body Line-by-Line (Cumulative)
# Analyzes: Exact code flow inside _process_body method
# ═══════════════════════════════════════════════════════════════════════════════
#
# "Follow the Rabbit Hole" Pattern:
#   Each benchmark includes ALL previous steps, then we subtract to get incremental.
#
# _process_body code flow (cumulative):
#   A_01: document.setup() only
#   A_02: A_01 + _generate_node_id()
#   A_03: A_02 + create_element + set_root + register_element
#   A_04: A_03 + attrs for loop
#   A_05: A_04 + _process_body_children() ← THE SCALING BOTTLENECK
#   A_06: Full _process_body (reference - should equal A_05)
#
# Incremental costs (calculated by subtraction):
#   setup_cost              = A_01
#   generate_node_id_cost   = A_02 - A_01
#   create_and_register     = A_03 - A_02
#   add_attributes          = A_04 - A_03
#   process_children        = A_05 - A_04  ← WHERE THE TIME GOES
#
# ═══════════════════════════════════════════════════════════════════════════════

import phase_e
from unittest                                                                                                   import TestCase
from mgraph_ai_service_html_graph.utils.Version                                                                 import version__mgraph_ai_service_html_graph
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids            import Html__To__Html_Dict__With__Node_Ids
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document                              import Html_MGraph__Document
from mgraph_db.mgraph.schemas.identifiers.Node_Path                                                             import Node_Path
from osbot_utils.helpers.performance.benchmark.Perf_Benchmark__Timing                                           import Perf_Benchmark__Timing
from osbot_utils.helpers.performance.benchmark.schemas.enums.Enum__Measure_Mode                                 import Enum__Measure_Mode
from osbot_utils.helpers.performance.benchmark.schemas.timing.Schema__Perf_Benchmark__Timing__Config            import Schema__Perf_Benchmark__Timing__Config
from osbot_utils.testing.Graph__Deterministic__Ids import graph_deterministic_ids
from osbot_utils.testing.__ import __
from osbot_utils.testing.__helpers import obj
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

REPORT_KEY         = 'perf_5__benchmark__process_body__line_by_line'
REPORT_TITLE       = '_process_body: Line-by-Line (Cumulative)'
REPORT_DESCRIPTION = ('Follow the Rabbit Hole: Each benchmark includes all previous steps. '
                      'Incremental costs calculated by subtraction. '
                      'A_05 - A_04 reveals the _process_body_children scaling cost.')
REPORT_TEST_INPUT  = 'HTML body dict with varying node counts'
REPORT_LEGEND      = { 'A': 'Cumulative stages = Each includes all previous code' }


# ═══════════════════════════════════════════════════════════════════════════════
# Performance Test Class
# ═══════════════════════════════════════════════════════════════════════════════

class test_perf__Phase_E__5__Benchmark__Process_Body__Line_By_Line(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.storage_path = path_combine(phase_e.path, '../perf_results')
        cls.storage      = Perf_Report__Storage__File_System(storage_path=cls.storage_path)
        cls.generator    = Html_Generator__For_Benchmarks()
        cls.config       = Schema__Perf_Benchmark__Timing__Config(title            = REPORT_TITLE,
                                                                  measure_fast     = True        ,
                                                                  print_to_console = False       ,
                                                                  asserts_enabled  = False       )

        # Pre-generate test data (change cls.html to test different sizes)
        with graph_deterministic_ids():
            cls.html_1       = cls.generator.generate__1  ()
            cls.html_10      = cls.generator.generate__10 ()
            cls.html_50      = cls.generator.generate__50 ()
            cls.html_100     = cls.generator.generate__100()
            cls.html_200     = cls.generator.generate__200()
            cls.html         = cls.html_100
            cls.html_dict    = Html__To__Html_Dict__With__Node_Ids(html=cls.html).convert()

        # Pre-extract body_dict
        converter        = Html__To__Html_MGraph__Document__Node_Id_Reuse()
        _, cls.body_dict = converter._extract_head_body(cls.html_dict)              # use converter._extract_head_body to create the body_dict value

    # ═══════════════════════════════════════════════════════════════════════════
    # Benchmark Registration - Cumulative "Follow the Rabbit Hole"
    # ═══════════════════════════════════════════════════════════════════════════

    def benchmarks(self, timing: Perf_Benchmark__Timing):
        body_dict           = self.body_dict
        html_to_html_mgraph = Html__To__Html_MGraph__Document__Node_Id_Reuse()
        document            = Html_MGraph__Document().setup()
        # ───────────────────────────────────────────────────────────────────────
        # A_01:
        # ───────────────────────────────────────────────────────────────────────
        def stage_A_01__generate_node_id():
            body_node_id = html_to_html_mgraph._generate_node_id(body_dict)
            assert body_node_id  == 'f0000005'

        timing.benchmark('A_01__generate_node_id', stage_A_01__generate_node_id)

        # ───────────────────────────────────────────────────────────────────────
        # A_02:
        # ───────────────────────────────────────────────────────────────────────
        def stage_A_02__register_element():
            body_node_id  = 'f0000005'
            document.body_graph.create_element(node_path = Node_Path('body'),
                                               node_id   = body_node_id     )
            document.body_graph.set_root(body_node_id)
            document.attrs_graph.register_element(body_node_id, 'body')


        timing.benchmark('A_02__register_element', stage_A_02__register_element)

        # ───────────────────────────────────────────────────────────────────────
        # A_03:
        # ───────────────────────────────────────────────────────────────────────
        def stage_A_03__add_attribute():
            body_node_id = 'f0000005'
            for position, (key, value) in enumerate(body_dict.get('attrs', {}).items()):
                document.attrs_graph.add_attribute(body_node_id, key, value, position)

        timing.benchmark('A_03__add_attribute', stage_A_03__add_attribute)

        # ───────────────────────────────────────────────────────────────────────
        # A_04:
        # ───────────────────────────────────────────────────────────────────────
        def stage_A_04___process_body_children():
            body_node_id = 'f0000005'
            html_to_html_mgraph._process_body_children(document, body_node_id, body_dict, 'body')

        timing.benchmark('A_04___process_body_children', stage_A_04___process_body_children)

        # ───────────────────────────────────────────────────────────────────────
        # A_05:
        # ───────────────────────────────────────────────────────────────────────
        def stage_A_05__full_process_body():
            html_to_html_mgraph._process_body(document, body_dict)
            return document

        timing.benchmark('A_05__full_process_body', stage_A_05__full_process_body)

        # ───────────────────────────────────────────────────────────────────────
        # A_06:
        # ───────────────────────────────────────────────────────────────────────

        html_to_html_mgraph__new = Html__To__Html_MGraph__Document__Node_Id_Reuse()
        document__new            = Html_MGraph__Document().setup()

        def stage_A_06__full_process_body__new_objects():
            html_to_html_mgraph__new._process_body(document__new, body_dict)


        timing.benchmark('A_06__full_process_body__new_objects', stage_A_06__full_process_body__new_objects)

    # ═══════════════════════════════════════════════════════════════════════════
    # Test Method
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test__process_body__line_by_line(self):
        builder = Perf_Report__Builder(metadata = Schema__Perf_Report__Metadata(title        = REPORT_TITLE                         ,
                                                                                version      = version__mgraph_ai_service_html_graph,
                                                                                description  = REPORT_DESCRIPTION                   ,
                                                                                test_input   = REPORT_TEST_INPUT                    ,
                                                                                measure_mode = Enum__Measure_Mode.FAST              ),
                                       legend   = Dict__Perf_Report__Legend(REPORT_LEGEND)                                           ,
                                       config   = self.config                                                                        )

        report = builder.run(self.benchmarks)

        #self.storage.save(report, key=REPORT_KEY, formats=['txt', 'md', 'json'])
        self.storage.save(report, key=REPORT_KEY, formats=['txt'])
