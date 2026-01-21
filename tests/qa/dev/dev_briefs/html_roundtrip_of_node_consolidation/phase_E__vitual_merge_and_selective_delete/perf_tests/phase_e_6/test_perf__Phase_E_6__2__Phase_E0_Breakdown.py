# ═══════════════════════════════════════════════════════════════════════════════
# Performance Benchmark: Phase E_6 - Phase E_0 Filtered Breakdown
# Analyzes: transform__phase_e0_filtered (L5/c) component costs
# ═══════════════════════════════════════════════════════════════════════════════
#
# Phase E_6 Test 2: Break down L5/c (Phase E_0 filtering) into components
#
# transform__phase_e0_filtered pipeline:
#   1. Html__To__Html_MGraph__Document__Node_Id_Reuse.convert_from_dict()  - Fresh MGraph
#   2. Phase_E__Text_Extractor.extract()                                   - Extract text nodes
#   3. Phase_E__Virtual_Merger.merge()                                     - Merge text per parent
#   4. Phase_E__Decision_Engine__Hash_Based.classify_all()                 - Classify keep/delete
#   5. Phase_E__Node_Deleter.delete()                                      - Delete unwanted nodes
#   6. Html_MGraph__Document__To__Html__With_Original_Head.convert()       - Reconstruct HTML
#
# SECTIONS:
#   A_xx - Individual component isolation (100 nodes)
#   B_xx - Full transform reference
#
# ═══════════════════════════════════════════════════════════════════════════════

import phase_e
from unittest                                                                                                   import TestCase
from mgraph_ai_service_html_graph.utils.Version                                                                 import version__mgraph_ai_service_html_graph
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids            import Html__To__Html_Dict__With__Node_Ids
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse
from osbot_utils.helpers.performance.benchmark.Perf_Benchmark__Timing                                           import Perf_Benchmark__Timing
from osbot_utils.helpers.performance.benchmark.schemas.enums.Enum__Measure_Mode                                 import Enum__Measure_Mode
from osbot_utils.helpers.performance.benchmark.schemas.timing.Schema__Perf_Benchmark__Timing__Config            import Schema__Perf_Benchmark__Timing__Config
from osbot_utils.testing.Graph__Deterministic__Ids                                                              import graph_deterministic_ids
from osbot_utils.type_safe.type_safe_core.config.type_safe_fast_create                                          import type_safe_fast_create
from osbot_utils.utils.Files                                                                                    import path_combine
from phase_e.core.Phase_E__Text_Extractor                                                                       import Phase_E__Text_Extractor
from phase_e.core.Phase_E__Virtual_Merger                                                                       import Phase_E__Virtual_Merger
from phase_e.core.Phase_E__Node_Deleter                                                                         import Phase_E__Node_Deleter
from phase_e.decision.Phase_E__Decision_Engine__Hash_Based                                                      import Phase_E__Decision_Engine__Hash_Based
from phase_e.mgraph.Html_MGraph__Document__To__Html__With_Original_Head                                         import Html_MGraph__Document__To__Html__With_Original_Head
from osbot_utils.helpers.performance.report.Perf_Report__Builder                                                import Perf_Report__Builder
from osbot_utils.helpers.performance.testing.Html_Generator__For_Benchmarks                                     import Html_Generator__For_Benchmarks
from osbot_utils.helpers.performance.report.schemas.Schema__Perf_Report__Metadata                               import Schema__Perf_Report__Metadata
from osbot_utils.helpers.performance.report.schemas.collections.Dict__Perf_Report__Legend                       import Dict__Perf_Report__Legend
from osbot_utils.helpers.performance.report.storage.Perf_Report__Storage__File_System                           import Perf_Report__Storage__File_System


# ═══════════════════════════════════════════════════════════════════════════════
# Report Metadata
# ═══════════════════════════════════════════════════════════════════════════════

REPORT_KEY         = 'perf_6_2__phase_e0_breakdown__100_nodes'
REPORT_TITLE       = 'Phase E_6: Phase E_0 Filtered Breakdown'
REPORT_DESCRIPTION = ('Breaks down transform__phase_e0_filtered (L5/c) into component costs. '
                      'Measures MGraph creation, text extraction, virtual merge, classification, '
                      'node deletion, and HTML reconstruction.')
REPORT_TEST_INPUT  = 'Synthetic HTML with 100 paragraphs (~300 nodes)'
REPORT_LEGEND      = {'A': 'Component isolation  = Each Phase E_0 step measured independently',
                      'B': 'Full transform       = Complete transform__phase_e0_filtered'    }


# ═══════════════════════════════════════════════════════════════════════════════
# State Factory - Creates exact state at each Phase E_0 stage
# ═══════════════════════════════════════════════════════════════════════════════

class Phase_E0__State_Factory:                                                  # Creates state at each filtering stage

    def __init__(self, html: str):
        self.html      = html
        self.html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()

    def state_for_stage_1(self) -> dict:                                        # Before MGraph creation
        return {'html_dict': self.html_dict}

    def state_for_stage_2(self) -> dict:                                        # After MGraph creation, before extraction
        document = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(self.html_dict)
        return {'html_dict': self.html_dict,
                'document' : document      }

    def state_for_stage_3(self) -> dict:                                        # After extraction, before merge
        document   = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(self.html_dict)
        extractor  = Phase_E__Text_Extractor()
        text_nodes = extractor.extract(document)
        return {'html_dict' : self.html_dict,
                'document'  : document      ,
                'text_nodes': text_nodes    }

    def state_for_stage_4(self) -> dict:                                        # After merge, before classify
        document     = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(self.html_dict)
        extractor    = Phase_E__Text_Extractor()
        text_nodes   = extractor.extract(document)
        merger       = Phase_E__Virtual_Merger()
        merged_texts = merger.merge(text_nodes, document)
        return {'html_dict'   : self.html_dict,
                'document'    : document      ,
                'merged_texts': merged_texts  }

    def state_for_stage_5(self) -> dict:                                        # After classify, before delete
        document          = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(self.html_dict)
        extractor         = Phase_E__Text_Extractor()
        text_nodes        = extractor.extract(document)
        merger            = Phase_E__Virtual_Merger()
        merged_texts      = merger.merge(text_nodes, document)
        decision_engine   = Phase_E__Decision_Engine__Hash_Based(threshold=0.5)
        decisions         = decision_engine.classify_all(merged_texts)
        parents_to_delete = decision_engine.get_parents_to_delete(decisions)
        return {'html_dict'        : self.html_dict      ,
                'document'         : document            ,
                'parents_to_delete': parents_to_delete   }

    def state_for_stage_6(self) -> dict:                                        # After delete, before reconstruct
        document          = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(self.html_dict)
        extractor         = Phase_E__Text_Extractor()
        text_nodes        = extractor.extract(document)
        merger            = Phase_E__Virtual_Merger()
        merged_texts      = merger.merge(text_nodes, document)
        decision_engine   = Phase_E__Decision_Engine__Hash_Based(threshold=0.5)
        decisions         = decision_engine.classify_all(merged_texts)
        parents_to_delete = decision_engine.get_parents_to_delete(decisions)
        deleter           = Phase_E__Node_Deleter()
        deleter.delete(document, parents_to_delete)
        return {'html_dict': self.html_dict,
                'document' : document      }                                    # Document now modified


# ═══════════════════════════════════════════════════════════════════════════════
# Full Transform Function (matches production code)
# ═══════════════════════════════════════════════════════════════════════════════

def transform__phase_e0_filtered(html_dict: dict, threshold: float = 0.5) -> str:
    converter              = Html__To__Html_MGraph__Document__Node_Id_Reuse()
    document_for_filtering = converter.convert_from_dict(html_dict)

    extractor  = Phase_E__Text_Extractor()
    text_nodes = extractor.extract(document_for_filtering)

    if not text_nodes:
        patched_converter = Html_MGraph__Document__To__Html__With_Original_Head(original_html_dict=html_dict)
        return patched_converter.convert(document_for_filtering)

    merger       = Phase_E__Virtual_Merger()
    merged_texts = merger.merge(text_nodes, document_for_filtering)

    decision_engine   = Phase_E__Decision_Engine__Hash_Based(threshold=threshold)
    decisions         = decision_engine.classify_all(merged_texts)
    parents_to_delete = decision_engine.get_parents_to_delete(decisions)

    deleter = Phase_E__Node_Deleter()
    deleter.delete(document_for_filtering, parents_to_delete)

    patched_converter = Html_MGraph__Document__To__Html__With_Original_Head(original_html_dict=html_dict)
    return patched_converter.convert(document_for_filtering)


# ═══════════════════════════════════════════════════════════════════════════════
# Performance Test Class
# ═══════════════════════════════════════════════════════════════════════════════

class test_perf__Phase_E_6__2__Phase_E0_Breakdown(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.storage_path = path_combine(phase_e.path, '../perf_results')
        cls.storage      = Perf_Report__Storage__File_System(storage_path=cls.storage_path)
        cls.generator    = Html_Generator__For_Benchmarks()
        cls.config       = Schema__Perf_Benchmark__Timing__Config(title            = REPORT_TITLE,
                                                                  measure_fast     = True        ,
                                                                  print_to_console = False       ,
                                                                  asserts_enabled  = False       )

        # Pre-generate test HTML with deterministic IDs
        with graph_deterministic_ids():
            cls.html_100 = cls.generator.generate__100()

        # Create state factory for stage isolation
        cls.state_factory = Phase_E0__State_Factory(cls.html_100)

        # Pre-compute states for benchmarks (outside measurement)
        with graph_deterministic_ids():
            cls.state_1 = cls.state_factory.state_for_stage_1()
            cls.state_2 = cls.state_factory.state_for_stage_2()
            cls.state_3 = cls.state_factory.state_for_stage_3()
            cls.state_4 = cls.state_factory.state_for_stage_4()
            cls.state_5 = cls.state_factory.state_for_stage_5()
            cls.state_6 = cls.state_factory.state_for_stage_6()

    # ═══════════════════════════════════════════════════════════════════════════
    # Benchmark Registration
    # ═══════════════════════════════════════════════════════════════════════════

    def benchmarks(self, timing: Perf_Benchmark__Timing):

        html_dict         = self.state_1['html_dict']
        document_2        = self.state_2['document']
        text_nodes_3      = self.state_3['text_nodes']
        document_3        = self.state_3['document']
        merged_texts_4    = self.state_4['merged_texts']
        parents_to_delete = self.state_5['parents_to_delete']
        document_6        = self.state_6['document']

        # ───────────────────────────────────────────────────────────────────────
        # Section A: Component Isolation
        # ───────────────────────────────────────────────────────────────────────

        # A_01: Fresh MGraph creation (Dict → MGraph)
        def stage_A_01__mgraph_creation():
            return Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)

        timing.benchmark('A_01__mgraph_creation', stage_A_01__mgraph_creation)

        # A_02: Text extraction
        extractor = Phase_E__Text_Extractor()

        def stage_A_02__text_extraction():
            return extractor.extract(document_2)

        timing.benchmark('A_02__text_extraction', stage_A_02__text_extraction)

        # A_03: Virtual merge
        merger = Phase_E__Virtual_Merger()

        def stage_A_03__virtual_merge():
            return merger.merge(text_nodes_3, document_3)

        timing.benchmark('A_03__virtual_merge', stage_A_03__virtual_merge)

        # A_04: Classification
        decision_engine = Phase_E__Decision_Engine__Hash_Based(threshold=0.5)

        def stage_A_04__classification():
            decisions = decision_engine.classify_all(merged_texts_4)
            return decision_engine.get_parents_to_delete(decisions)

        timing.benchmark('A_04__classification', stage_A_04__classification)

        # A_05: Node deletion
        deleter = Phase_E__Node_Deleter()

        def stage_A_05__node_deletion():                                        # Need fresh document each time
            fresh_document    = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)
            fresh_extractor   = Phase_E__Text_Extractor()
            fresh_text_nodes  = fresh_extractor.extract(fresh_document)
            fresh_merger      = Phase_E__Virtual_Merger()
            fresh_merged      = fresh_merger.merge(fresh_text_nodes, fresh_document)
            fresh_engine      = Phase_E__Decision_Engine__Hash_Based(threshold=0.5)
            fresh_decisions   = fresh_engine.classify_all(fresh_merged)
            fresh_to_delete   = fresh_engine.get_parents_to_delete(fresh_decisions)
            deleter.delete(fresh_document, fresh_to_delete)
            return fresh_document

        timing.benchmark('A_05__node_deletion__cumulative', stage_A_05__node_deletion)

        # Adjust A_05 to get isolated deletion cost
        benchmark_a_01 = timing.results.get('A_01__mgraph_creation')
        benchmark_a_02 = timing.results.get('A_02__text_extraction')
        benchmark_a_03 = timing.results.get('A_03__virtual_merge')
        benchmark_a_04 = timing.results.get('A_04__classification')
        benchmark_a_05 = timing.results.get('A_05__node_deletion__cumulative')

        prior_stages_cost          = (benchmark_a_01.final_score + benchmark_a_02.final_score +
                                      benchmark_a_03.final_score + benchmark_a_04.final_score)
        benchmark_a_05.final_score = benchmark_a_05.final_score - prior_stages_cost
        benchmark_a_05.raw_score   = benchmark_a_05.raw_score - prior_stages_cost

        # A_06: HTML reconstruction
        converter_L3 = Html_MGraph__Document__To__Html__With_Original_Head(original_html_dict=html_dict)

        def stage_A_06__html_reconstruction():
            return converter_L3.convert(document_6)

        timing.benchmark('A_06__html_reconstruction', stage_A_06__html_reconstruction)

        # ───────────────────────────────────────────────────────────────────────
        # Section B: Full Transform Reference
        # ───────────────────────────────────────────────────────────────────────

        # B_01: Full transform__phase_e0_filtered (should ≈ sum of A_01 through A_06)
        def stage_B_01__full_transform():
            return transform__phase_e0_filtered(html_dict, threshold=0.5)

        timing.benchmark('B_01__full_transform__phase_e0_filtered', stage_B_01__full_transform)

    # ═══════════════════════════════════════════════════════════════════════════
    # Test Method
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test__phase_e0__breakdown(self):
        builder = Perf_Report__Builder(metadata = Schema__Perf_Report__Metadata(title        = REPORT_TITLE                         ,
                                                                                version      = version__mgraph_ai_service_html_graph,
                                                                                description  = REPORT_DESCRIPTION                   ,
                                                                                test_input   = REPORT_TEST_INPUT                    ,
                                                                                measure_mode = Enum__Measure_Mode.FAST              ),
                                       legend   = Dict__Perf_Report__Legend(REPORT_LEGEND)                                           ,
                                       config   = self.config                                                                        )

        report = builder.run(self.benchmarks)

        # Save report (txt only for now)
        self.storage.save(report, key=REPORT_KEY, formats=['txt'])

        # Validate structure
        assert report.metadata.benchmark_count == 7                             # A_01 through A_06, B_01
        assert len(report.benchmarks)          == 7
        assert len(report.categories)          == 2                             # A and B sections

        # Print report to console
        #print(Perf_Report__Renderer__Text().render(report))