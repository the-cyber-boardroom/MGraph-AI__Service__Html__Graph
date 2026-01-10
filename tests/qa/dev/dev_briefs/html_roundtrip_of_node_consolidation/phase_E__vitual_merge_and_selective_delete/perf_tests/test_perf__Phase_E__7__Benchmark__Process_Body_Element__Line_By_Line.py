# ═══════════════════════════════════════════════════════════════════════════════
# Performance Benchmark: _process_body__element Line-by-Line
# Analyzes: Exact code flow inside the element processing bottleneck
# ═══════════════════════════════════════════════════════════════════════════════
#
# "Follow the Rabbit Hole" Pattern - Level 3
#
# _process_body__element code flow:
#   A_01: node_id = self._generate_node_id()
#   A_02: self._process_body__create_in_graph(...)
#   A_03: self._process_body__register_attrs(...)
#   A_04: self._process_body_children(...) ← RECURSIVE
#   A_05: Full _process_body__element (reference)
#
# For our HTML structure (body > p > TEXT):
#   - Each <p> has one TEXT child
#   - A_04 recursively calls _process_body_children for <p>
#   - Which finds TEXT and calls _process_body__text_node
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
from osbot_utils.testing.Graph__Deterministic__Ids                                                              import graph_deterministic_ids
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

REPORT_KEY         = 'perf_7__benchmark__process_body_element__line_by_line'
REPORT_TITLE       = '_process_body__element: Line-by-Line'
REPORT_DESCRIPTION = ('Follow the Rabbit Hole Level 3: Break down the element processing. '
                      'Measures node ID generation, graph creation, attribute registration, and recursive children.')
REPORT_TEST_INPUT  = 'Single element processing, then full loop'
REPORT_LEGEND      = { 'A': '_process_body__element operations (single element)',
                       'B': 'Full loop processing (all elements)'              }


# ═══════════════════════════════════════════════════════════════════════════════
# Performance Test Class
# ═══════════════════════════════════════════════════════════════════════════════

class test_perf__Phase_E__7__Benchmark__Process_Body_Element__Line_By_Line(TestCase):

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
            cls.html_1       = cls.generator.generate__1    ()
            cls.html_10      = cls.generator.generate__10   ()
            cls.html_50      = cls.generator.generate__50   ()
            cls.html_100     = cls.generator.generate__100  ()
            cls.html_200     = cls.generator.generate__200  ()
            cls.html_500     = cls.generator.generate__500  ()
            cls.html_1_000   = cls.generator.generate__1_000()
            cls.html         = cls.html_100
            cls.html_dict    = Html__To__Html_Dict__With__Node_Ids(html=cls.html).convert()

        # Pre-extract body_dict and nodes
        converter        = Html__To__Html_MGraph__Document__Node_Id_Reuse()
        _, cls.body_dict = converter._extract_head_body(cls.html_dict)
        cls.nodes        = cls.body_dict.get('nodes', [])

        # Extract first <p> element for single-element tests
        cls.first_p_node = cls.nodes[0] if cls.nodes else None

    # ═══════════════════════════════════════════════════════════════════════════
    # Benchmark Registration
    # ═══════════════════════════════════════════════════════════════════════════

    def benchmarks(self, timing: Perf_Benchmark__Timing):
        body_dict    = self.body_dict
        nodes        = self.nodes
        first_p_node = self.first_p_node
        body_node_id = 'f0000005'

        # ───────────────────────────────────────────────────────────────────────
        # Helper: Create fresh document with body root
        # ───────────────────────────────────────────────────────────────────────
        def create_fresh_document_with_body():
            document = Html_MGraph__Document().setup()
            document.body_graph.create_element(node_path=Node_Path('body'), node_id=body_node_id)
            document.body_graph.set_root(body_node_id)
            document.attrs_graph.register_element(body_node_id, 'body')
            return document

        # ═══════════════════════════════════════════════════════════════════════
        # Section A: Single element operations
        # ═══════════════════════════════════════════════════════════════════════

        # ───────────────────────────────────────────────────────────────────────
        # A_01: node_id = self._generate_node_id()
        # ───────────────────────────────────────────────────────────────────────
        converter_A_01 = Html__To__Html_MGraph__Document__Node_Id_Reuse()

        def stage_A_01__generate_node_id():
            node_id = converter_A_01._generate_node_id()
            return node_id

        timing.benchmark('A_01__generate_node_id', stage_A_01__generate_node_id)

        # ───────────────────────────────────────────────────────────────────────
        # A_02: self._process_body__create_in_graph(...)
        # ───────────────────────────────────────────────────────────────────────
        document_A_02  = create_fresh_document_with_body()
        converter_A_02 = Html__To__Html_MGraph__Document__Node_Id_Reuse()

        def stage_A_02__create_in_graph():
            node_id = converter_A_02._generate_node_id()
            converter_A_02._process_body__create_in_graph(document_A_02, body_node_id,
                                                          node_id, 0, 'body.p[0]')

        timing.benchmark('A_02__create_in_graph', stage_A_02__create_in_graph)

        # ───────────────────────────────────────────────────────────────────────
        # A_03: self._process_body__register_attrs(...)
        # ───────────────────────────────────────────────────────────────────────
        document_A_03  = create_fresh_document_with_body()
        converter_A_03 = Html__To__Html_MGraph__Document__Node_Id_Reuse()

        def stage_A_03__register_attrs():
            node_id = converter_A_03._generate_node_id()
            converter_A_03._process_body__create_in_graph(document_A_03, body_node_id,
                                                          node_id, 0, 'body.p[0]')
            converter_A_03._process_body__register_attrs(document_A_03, node_id, 'p', first_p_node)

        timing.benchmark('A_03__register_attrs', stage_A_03__register_attrs)

        # ───────────────────────────────────────────────────────────────────────
        # A_04: self._process_body_children(...) - RECURSIVE for single <p>
        # This processes the TEXT child inside the <p>
        # ───────────────────────────────────────────────────────────────────────
        document_A_04  = create_fresh_document_with_body()
        converter_A_04 = Html__To__Html_MGraph__Document__Node_Id_Reuse()

        def stage_A_04__process_children_single():
            node_id = converter_A_04._generate_node_id()
            converter_A_04._process_body__create_in_graph(document_A_04, body_node_id,
                                                          node_id, 0, 'body.p[0]')
            converter_A_04._process_body__register_attrs(document_A_04, node_id, 'p', first_p_node)
            converter_A_04._process_body_children(document_A_04, node_id, first_p_node, 'body.p[0]')

        timing.benchmark('A_04__process_children_single', stage_A_04__process_children_single)

        # ───────────────────────────────────────────────────────────────────────
        # A_05: Full _process_body__element for single <p> (reference)
        # ───────────────────────────────────────────────────────────────────────
        document_A_05  = create_fresh_document_with_body()
        converter_A_05 = Html__To__Html_MGraph__Document__Node_Id_Reuse()

        def stage_A_05__full_process_element_single():
            converter_A_05._process_body__element(document_A_05, body_node_id, first_p_node,
                                                   0, 'p', 'body.p[0]')

        timing.benchmark('A_05__full_process_element_single', stage_A_05__full_process_element_single)

        # ═══════════════════════════════════════════════════════════════════════
        # Section B: Full loop processing (all elements)
        # ═══════════════════════════════════════════════════════════════════════

        # ───────────────────────────────────────────────────────────────────────
        # B_01: _generate_node_id for ALL elements
        # ───────────────────────────────────────────────────────────────────────
        converter_B_01 = Html__To__Html_MGraph__Document__Node_Id_Reuse()

        def stage_B_01__generate_node_id_all():
            for position, node in enumerate(nodes):
                if not isinstance(node, dict):
                    continue
                if 'tag' in node:
                    node_id = converter_B_01._generate_node_id()

        timing.benchmark('B_01__generate_node_id_all', stage_B_01__generate_node_id_all)

        # ───────────────────────────────────────────────────────────────────────
        # B_02: _generate_node_id + _create_in_graph for ALL elements
        # ───────────────────────────────────────────────────────────────────────
        document_B_02  = create_fresh_document_with_body()
        converter_B_02 = Html__To__Html_MGraph__Document__Node_Id_Reuse()

        def stage_B_02__create_in_graph_all():
            tag_counts     = converter_B_02._count_tags(nodes)
            tag_occurrence = {}
            for position, node in enumerate(nodes):
                if not isinstance(node, dict):
                    continue
                if 'tag' in node:
                    tag       = node.get('tag', '').lower()
                    tag_index = tag_occurrence.get(tag, 0)
                    tag_occurrence[tag] = tag_index + 1
                    if tag_counts.get(tag, 0) > 1:
                        node_path = f"body.{tag}[{tag_index}]"
                    else:
                        node_path = f"body.{tag}"
                    node_id = converter_B_02._generate_node_id()
                    converter_B_02._process_body__create_in_graph(document_B_02, body_node_id,
                                                                   node_id, position, node_path)

        timing.benchmark('B_02__create_in_graph_all', stage_B_02__create_in_graph_all)

        benchmark_b_02__result = timing.results.get('B_02__create_in_graph_all')


        # ───────────────────────────────────────────────────────────────────────
        # B_03: _generate_node_id + _create_in_graph + _register_attrs for ALL
        # ───────────────────────────────────────────────────────────────────────
        document_B_03  = create_fresh_document_with_body()
        converter_B_03 = Html__To__Html_MGraph__Document__Node_Id_Reuse()

        def stage_B_03__register_attrs_all():
            tag_counts     = converter_B_03._count_tags(nodes)
            tag_occurrence = {}
            for position, node in enumerate(nodes):
                if not isinstance(node, dict):
                    continue
                if 'tag' in node:
                    tag       = node.get('tag', '').lower()
                    tag_index = tag_occurrence.get(tag, 0)
                    tag_occurrence[tag] = tag_index + 1
                    if tag_counts.get(tag, 0) > 1:
                        node_path = f"body.{tag}[{tag_index}]"
                    else:
                        node_path = f"body.{tag}"
                    node_id = converter_B_03._generate_node_id()
                    converter_B_03._process_body__create_in_graph(document_B_03, body_node_id,
                                                                   node_id, position, node_path)
                    converter_B_03._process_body__register_attrs(document_B_03, node_id, tag, node)

        timing.benchmark('B_03__register_attrs_all', stage_B_03__register_attrs_all)

        benchmark_b_03__result = timing.results.get('B_03__register_attrs_all')
        benchmark_b_03__result.final_score -= benchmark_b_02__result.final_score
        benchmark_b_03__result.raw_score   -= benchmark_b_02__result.raw_score

        # ───────────────────────────────────────────────────────────────────────
        # B_04: Full _process_body__element for ALL (includes recursive children)
        # ───────────────────────────────────────────────────────────────────────
        document_B_04  = create_fresh_document_with_body()
        converter_B_04 = Html__To__Html_MGraph__Document__Node_Id_Reuse()

        def stage_B_04__full_process_element_all():
            tag_counts     = converter_B_04._count_tags(nodes)
            tag_occurrence = {}
            for position, node in enumerate(nodes):
                if not isinstance(node, dict):
                    continue
                if 'tag' in node:
                    tag       = node.get('tag', '').lower()
                    tag_index = tag_occurrence.get(tag, 0)
                    tag_occurrence[tag] = tag_index + 1
                    if tag_counts.get(tag, 0) > 1:
                        node_path = f"body.{tag}[{tag_index}]"
                    else:
                        node_path = f"body.{tag}"
                    converter_B_04._process_body__element(document_B_04, body_node_id, node,
                                                          position, tag, node_path)

        timing.benchmark('B_04__full_process_element_all', stage_B_04__full_process_element_all)

        # ───────────────────────────────────────────────────────────────────────
        # B_05: Full _process_body_children (reference from perf_6)
        # ───────────────────────────────────────────────────────────────────────
        document_B_05  = create_fresh_document_with_body()
        converter_B_05 = Html__To__Html_MGraph__Document__Node_Id_Reuse()

        def stage_B_05__full_process_body_children():
            converter_B_05._process_body_children(document_B_05, body_node_id, body_dict, 'body')

        timing.benchmark('B_05__full_process_body_children', stage_B_05__full_process_body_children)

    # ═══════════════════════════════════════════════════════════════════════════
    # Test Method
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test__process_body_element__line_by_line(self):
        builder = Perf_Report__Builder(metadata = Schema__Perf_Report__Metadata(title        = REPORT_TITLE                         ,
                                                                                version      = version__mgraph_ai_service_html_graph,
                                                                                description  = REPORT_DESCRIPTION                   ,
                                                                                test_input   = REPORT_TEST_INPUT                    ,
                                                                                measure_mode = Enum__Measure_Mode.FAST              ),
                                       legend   = Dict__Perf_Report__Legend(REPORT_LEGEND)                                           ,
                                       config   = self.config                                                                        )

        report = builder.run(self.benchmarks)

        self.storage.save(report, key=REPORT_KEY, formats=['txt'])

        print(Perf_Report__Renderer__Text().render(report))