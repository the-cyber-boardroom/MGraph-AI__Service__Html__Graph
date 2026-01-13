# ═══════════════════════════════════════════════════════════════════════════════
# Performance Benchmark: Phase E_6 - Cache Hit vs Miss
# Analyzes: Cache save operations vs cache load operations
# ═══════════════════════════════════════════════════════════════════════════════
#
# Phase E_6 Test 3: Quantify cache performance benefit
#
# Cache operations measured:
#   Save (Miss): Create entry, save L1 (HTML), save L2 (dict), save L3 (MGraph)
#   Load (Hit):  Load L1, load L2, load L3 from cache
#
# Uses in-memory cache service for reproducible results.
# Uses actual layer classes for realistic measurements.
#
# SECTIONS:
#   A_xx - Cache save operations (cache miss scenario)
#   B_xx - Cache load operations (cache hit scenario)
#   C_xx - Full pipeline comparisons
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
from phase_e.html_cache.Html_Cache__Layer__Html                                                             import Html_Cache__Layer__Html
from phase_e.html_cache.Html_Cache__Layer__Html__Dict                                                       import Html_Cache__Layer__Html__Dict
from phase_e.html_cache.Html_Cache__Layer__MGraph                                                           import Html_Cache__Layer__MGraph
from phase_e.html_cache.Html_Cache__Manager                                                                 import Html_Cache__Manager
from phase_e.html_cache.schemas.Schema__Html_Cache                                                          import Schema__Html_Cache__Config, Schema__Html_Cache__Stats
from phase_e.performance.Html_Generator__For_Benchmarks                                                     import Html_Generator__For_Benchmarks
from phase_e.report.builder.Perf_Report__Builder                                                            import Perf_Report__Builder
from phase_e.report.collections.Dict__Perf_Report__Legend                                                   import Dict__Perf_Report__Legend
from phase_e.report.renderers.Perf_Report__Renderer__Text                                                   import Perf_Report__Renderer__Text
from phase_e.report.schemas.Schema__Perf_Report__Metadata                                                   import Schema__Perf_Report__Metadata
from phase_e.report.storage.Perf_Report__Storage__File_System                                               import Perf_Report__Storage__File_System
from phase_e.storage.backends.Perf__Storage__Cache_Service                                                  import Perf__Storage__Cache_Service
from phase_e.storage.cache_service.Cache_Service__Client                                                    import Cache_Service__Client
from phase_e.storage.enums.Enum__Storage_Mode                                                               import Enum__Storage_Mode
from phase_e.storage.schemas.Schema__Perf__Storage__Config                                                  import Schema__Perf__Storage__Config
from tests.Phase_E__Fast_API__Test_Objs                                                                     import client_cache_service

# ═══════════════════════════════════════════════════════════════════════════════
# Report Metadata
# ═══════════════════════════════════════════════════════════════════════════════

REPORT_KEY         = 'perf_6_3__cache_hit_miss__10_nodes'
REPORT_TITLE       = 'Phase E_6: Cache Hit vs Miss'
REPORT_DESCRIPTION = ('Compares cache save (miss) vs cache load (hit) performance. '
                      'Measures create entry, save L1/L2/L3, and load L1/L2/L3 operations. '
                      'Uses actual layer classes with in-memory cache service.')
REPORT_TEST_INPUT  = 'Synthetic HTML with 10 paragraphs (~30 nodes)'
REPORT_LEGEND      = {'A': 'Cache save (miss)  = First request - create and store data'  ,
                      'B': 'Cache load (hit)   = Subsequent request - retrieve from cache',
                      'C': 'Full pipeline      = Complete save/load cycles'              }


# ═══════════════════════════════════════════════════════════════════════════════
# Performance Test Class
# ═══════════════════════════════════════════════════════════════════════════════

class test_perf__Phase_E_6__3__Cache_Hit_Miss(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.storage_path    = path_combine(phase_e.path, '../perf_results')
        cls.report_storage  = Perf_Report__Storage__File_System(storage_path=cls.storage_path)
        cls.generator       = Html_Generator__For_Benchmarks()
        cls.config          = Schema__Perf_Benchmark__Timing__Config(title            = REPORT_TITLE,
                                                                     measure_fast     = True        ,
                                                                     print_to_console = False       ,
                                                                     asserts_enabled  = False       )

        # ───────────────────────────────────────────────────────────────────────
        # Set up cache service and storage
        # ───────────────────────────────────────────────────────────────────────
        cls.cache_client, cls.cache_service = client_cache_service()
        cls.cache_client_wrapper            = Cache_Service__Client(cache_client=cls.cache_client)

        cls.cache_namespace = 'pytest-perf-e6-3'
        cls.storage_config  = Schema__Perf__Storage__Config(storage_mode    = Enum__Storage_Mode.CACHE_SERVICE,
                                                            cache_namespace = cls.cache_namespace)

        # ───────────────────────────────────────────────────────────────────────
        # Pre-generate test HTML
        # ───────────────────────────────────────────────────────────────────────
        cls.html_1   = cls.generator.generate__1()
        cls.html_10  = cls.generator.generate__10()
        cls.html_50  = cls.generator.generate__10()
        cls.html_100 = cls.generator.generate__100()
        cls.html     = cls.html_10


        # ───────────────────────────────────────────────────────────────────────
        # Pre-compute pipeline data (outside measurement)
        # ───────────────────────────────────────────────────────────────────────
        with graph_deterministic_ids():
            cls.html_str   = cls.html
            cls.html_dict  = Html__To__Html_Dict__With__Node_Ids(html=cls.html_str).convert()
            cls.mgraph_doc = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(cls.html_dict)

        # ───────────────────────────────────────────────────────────────────────
        # Pre-populate cache for load benchmarks
        # ───────────────────────────────────────────────────────────────────────
        cls.prepopulated_cache_id = cls.prepopulate_cache()

    @classmethod
    def create_storage(cls, session_name: str, target_name: str) -> Perf__Storage__Cache_Service:
        """Create a fresh storage instance for benchmarks."""
        return Perf__Storage__Cache_Service(config       = cls.storage_config      ,
                                            client       = cls.cache_client_wrapper,
                                            session_name = session_name            ,
                                            target_name  = target_name             )

    @classmethod
    def create_layers(cls, storage: Perf__Storage__Cache_Service) -> tuple:
        """Create layer instances sharing storage and stats."""
        stats        = Schema__Html_Cache__Stats()
        layer_html   = Html_Cache__Layer__Html      (storage=storage, stats=stats)
        layer_dict   = Html_Cache__Layer__Html__Dict(storage=storage, stats=stats)
        layer_mgraph = Html_Cache__Layer__MGraph    (storage=storage, stats=stats)
        return layer_html, layer_dict, layer_mgraph, stats

    @classmethod
    def prepopulate_cache(cls) -> str:
        """Create cache entry with data for load tests using actual layers."""
        storage = cls.create_storage(session_name='perf-test-prepop',
                                     target_name='load-benchmark')
        cache_id = storage.create_file__perf_entry()

        layer_html, layer_dict, layer_mgraph, _ = cls.create_layers(storage)

        # Save all layers using actual layer methods
        layer_html.save  (cache_id=cache_id, html=cls.html_str, source='benchmark')
        layer_dict.save  (cache_id=cache_id, html_dict=cls.html_dict              )
        layer_mgraph.save(cache_id=cache_id, document=cls.mgraph_doc              )

        # Store references for load benchmarks
        cls.prepop_storage      = storage
        cls.prepop_layer_html   = layer_html
        cls.prepop_layer_dict   = layer_dict
        cls.prepop_layer_mgraph = layer_mgraph

        cache_id_base_path  = 'pytest-perf-e6-3/data/key-based/sessions/perf-test-prepop/targets/load-benchmark/perf-entry'
        cache_id__sharded   = f"{cache_id[0:2]}/{cache_id[2:4]}/{cache_id}"

        assert cache_id_base_path             == f'{cls.cache_namespace}/data/key-based/sessions/{storage.session_name}/targets/{storage.target_name}/{storage.file_id}'
        assert storage.namespace__all_files() == [f'{cache_id_base_path}.json',
                                                  f'{cache_id_base_path}.json.config',
                                                  f'{cache_id_base_path}.json.metadata',

                                                  f'{cache_id_base_path}/data/L1/metadata.json',
                                                  f'{cache_id_base_path}/data/L1/raw-html.txt',
                                                  f'{cache_id_base_path}/data/L2/html-dict.json',
                                                  f'{cache_id_base_path}/data/L3/metadata.json',
                                                  f'{cache_id_base_path}/data/L3/mgraph-document.json',
                                                   'pytest-perf-e6-3/refs/by-hash/d0/dd/d0ddec7e78c802c9.json',
                                                  f'pytest-perf-e6-3/refs/by-id/{cache_id__sharded}.json']


        return cache_id

    # ═══════════════════════════════════════════════════════════════════════════
    # Benchmark Registration
    # ═══════════════════════════════════════════════════════════════════════════

    def benchmarks(self, timing: Perf_Benchmark__Timing):

        # References for benchmarks
        html_str          = self.html_str
        html_dict         = self.html_dict
        mgraph_doc        = self.mgraph_doc
        prepopulated_id   = self.prepopulated_cache_id
        prepop_layer_html  = self.prepop_layer_html
        prepop_layer_dict  = self.prepop_layer_dict
        prepop_layer_mgraph = self.prepop_layer_mgraph

        # Counter for unique target names (avoids cache key collisions)
        benchmark_counter = [0]

        def next_target():
            benchmark_counter[0] += 1
            return f'bench-target-{benchmark_counter[0]}'

        # ───────────────────────────────────────────────────────────────────────
        # Section A: Cache Save Operations (Cache Miss)
        # ───────────────────────────────────────────────────────────────────────

        # A_01: Create cache entry (storage setup + entry creation)
        def stage_A_01__create_entry():
            storage  = self.create_storage(session_name='perf-a01', target_name=next_target())
            cache_id = storage.create_file__perf_entry()
            return cache_id

        timing.benchmark('A_01__create_entry', stage_A_01__create_entry)

        # A_02: Save L1 (raw HTML string via layer)
        storage_a02  = self.create_storage(session_name='perf-a02', target_name='save-l1')
        cache_id_a02 = storage_a02.create_file__perf_entry()
        layer_html_a02, _, _, _ = self.create_layers(storage_a02)

        def stage_A_02__save_L1():
            return layer_html_a02.save(cache_id=cache_id_a02, html=html_str, source='benchmark')

        timing.benchmark('A_02__save_L1__raw_html', stage_A_02__save_L1)

        # A_03: Save L2 (html_dict via layer)
        storage_a03  = self.create_storage(session_name='perf-a03', target_name='save-l2')
        cache_id_a03 = storage_a03.create_file__perf_entry()
        _, layer_dict_a03, _, _ = self.create_layers(storage_a03)

        def stage_A_03__save_L2():
            return layer_dict_a03.save(cache_id=cache_id_a03, html_dict=html_dict)

        timing.benchmark('A_03__save_L2__html_dict', stage_A_03__save_L2)

        # A_04: Save L3 (MGraph document via layer)
        storage_a04  = self.create_storage(session_name='perf-a04', target_name='save-l3')
        cache_id_a04 = storage_a04.create_file__perf_entry()
        _, _, layer_mgraph_a04, _ = self.create_layers(storage_a04)

        def stage_A_04__save_L3():
            return layer_mgraph_a04.save(cache_id=cache_id_a04, document=mgraph_doc)

        timing.benchmark('A_04__save_L3__mgraph', stage_A_04__save_L3)

        # A_05: Full save pipeline (create + save all layers)
        def stage_A_05__full_save_pipeline():
            target  = next_target()
            storage = self.create_storage(session_name='perf-a05', target_name=target)
            cache_id = storage.create_file__perf_entry()
            layer_html, layer_dict, layer_mgraph, _ = self.create_layers(storage)

            layer_html.save(cache_id=cache_id, html=html_str, source='benchmark')
            layer_dict.save(cache_id=cache_id, html_dict=html_dict)
            layer_mgraph.save(cache_id=cache_id, document=mgraph_doc)
            return cache_id

        timing.benchmark('A_05__full_save_pipeline', stage_A_05__full_save_pipeline)

        # ───────────────────────────────────────────────────────────────────────
        # Section B: Cache Load Operations (Cache Hit)
        # ───────────────────────────────────────────────────────────────────────

        # B_01: Load L1 (raw HTML from cache)
        def stage_B_01__load_L1():
            return prepop_layer_html.load(cache_id=prepopulated_id)

        timing.benchmark('B_01__load_L1__raw_html', stage_B_01__load_L1)

        # B_02: Load L2 (html_dict from cache)
        def stage_B_02__load_L2():
            return prepop_layer_dict.load(cache_id=prepopulated_id)

        timing.benchmark('B_02__load_L2__html_dict', stage_B_02__load_L2)

        # B_03: Load L3 (MGraph document from cache - includes deserialization)
        def stage_B_03__load_L3():
            return prepop_layer_mgraph.load(cache_id=prepopulated_id)

        timing.benchmark('B_03__load_L3__mgraph', stage_B_03__load_L3)

        # B_04: Full load pipeline (load all layers)
        def stage_B_04__full_load_pipeline():
            l1 = prepop_layer_html.load(cache_id=prepopulated_id)
            l2 = prepop_layer_dict.load(cache_id=prepopulated_id)
            l3 = prepop_layer_mgraph.load(cache_id=prepopulated_id)
            return (l1, l2, l3)

        timing.benchmark('B_04__full_load_pipeline', stage_B_04__full_load_pipeline)

        # ───────────────────────────────────────────────────────────────────────
        # Section C: Full Pipeline Comparisons (using Html_Cache__Manager)
        # ───────────────────────────────────────────────────────────────────────

        # C_01: Full cache miss via manager (save HTML + build full pipeline)
        def stage_C_01__manager_full_miss():
            target  = next_target()
            storage = self.create_storage(session_name='perf-c01', target_name=target)
            manager = Html_Cache__Manager(storage=storage).setup()
            document = manager.build_full_pipeline(target=target, html=html_str, source='benchmark')
            return document

        timing.benchmark('C_01__manager__full_cache_miss', stage_C_01__manager_full_miss)

        # C_02: Cache hit via manager (get_mgraph from pre-populated cache)
        storage_c02 = self.prepop_storage
        manager_c02 = Html_Cache__Manager(storage=storage_c02).setup()

        def stage_C_02__manager_cache_hit():
            # Target was 'load-benchmark' from prepopulate
            return manager_c02.get_mgraph(target='load-benchmark', build_if_missing=False)

        timing.benchmark('C_02__manager__cache_hit', stage_C_02__manager_cache_hit)

    # ═══════════════════════════════════════════════════════════════════════════
    # Test Method
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test__cache_hit_miss(self):
        builder = Perf_Report__Builder(metadata = Schema__Perf_Report__Metadata(title        = REPORT_TITLE                         ,
                                                                                version      = version__mgraph_ai_service_html_graph,
                                                                                description  = REPORT_DESCRIPTION                   ,
                                                                                test_input   = REPORT_TEST_INPUT                    ,
                                                                                measure_mode = Enum__Measure_Mode.FAST              ),
                                       legend   = Dict__Perf_Report__Legend(REPORT_LEGEND)                                           ,
                                       config   = self.config                                                                        )

        report = builder.run(self.benchmarks)

        # Save report
        self.report_storage.save(report, key=REPORT_KEY, formats=['txt'])

        # Validate structure
        assert report.metadata.benchmark_count == 11                            # A_01-A_05, B_01-B_04, C_01-C_02
        assert len(report.benchmarks)          == 11
        assert len(report.categories)          == 3                             # A, B, and C sections

        # Print report to console
        #print(Perf_Report__Renderer__Text().render(report))