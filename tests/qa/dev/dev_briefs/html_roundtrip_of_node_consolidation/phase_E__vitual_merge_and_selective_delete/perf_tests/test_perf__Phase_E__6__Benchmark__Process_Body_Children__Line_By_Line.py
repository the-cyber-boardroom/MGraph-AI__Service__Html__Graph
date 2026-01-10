# ═══════════════════════════════════════════════════════════════════════════════
# Performance Benchmark: _process_body_children Line-by-Line
# Analyzes: Exact code flow inside the scaling bottleneck
# ═══════════════════════════════════════════════════════════════════════════════
#
# "Follow the Rabbit Hole" Pattern - Level 2
#
# _process_body_children code flow:
#   A_01: nodes = parent_dict.get('nodes', [])
#   A_02: tag_counts = self._count_tags(nodes)
#   A_03: Loop iteration overhead (no processing)
#   A_04: _process_body__text_node for ALL text nodes
#   A_05: _process_body__element for ALL elements (RECURSIVE!)
#   A_06: Full _process_body_children (reference)
#
# Expected: A_05 ≈ A_06 since body children are all elements (no direct text)
# The recursive _process_body__element processes each <p> AND its TEXT child.
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

REPORT_KEY         = 'perf_6__benchmark__process_body_children__line_by_line'
REPORT_TITLE       = '_process_body_children: Line-by-Line'
REPORT_DESCRIPTION = ('Follow the Rabbit Hole Level 2: Break down the recursive _process_body_children. '
                      'Measures tag counting, loop overhead, text node processing, and element processing.')
REPORT_TEST_INPUT  = 'HTML body dict with varying node counts'
REPORT_LEGEND      = { 'A': '_process_body_children operations' }


# ═══════════════════════════════════════════════════════════════════════════════
# Performance Test Class
# ═══════════════════════════════════════════════════════════════════════════════

class test_perf__Phase_E__6__Benchmark__Process_Body_Children__Line_By_Line(TestCase):

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
            cls.html_1         = cls.generator.generate__1  ()
            cls.html_10        = cls.generator.generate__10 ()
            cls.html_50        = cls.generator.generate__50 ()
            cls.html_100       = cls.generator.generate__100()
            cls.html_200       = cls.generator.generate__200()
            cls.html_1_000     = cls.generator.generate__1_000()
            cls.html_10_000    = cls.generator.generate__10_000()
            cls.html_100_000   = cls.generator.generate__100_000()
            cls.html           = cls.html_100
            cls.html_dict      = Html__To__Html_Dict__With__Node_Ids(html=cls.html).convert()

            from osbot_utils.testing.__helpers import obj
            from osbot_utils.testing.__ import __
            # assert cls.html_1 == ('<html>\n'
            #                      '    <head>\n'
            #                      '        <title>Benchmark Test Page</title>\n'
            #                      '    </head>\n'
            #                      '    <body>\n'
            #                      '        <p>Paragraph 0: word0 word1 word2 word3 word4</p>\n'
            #                      '    </body>\n'
            #                      '</html>')
            # assert obj(cls.html_dict) == __(tag='html',
            #                                 attrs=__(),
            #                                 nodes=[__(tag='head',
            #                                           attrs=__(),
            #                                           nodes=[__(tag='title',
            #                                                     attrs=__(),
            #                                                     nodes=[__(type='TEXT',
            #                                                               data='Benchmark Test Page',
            #                                                               node_id='f0000004')],
            #                                                     node_id='f0000003')],
            #                                           node_id='f0000002'),
            #                                        __(tag='body',
            #                                           attrs=__(),
            #                                           nodes=[__(tag='p',
            #                                                     attrs=__(),
            #                                                     nodes=[__(type='TEXT',
            #                                                               data='Paragraph 0: word0 word1 word2 word3 '
            #                                                                    'word4',
            #                                                               node_id='f0000007')],
            #                                                     node_id='f0000006')],
            #                                           node_id='f0000005')],
            #                                 node_id='f0000001')

        # Pre-extract body_dict
        converter        = Html__To__Html_MGraph__Document__Node_Id_Reuse()
        _, cls.body_dict = converter._extract_head_body(cls.html_dict)

        # Extract nodes list for tests
        cls.nodes = cls.body_dict.get('nodes', [])

    # ═══════════════════════════════════════════════════════════════════════════
    # Benchmark Registration
    # ═══════════════════════════════════════════════════════════════════════════

    def benchmarks(self, timing: Perf_Benchmark__Timing):
        body_dict           = self.body_dict
        nodes               = self.nodes
        body_node_id        = 'f0000005'

        # Shared converter for non-mutating operations (A_01, A_02, A_03)
        html_to_html_mgraph = Html__To__Html_MGraph__Document__Node_Id_Reuse()

        # ───────────────────────────────────────────────────────────────────────
        # A_01: nodes = parent_dict.get('nodes', [])
        # ───────────────────────────────────────────────────────────────────────
        def stage_A_01__get_nodes():
            result = body_dict.get('nodes', [])
            return result

        timing.benchmark('A_01__get_nodes', stage_A_01__get_nodes)

        # ───────────────────────────────────────────────────────────────────────
        # A_02: tag_counts = self._count_tags(nodes)
        # ───────────────────────────────────────────────────────────────────────
        def stage_A_02__count_tags():
            tag_counts = html_to_html_mgraph._count_tags(nodes)
            return tag_counts

        timing.benchmark('A_02__count_tags', stage_A_02__count_tags)

        # ───────────────────────────────────────────────────────────────────────
        # A_03a: Pure loop iteration (enumerate + isinstance only)
        # ───────────────────────────────────────────────────────────────────────
        def stage_A_03a__pure_loop():
            for position, node in enumerate(nodes):
                if not isinstance(node, dict):
                    continue
                # Just iteration, no processing

        timing.benchmark('A_03a__pure_loop', stage_A_03a__pure_loop)

        # ───────────────────────────────────────────────────────────────────────
        # A_03b: Loop + _is_text_node check (difference = N × _is_text_node cost)
        # ───────────────────────────────────────────────────────────────────────
        def stage_A_03b__loop_with_is_text_node():
            for position, node in enumerate(nodes):
                if not isinstance(node, dict):
                    continue
                if html_to_html_mgraph._is_text_node(node):
                    pass  # Would call _process_body__text_node

        timing.benchmark('A_03b__loop_with_is_text_node', stage_A_03b__loop_with_is_text_node)

        # ───────────────────────────────────────────────────────────────────────
        # A_03c: Full loop overhead (with tag processing logic)
        # ───────────────────────────────────────────────────────────────────────
        def stage_A_03c__full_loop_overhead():
            tag_occurrence = {}
            for position, node in enumerate(nodes):
                if not isinstance(node, dict):
                    continue
                if html_to_html_mgraph._is_text_node(node):
                    pass  # Would call _process_body__text_node
                elif 'tag' in node:
                    tag       = node.get('tag', '').lower()
                    tag_index = tag_occurrence.get(tag, 0)
                    tag_occurrence[tag] = tag_index + 1
                    # Would call _process_body__element

        timing.benchmark('A_03c__full_loop_overhead', stage_A_03c__full_loop_overhead)

        # ───────────────────────────────────────────────────────────────────────
        # Helper: Create fresh document with body root (for A_04, A_05, A_06)
        # ───────────────────────────────────────────────────────────────────────
        def create_fresh_document_with_body():
            document = Html_MGraph__Document().setup()
            document.body_graph.create_element(node_path=Node_Path('body'), node_id=body_node_id)
            document.body_graph.set_root(body_node_id)
            document.attrs_graph.register_element(body_node_id, 'body')
            return document

        # ───────────────────────────────────────────────────────────────────────
        # A_04: _process_body__text_node for ALL text nodes at body level
        # Note: For body level, there are NO direct text children (all are <p>)
        # This measures what would happen if there were text nodes
        # ───────────────────────────────────────────────────────────────────────
        document  = create_fresh_document_with_body()
        converter = Html__To__Html_MGraph__Document__Node_Id_Reuse()
        def stage_A_04__process_all_text_nodes():
            for position, node in enumerate(nodes):
                if not isinstance(node, dict):
                    continue
                if converter._is_text_node(node):
                    raise Exception("we never get here") # we next get this exception, which confirms we have a problem with our current dataset
                    converter._process_body__text_node(document, body_node_id, node, position)

        timing.benchmark('A_04__process_all_text_nodes', stage_A_04__process_all_text_nodes)

        # ───────────────────────────────────────────────────────────────────────
        # A_05: _process_body__element for ALL elements at body level
        # Note: This is RECURSIVE - each <p> processes its TEXT child
        # This should be where most of the time goes!
        # ───────────────────────────────────────────────────────────────────────
        document       = create_fresh_document_with_body()
        converter      = Html__To__Html_MGraph__Document__Node_Id_Reuse()
        def stage_A_05__process_all_elements():
            tag_counts     = converter._count_tags(nodes)
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
                    converter._process_body__element(document, body_node_id, node,
                                                     position, tag, node_path)

        timing.benchmark('A_05__process_all_elements', stage_A_05__process_all_elements)

        # ───────────────────────────────────────────────────────────────────────
        # A_06: Full _process_body_children (all children)
        # Fresh document each iteration to measure true cost
        # ───────────────────────────────────────────────────────────────────────
        document  = create_fresh_document_with_body()
        converter = Html__To__Html_MGraph__Document__Node_Id_Reuse()

        def stage_A_06__full_process_body_children():
            converter._process_body_children(document, body_node_id, body_dict, 'body')

        timing.benchmark('A_06__full_process_body_children', stage_A_06__full_process_body_children)

    # ═══════════════════════════════════════════════════════════════════════════
    # Test Method
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test__process_body_children__line_by_line(self):
        builder = Perf_Report__Builder(metadata = Schema__Perf_Report__Metadata(title        = REPORT_TITLE                         ,
                                                                                version      = version__mgraph_ai_service_html_graph,
                                                                                description  = REPORT_DESCRIPTION                   ,
                                                                                test_input   = REPORT_TEST_INPUT                    ,
                                                                                measure_mode = Enum__Measure_Mode.FAST              ),
                                       legend   = Dict__Perf_Report__Legend(REPORT_LEGEND)                                           ,
                                       config   = self.config                                                                        )

        report = builder.run(self.benchmarks)

        self.storage.save(report, key=REPORT_KEY, formats=['txt'])

        #print(Perf_Report__Renderer__Text().render(report))