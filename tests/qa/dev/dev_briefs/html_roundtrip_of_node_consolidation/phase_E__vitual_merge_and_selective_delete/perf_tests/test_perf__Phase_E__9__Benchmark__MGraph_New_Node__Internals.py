# ═══════════════════════════════════════════════════════════════════════════════
# Performance Benchmark: MGraph new_node Internals Breakdown
# Analyzes: The internal call chain inside new_node operations
# ═══════════════════════════════════════════════════════════════════════════════
#
# "Follow the Rabbit Hole" Pattern - Level 5
#
# new_node call chain:
#   Html_MGraph__Base.new_element_node()
#     └── mgraph.edit().new_node()
#           └── MGraph__Edit.new_node()
#                 ├── with self.index() as index:      # A_01: Index context
#                 ├── self.graph.new_node(**kwargs)    # A_02: Domain layer
#                 │     └── Domain__MGraph__Graph.new_node()
#                 │           ├── self.model.new_node()  # A_03: Model/Schema creation
#                 │           └── self.mgraph_node()     # A_04: Domain wrapper
#                 └── index.add_node(node.node.data)   # A_05: Index update
#
# new_edge call chain (similar structure):
#   MGraph__Edit.new_edge()
#         ├── self.graph.new_edge(**kwargs)
#         └── self.index().add_edge(edge.edge.data)
#
# ═══════════════════════════════════════════════════════════════════════════════

import phase_e
from unittest                                                                                                   import TestCase
from mgraph_ai_service_html_graph.utils.Version                                                                 import version__mgraph_ai_service_html_graph
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids            import Html__To__Html_Dict__With__Node_Ids
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document                              import Html_MGraph__Document
from mgraph_db.mgraph.schemas.Schema__MGraph__Node                                                              import Schema__MGraph__Node
from mgraph_db.mgraph.schemas.Schema__MGraph__Edge                                                              import Schema__MGraph__Edge
from mgraph_db.mgraph.schemas.identifiers.Node_Path                                                             import Node_Path
from mgraph_db.mgraph.schemas.identifiers.Edge_Path                                                             import Edge_Path
from osbot_utils.helpers.performance.benchmark.Perf_Benchmark__Timing                                           import Perf_Benchmark__Timing
from osbot_utils.helpers.performance.benchmark.schemas.enums.Enum__Measure_Mode                                 import Enum__Measure_Mode
from osbot_utils.helpers.performance.benchmark.schemas.timing.Schema__Perf_Benchmark__Timing__Config            import Schema__Perf_Benchmark__Timing__Config
from osbot_utils.testing.Graph__Deterministic__Ids                                                              import graph_deterministic_ids
from osbot_utils.type_safe.type_safe_core.config.type_safe_fast_create                                          import type_safe_fast_create
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                                               import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id                                               import Safe_Id
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

REPORT_KEY         = 'perf_9__benchmark__mgraph_new_node__internals'
REPORT_TITLE       = 'MGraph new_node: Internals Breakdown'
REPORT_DESCRIPTION = ('Follow the Rabbit Hole Level 5: Break down the new_node call chain. '
                      'Measures index context, model creation, domain wrapper, and index update.')
REPORT_TEST_INPUT  = 'MGraph internal operations measured individually'
REPORT_LEGEND      = { 'A': 'new_node internals (single call)'  ,
                       'B': 'new_edge internals (single call)'  ,
                       'C': 'Full loop processing (all elements)' }


# ═══════════════════════════════════════════════════════════════════════════════
# Performance Test Class
# ═══════════════════════════════════════════════════════════════════════════════

class test_perf__Phase_E__9__Benchmark__MGraph_New_Node__Internals(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.storage_path = path_combine(phase_e.path, '../perf_results')
        cls.storage      = Perf_Report__Storage__File_System(storage_path=cls.storage_path)
        cls.generator    = Html_Generator__For_Benchmarks()
        cls.config       = Schema__Perf_Benchmark__Timing__Config(title            = REPORT_TITLE,
                                                                  measure_fast     = True        ,
                                                                  print_to_console = False       ,
                                                                  asserts_enabled  = False       )

        # Pre-generate test data
        with graph_deterministic_ids():
            cls.html_100     = cls.generator.generate__100  ()
            cls.html_200     = cls.generator.generate__200  ()
            cls.html_500     = cls.generator.generate__500  ()
            cls.html_1_000   = cls.generator.generate__1_000()
            cls.html         = cls.html_1_000

            cls.html_dict    = Html__To__Html_Dict__With__Node_Ids(html=cls.html).convert()

        # Pre-extract body_dict and nodes
        converter        = Html__To__Html_MGraph__Document__Node_Id_Reuse()
        _, cls.body_dict = converter._extract_head_body(cls.html_dict)
        cls.nodes        = cls.body_dict.get('nodes', [])

    # ═══════════════════════════════════════════════════════════════════════════
    # Benchmark Registration
    # ═══════════════════════════════════════════════════════════════════════════

    def benchmarks(self, timing: Perf_Benchmark__Timing):
        nodes        = self.nodes
        body_node_id = Node_Id('f0000005')

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
        # Section A: new_node internals (single call)
        # ═══════════════════════════════════════════════════════════════════════

        # ───────────────────────────────────────────────────────────────────────
        # A_01: mgraph.edit() - getting the edit object
        # ───────────────────────────────────────────────────────────────────────
        document_A_01 = create_fresh_document_with_body()
        mgraph_A_01   = document_A_01.body_graph.mgraph

        def stage_A_01__get_edit():
            edit = mgraph_A_01.edit()
            return edit

        timing.benchmark('A_01__get_edit', stage_A_01__get_edit)

        # ───────────────────────────────────────────────────────────────────────
        # A_02: edit.index() - getting/entering index context
        # ───────────────────────────────────────────────────────────────────────
        document_A_02 = create_fresh_document_with_body()
        edit_A_02     = document_A_02.body_graph.mgraph.edit()

        def stage_A_02__get_index():
            index = edit_A_02.index()
            return index

        timing.benchmark('A_02__get_index', stage_A_02__get_index)

        # ───────────────────────────────────────────────────────────────────────
        # A_03: model.new_node() - Schema creation at model layer
        # This bypasses edit layer to measure raw model/schema creation
        # ───────────────────────────────────────────────────────────────────────
        document_A_03 = create_fresh_document_with_body()
        model_A_03    = document_A_03.body_graph.mgraph.edit().graph.model

        def stage_A_03__model_new_node():
            node = model_A_03.new_node(node_type=Schema__MGraph__Node,
                                       node_path=Node_Path('body.p[0]'))
            return node

        timing.benchmark('A_03__model_new_node', stage_A_03__model_new_node)

        # ───────────────────────────────────────────────────────────────────────
        # A_04: graph.mgraph_node() - Domain wrapper creation
        # ───────────────────────────────────────────────────────────────────────
        document_A_04 = create_fresh_document_with_body()
        graph_A_04    = document_A_04.body_graph.mgraph.edit().graph
        model_A_04    = graph_A_04.model

        def stage_A_04__mgraph_node_wrapper():
            # First create a model node
            model_node = model_A_04.new_node(node_type=Schema__MGraph__Node,
                                             node_path=Node_Path('body.p[0]'))
            # Then wrap it in domain object
            domain_node = graph_A_04.mgraph_node(node=model_node)
            return domain_node

        timing.benchmark('A_04__mgraph_node_wrapper', stage_A_04__mgraph_node_wrapper)

        # Adjust A_04 to get isolated mgraph_node cost
        benchmark_a_03__result = timing.results.get('A_03__model_new_node')
        benchmark_a_04__result = timing.results.get('A_04__mgraph_node_wrapper')
        try:
            benchmark_a_04__result.final_score -= benchmark_a_03__result.final_score
            benchmark_a_04__result.raw_score   -= benchmark_a_03__result.raw_score
        except: # due to low timings we had a couple cases of E               ValueError: Safe_UInt must be >= 0, got -20000
            pass

        # ───────────────────────────────────────────────────────────────────────
        # A_05: index.add_node() - Index update
        # ───────────────────────────────────────────────────────────────────────
        document_A_05 = create_fresh_document_with_body()
        edit_A_05     = document_A_05.body_graph.mgraph.edit()
        model_A_05    = edit_A_05.graph.model
        index_A_05    = edit_A_05.index()

        def stage_A_05__index_add_node():
            # Create a node at model layer
            model_node = model_A_05.new_node(node_type=Schema__MGraph__Node,
                                             node_path=Node_Path('body.p[0]'))
            # Add to index
            index_A_05.add_node(model_node.data)

        timing.benchmark('A_05__index_add_node', stage_A_05__index_add_node)

        # Adjust A_05 to get isolated index.add_node cost
        benchmark_a_05__result = timing.results.get('A_05__index_add_node')
        benchmark_a_05__result.final_score -= benchmark_a_03__result.final_score
        benchmark_a_05__result.raw_score   -= benchmark_a_03__result.raw_score

        # ───────────────────────────────────────────────────────────────────────
        # A_06: Full new_node via edit layer (reference)
        # ───────────────────────────────────────────────────────────────────────
        document_A_06 = create_fresh_document_with_body()
        edit_A_06     = document_A_06.body_graph.mgraph.edit()

        def stage_A_06__full_edit_new_node():
            node = edit_A_06.new_node(node_type=Schema__MGraph__Node,
                                      node_path=Node_Path('body.p[0]'))
            return node

        timing.benchmark('A_06__full_edit_new_node', stage_A_06__full_edit_new_node)

        # ───────────────────────────────────────────────────────────────────────
        # A_07: Full new_element_node via Html_MGraph__Body (high-level reference)
        # ───────────────────────────────────────────────────────────────────────
        document_A_07  = create_fresh_document_with_body()
        converter_A_07 = Html__To__Html_MGraph__Document__Node_Id_Reuse()

        def stage_A_07__full_create_element():
            node_id = converter_A_07._generate_node_id()
            document_A_07.body_graph.create_element(node_path=Node_Path('body.p[0]'),
                                                     node_id=node_id)

        timing.benchmark('A_07__full_create_element', stage_A_07__full_create_element)

        # ═══════════════════════════════════════════════════════════════════════
        # Section B: new_edge internals (single call)
        # ═══════════════════════════════════════════════════════════════════════

        # ───────────────────────────────────────────────────────────────────────
        # B_01: model.new_edge() - Schema creation at model layer
        # ───────────────────────────────────────────────────────────────────────
        document_B_01 = create_fresh_document_with_body()
        model_B_01    = document_B_01.body_graph.mgraph.edit().graph.model
        # Create a child node first
        child_node_B_01 = model_B_01.new_node(node_type=Schema__MGraph__Node,
                                              node_path=Node_Path('body.p[0]'))
        child_id_B_01 = child_node_B_01.data.node_id

        def stage_B_01__model_new_edge():
            edge = model_B_01.new_edge(from_node_id=body_node_id,
                                       to_node_id=child_id_B_01,
                                       predicate=Safe_Id('child'),
                                       edge_path=Edge_Path('0'))
            return edge

        timing.benchmark('B_01__model_new_edge', stage_B_01__model_new_edge)

        # ───────────────────────────────────────────────────────────────────────
        # B_02: index.add_edge() - Index update for edge
        # ───────────────────────────────────────────────────────────────────────
        document_B_02 = create_fresh_document_with_body()
        edit_B_02     = document_B_02.body_graph.mgraph.edit()
        model_B_02    = edit_B_02.graph.model
        index_B_02    = edit_B_02.index()
        # Create a child node first
        child_node_B_02 = model_B_02.new_node(node_type=Schema__MGraph__Node,
                                              node_path=Node_Path('body.p[0]'))
        child_id_B_02 = child_node_B_02.data.node_id
        index_B_02.add_node(child_node_B_02.data)

        def stage_B_02__index_add_edge():
            # Create edge at model layer
            model_edge = model_B_02.new_edge(from_node_id=body_node_id,
                                             to_node_id=child_id_B_02,
                                             predicate=Safe_Id('child'),
                                             edge_path=Edge_Path('0'))
            # Add to index
            index_B_02.add_edge(model_edge.data)

        timing.benchmark('B_02__index_add_edge', stage_B_02__index_add_edge)

        # Adjust B_02 to get isolated index.add_edge cost
        benchmark_b_01__result = timing.results.get('B_01__model_new_edge')
        benchmark_b_02__result = timing.results.get('B_02__index_add_edge')
        benchmark_b_02__result.final_score -= benchmark_b_01__result.final_score
        benchmark_b_02__result.raw_score   -= benchmark_b_01__result.raw_score

        # ───────────────────────────────────────────────────────────────────────
        # B_03: Full new_edge via edit layer (reference)
        # ───────────────────────────────────────────────────────────────────────
        document_B_03 = create_fresh_document_with_body()
        edit_B_03     = document_B_03.body_graph.mgraph.edit()
        model_B_03    = edit_B_03.graph.model
        # Create a child node first
        child_node_B_03 = edit_B_03.new_node(node_type=Schema__MGraph__Node,
                                             node_path=Node_Path('body.p[0]'))
        child_id_B_03 = child_node_B_03.node_id

        def stage_B_03__full_edit_new_edge():
            edge = edit_B_03.new_edge(from_node_id=body_node_id,
                                      to_node_id=child_id_B_03,
                                      predicate=Safe_Id('child'),
                                      edge_path=Edge_Path('0'))
            return edge

        timing.benchmark('B_03__full_edit_new_edge', stage_B_03__full_edit_new_edge)

        # ───────────────────────────────────────────────────────────────────────
        # B_04: Full add_child via Html_MGraph__Body (high-level reference)
        # ───────────────────────────────────────────────────────────────────────
        document_B_04  = create_fresh_document_with_body()
        converter_B_04 = Html__To__Html_MGraph__Document__Node_Id_Reuse()
        # Create a child node first
        child_id_B_04 = converter_B_04._generate_node_id()
        document_B_04.body_graph.create_element(node_path=Node_Path('body.p[0]'),
                                                 node_id=child_id_B_04)

        def stage_B_04__full_add_child():
            document_B_04.body_graph.add_child(body_node_id, child_id_B_04, 0)

        timing.benchmark('B_04__full_add_child', stage_B_04__full_add_child)

        # ═══════════════════════════════════════════════════════════════════════
        # Section C: Full loop processing (all elements) - Reference
        # ═══════════════════════════════════════════════════════════════════════

        # ───────────────────────────────────────────────────────────────────────
        # C_01: model.new_node() for ALL elements (bypass edit layer)
        # ───────────────────────────────────────────────────────────────────────
        document_C_01 = create_fresh_document_with_body()
        model_C_01    = document_C_01.body_graph.mgraph.edit().graph.model
        converter_C_01 = Html__To__Html_MGraph__Document__Node_Id_Reuse()

        def stage_C_01__model_new_node_all():
            tag_counts     = converter_C_01._count_tags(nodes)
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
                    model_C_01.new_node(node_type=Schema__MGraph__Node,
                                        node_path=Node_Path(node_path))

        timing.benchmark('C_01__model_new_node_all', stage_C_01__model_new_node_all)

        # ───────────────────────────────────────────────────────────────────────
        # C_02: Full create_element for ALL (reference from perf_8)
        # ───────────────────────────────────────────────────────────────────────
        document_C_02  = create_fresh_document_with_body()
        converter_C_02 = Html__To__Html_MGraph__Document__Node_Id_Reuse()

        def stage_C_02__full_create_element_all():
            tag_counts     = converter_C_02._count_tags(nodes)
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
                    node_id = converter_C_02._generate_node_id()
                    document_C_02.body_graph.create_element(node_path=Node_Path(node_path),
                                                            node_id=node_id)

        timing.benchmark('C_02__full_create_element_all', stage_C_02__full_create_element_all)

    # ═══════════════════════════════════════════════════════════════════════════
    # Test Method
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test__mgraph_new_node__internals(self):
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