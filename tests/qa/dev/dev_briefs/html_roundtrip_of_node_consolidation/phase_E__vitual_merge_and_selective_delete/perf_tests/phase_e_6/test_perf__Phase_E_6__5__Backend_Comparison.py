# ═══════════════════════════════════════════════════════════════════════════════
# Performance Benchmark: Phase E_6 - Backend Comparison
# Analyzes: Cache performance across different backends
# ═══════════════════════════════════════════════════════════════════════════════
#
# Phase E_6 Test 5: Compare cache backend performance
#
# Backends tested:
#   A: In-memory full pipelines  - FastAPI TestClient (save/load)
#   B: In-memory breakdown       - Isolate individual costs
#   C: Local server              - http://localhost:10017
#   D: Live server               - https://cache.dev.mgraph.ai/
#
# SECTIONS:
#   A_xx - In-memory full pipelines (baseline)
#   B_xx - In-memory cost breakdown (setup, layers, pure saves/loads)
#   C_xx - Local server (network overhead, localhost)
#   D_xx - Live serverless (real-world latency)
#
# ═══════════════════════════════════════════════════════════════════════════════

import pytest
import phase_e
from unittest                                                                                               import TestCase
from mgraph_ai_service_cache_client.client.Client__Cache__Service                                           import Client__Cache__Service
from mgraph_ai_service_html_graph.utils.Version                                                             import version__mgraph_ai_service_html_graph
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids        import Html__To__Html_Dict__With__Node_Ids
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse
from osbot_utils.helpers.performance.benchmark.Perf_Benchmark__Timing                                       import Perf_Benchmark__Timing
from osbot_utils.helpers.performance.benchmark.schemas.enums.Enum__Measure_Mode                             import Enum__Measure_Mode
from osbot_utils.helpers.performance.benchmark.schemas.timing.Schema__Perf_Benchmark__Timing__Config        import Schema__Perf_Benchmark__Timing__Config
from osbot_utils.testing.Graph__Deterministic__Ids                                                          import graph_deterministic_ids
from osbot_utils.testing.Temp_Env_Vars                                                                      import Temp_Env_Vars
from osbot_utils.type_safe.type_safe_core.config.type_safe_fast_create                                      import type_safe_fast_create
from osbot_utils.utils.Env                                                                                  import get_env, load_dotenv
from osbot_utils.utils.Files                                                                                import path_combine, file_exists
from phase_e.html_cache.Html_Cache__Layer__Html                                                             import Html_Cache__Layer__Html
from phase_e.html_cache.Html_Cache__Layer__Html__Dict                                                       import Html_Cache__Layer__Html__Dict
from phase_e.html_cache.Html_Cache__Layer__MGraph                                                           import Html_Cache__Layer__MGraph
from phase_e.html_cache.schemas.Schema__Html_Cache                                                          import Schema__Html_Cache__Stats
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
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

ENV_VAR__URL__CACHE_SERVICE  = 'URL__TARGET_SERVER__CACHE_SERVICE'
URL__LOCAL_SERVER            = 'http://127.0.0.1:10017'
URL__LIVE_SERVER             = 'https://cache.dev.mgraph.ai/'

REPORT_KEY         = 'perf_6_5__backend_comparison__50_nodes'
REPORT_TITLE       = 'Phase E_6: Backend Comparison'
REPORT_DESCRIPTION = ('Compares cache performance across backends: in-memory, local server, and live serverless. '
                      'Measures full save and load pipelines at each backend, plus cost breakdown.')
REPORT_TEST_INPUT  = 'Synthetic HTML with 50 paragraphs (~150 nodes)'
REPORT_LEGEND      = {'A': 'In-memory pipelines  = Full save/load via TestClient'        ,
                      'B': 'In-memory breakdown  = Isolate setup, layers, pure ops'      ,
                      'C': 'Local server         = http://localhost:10017'               ,
                      'D': 'Live serverless      = https://cache.dev.mgraph.ai/'         }


# ═══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════════

def load_env_vars__cache_service():                                             # Load cache service credentials from env file
    env_var_file_name = '.cache_service.env'
    env_var_file      = path_combine(__file__, f'../{env_var_file_name}')
    load_dotenv(dotenv_path=env_var_file, override=True)
    url_cache_service = get_env(ENV_VAR__URL__CACHE_SERVICE)

    assert file_exists(env_var_file), f"Env file not found: {env_var_file}"
    assert url_cache_service is not None, f"Env var {ENV_VAR__URL__CACHE_SERVICE} not set"

    return url_cache_service


def is_local_server_available():                                                # Check if local cache server is running
    try:
        load_env_vars__cache_service()
        with Temp_Env_Vars(env_vars={ENV_VAR__URL__CACHE_SERVICE: URL__LOCAL_SERVER}):
            client = Client__Cache__Service().client()
            result = client.info().health()
            return result and result.get('status') == 'ok'
    except Exception as error:
        print(error)
        return False


def is_live_server_available():                                                 # Check if live cache server is accessible
    try:
        load_env_vars__cache_service()                                          # Load credentials
        with Temp_Env_Vars(env_vars={ENV_VAR__URL__CACHE_SERVICE: URL__LIVE_SERVER}):
            client = Client__Cache__Service().client()
            result = client.info().health()
            return result and result.get('status') == 'ok'
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# Performance Test Class
# ═══════════════════════════════════════════════════════════════════════════════

class test_perf__Phase_E_6__5__Backend_Comparison(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.storage_path   = path_combine(phase_e.path, '../perf_results')
        cls.report_storage = Perf_Report__Storage__File_System(storage_path=cls.storage_path)
        cls.generator      = Html_Generator__For_Benchmarks()
        cls.config         = Schema__Perf_Benchmark__Timing__Config(title            = REPORT_TITLE,
                                                                    measure_only_3   = True        ,
                                                                    print_to_console = False       ,
                                                                    asserts_enabled  = False       )

        # ───────────────────────────────────────────────────────────────────────
        # Backend enable flags
        # ───────────────────────────────────────────────────────────────────────
        cls.enable_local_server  = False
        cls.enable_remote_server = False

        # ───────────────────────────────────────────────────────────────────────
        # Pre-generate test HTML (50 paragraphs for reasonable test time)
        # ───────────────────────────────────────────────────────────────────────
        with graph_deterministic_ids():
            cls.html_50 = cls.generator.generate__50()

        # ───────────────────────────────────────────────────────────────────────
        # Pre-compute pipeline data
        # ───────────────────────────────────────────────────────────────────────
        with graph_deterministic_ids():
            cls.html_str   = cls.html_50
            cls.html_dict  = Html__To__Html_Dict__With__Node_Ids(html=cls.html_str).convert()
            cls.mgraph_doc = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(cls.html_dict)

        # ───────────────────────────────────────────────────────────────────────
        # Set up in-memory cache (always available)
        # ───────────────────────────────────────────────────────────────────────
        cls.inmem_cache_client, cls.inmem_cache_service = client_cache_service()
        cls.inmem_client_wrapper = Cache_Service__Client(cache_client=cls.inmem_cache_client)

        # ───────────────────────────────────────────────────────────────────────
        # Check backend availability
        # ───────────────────────────────────────────────────────────────────────
        cls.local_available = cls.enable_local_server  and is_local_server_available()
        cls.live_available  = cls.enable_remote_server and is_live_server_available()

        if cls.enable_local_server and not cls.local_available:
            print(f"\n⚠ Local server not available at {URL__LOCAL_SERVER}")
        if cls.enable_remote_server and not cls.live_available:
            print(f"\n⚠ Live server not available at {URL__LIVE_SERVER}")

        # ───────────────────────────────────────────────────────────────────────
        # Shared target counter
        # ───────────────────────────────────────────────────────────────────────
        cls.target_counter = [0]

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def next_target(self):
        self.target_counter[0] += 1
        return f'target-{self.target_counter[0]}'

    def create_storage(self, client_wrapper: Cache_Service__Client,             # Create storage for a specific backend
                       session_name: str, target_name: str) -> Perf__Storage__Cache_Service:
        config = Schema__Perf__Storage__Config(storage_mode    = Enum__Storage_Mode.CACHE_SERVICE,
                                               cache_namespace = 'pytest-perf-e6-5'              )
        return Perf__Storage__Cache_Service(config       = config        ,
                                            client       = client_wrapper,
                                            session_name = session_name  ,
                                            target_name  = target_name   )

    def create_layers(self, storage: Perf__Storage__Cache_Service) -> tuple:    # Create layer instances
        stats        = Schema__Html_Cache__Stats()
        layer_html   = Html_Cache__Layer__Html      (storage=storage, stats=stats)
        layer_dict   = Html_Cache__Layer__Html__Dict(storage=storage, stats=stats)
        layer_mgraph = Html_Cache__Layer__MGraph    (storage=storage, stats=stats)
        return layer_html, layer_dict, layer_mgraph, stats

    # ═══════════════════════════════════════════════════════════════════════════
    # Section A: In-Memory Full Pipelines
    # ═══════════════════════════════════════════════════════════════════════════

    def benchmarks__section_A__inmem_pipelines(self, timing: Perf_Benchmark__Timing):
        """In-memory full save/load pipelines (baseline measurement)."""

        # A_01: Full save pipeline (in-memory)
        def stage_A_01__inmem_save_pipeline():
            target   = self.next_target()
            storage  = self.create_storage(self.inmem_client_wrapper, 'inmem-save', target)
            cache_id = storage.create_file__perf_entry()

            layer_html, layer_dict, layer_mgraph, _ = self.create_layers(storage)
            layer_html.save  (cache_id=cache_id, html=self.html_str, source='benchmark')
            layer_dict.save  (cache_id=cache_id, html_dict=self.html_dict)
            layer_mgraph.save(cache_id=cache_id, document=self.mgraph_doc)
            return cache_id

        timing.benchmark('A_01__inmem__save_pipeline', stage_A_01__inmem_save_pipeline)

        # A_02: Full load pipeline (in-memory) - pre-populate first
        inmem_storage_for_load = self.create_storage(self.inmem_client_wrapper, 'inmem-load', 'load-target')
        inmem_cache_id         = inmem_storage_for_load.create_file__perf_entry()
        inmem_layers           = self.create_layers(inmem_storage_for_load)
        inmem_layers[0].save(cache_id=inmem_cache_id, html=self.html_str, source='benchmark')
        inmem_layers[1].save(cache_id=inmem_cache_id, html_dict=self.html_dict)
        inmem_layers[2].save(cache_id=inmem_cache_id, document=self.mgraph_doc)

        def stage_A_02__inmem_load_pipeline():
            l1 = inmem_layers[0].load(cache_id=inmem_cache_id)
            l2 = inmem_layers[1].load(cache_id=inmem_cache_id)
            l3 = inmem_layers[2].load(cache_id=inmem_cache_id)
            return (l1, l2, l3)

        timing.benchmark('A_02__inmem__load_pipeline', stage_A_02__inmem_load_pipeline)

    # ═══════════════════════════════════════════════════════════════════════════
    # Section B: In-Memory Cost Breakdown
    # ═══════════════════════════════════════════════════════════════════════════

    def benchmarks__section_B__inmem_breakdown(self, timing: Perf_Benchmark__Timing):
        """Isolate individual costs: serialization, requests, setup, layers."""

        # B_01: Raw JSON serialization (no network)
        def stage_B_01__raw_json_serialize():
            import json
            data = json.dumps(self.mgraph_doc.json())
            return len(data)

        timing.benchmark('B_01__raw_json_serialize', stage_B_01__raw_json_serialize)

        # B_02: TestClient request overhead (health check)
        def stage_B_02__request_overhead():
            return self.inmem_cache_client.info().health()

        timing.benchmark('B_02__request_overhead', stage_B_02__request_overhead)

        # B_03: Create storage + entry (no layers, no saves)
        def stage_B_03__create_storage_and_entry():
            storage = self.create_storage(self.inmem_client_wrapper, 'inmem-b03', self.next_target())
            return storage.create_file__perf_entry()

        timing.benchmark('B_03__create_storage_and_entry', stage_B_03__create_storage_and_entry)

        # B_04: Create layers only (pre-created storage)
        storage_b04  = self.create_storage(self.inmem_client_wrapper, 'inmem-b04', 'layers-only')
        cache_id_b04 = storage_b04.create_file__perf_entry()

        def stage_B_04__create_layers_only():
            return self.create_layers(storage_b04)

        timing.benchmark('B_04__create_layers_only', stage_B_04__create_layers_only)

        # B_05: Full setup (storage + entry + layers) - for comparison
        def stage_B_05__full_setup():
            storage  = self.create_storage(self.inmem_client_wrapper, 'inmem-b05', self.next_target())
            cache_id = storage.create_file__perf_entry()
            layers   = self.create_layers(storage)
            return cache_id, layers

        timing.benchmark('B_05__full_setup', stage_B_05__full_setup)

        # ───────────────────────────────────────────────────────────────────────
        # Pure save operations (pre-created storage/layers)
        # ───────────────────────────────────────────────────────────────────────
        storage_pure  = self.create_storage(self.inmem_client_wrapper, 'inmem-pure', 'pure-ops')
        cache_id_pure = storage_pure.create_file__perf_entry()
        layer_html_pure, layer_dict_pure, layer_mgraph_pure, _ = self.create_layers(storage_pure)

        # B_06: Pure L1 save
        def stage_B_06__pure_L1_save():
            return layer_html_pure.save(cache_id=cache_id_pure, html=self.html_str, source='benchmark')

        timing.benchmark('B_06__pure_L1_save', stage_B_06__pure_L1_save)

        # B_07: Pure L2 save
        def stage_B_07__pure_L2_save():
            return layer_dict_pure.save(cache_id=cache_id_pure, html_dict=self.html_dict)

        timing.benchmark('B_07__pure_L2_save', stage_B_07__pure_L2_save)

        # B_08: Pure L3 save
        def stage_B_08__pure_L3_save():
            return layer_mgraph_pure.save(cache_id=cache_id_pure, document=self.mgraph_doc)

        timing.benchmark('B_08__pure_L3_save', stage_B_08__pure_L3_save)

        # ───────────────────────────────────────────────────────────────────────
        # Pure load operations (pre-populated)
        # ───────────────────────────────────────────────────────────────────────

        # B_09: Pure L1 load
        def stage_B_09__pure_L1_load():
            return layer_html_pure.load(cache_id=cache_id_pure)

        timing.benchmark('B_09__pure_L1_load', stage_B_09__pure_L1_load)

        # B_10: Pure L2 load
        def stage_B_10__pure_L2_load():
            return layer_dict_pure.load(cache_id=cache_id_pure)

        timing.benchmark('B_10__pure_L2_load', stage_B_10__pure_L2_load)

        # B_11: Pure L3 load
        def stage_B_11__pure_L3_load():
            return layer_mgraph_pure.load(cache_id=cache_id_pure)

        timing.benchmark('B_11__pure_L3_load', stage_B_11__pure_L3_load)

    # ═══════════════════════════════════════════════════════════════════════════
    # Section C: Local Server
    # ═══════════════════════════════════════════════════════════════════════════

    def benchmarks__section_C__local_server(self, timing: Perf_Benchmark__Timing):
        """Local server benchmarks (localhost network overhead)."""

        if not self.local_available:
            return

        load_env_vars__cache_service()
        with Temp_Env_Vars(env_vars={ENV_VAR__URL__CACHE_SERVICE: URL__LOCAL_SERVER}):
            local_cache_client               = Client__Cache__Service().client().setup_config_from_env()
            local_cache_client.config.base_url = URL__LOCAL_SERVER
            local_client_wrapper             = Cache_Service__Client(cache_client=local_cache_client)

            # C_01: Full save pipeline (local)
            def stage_C_01__local_save_pipeline():
                target   = self.next_target()
                storage  = self.create_storage(local_client_wrapper, 'local-save', target)
                cache_id = storage.create_file__perf_entry()

                layer_html, layer_dict, layer_mgraph, _ = self.create_layers(storage)
                layer_html.save  (cache_id=cache_id, html=self.html_str, source='benchmark')
                layer_dict.save  (cache_id=cache_id, html_dict=self.html_dict)
                layer_mgraph.save(cache_id=cache_id, document=self.mgraph_doc)
                return cache_id

            timing.benchmark('C_01__local__save_pipeline', stage_C_01__local_save_pipeline)

            # C_02: Full load pipeline (local) - pre-populate
            local_storage_for_load = self.create_storage(local_client_wrapper, 'local-load', 'load-target')
            local_cache_id         = local_storage_for_load.create_file__perf_entry()
            local_layers           = self.create_layers(local_storage_for_load)
            local_layers[0].save(cache_id=local_cache_id, html=self.html_str, source='benchmark')
            local_layers[1].save(cache_id=local_cache_id, html_dict=self.html_dict)
            local_layers[2].save(cache_id=local_cache_id, document=self.mgraph_doc)

            def stage_C_02__local_load_pipeline():
                l1 = local_layers[0].load(cache_id=local_cache_id)
                l2 = local_layers[1].load(cache_id=local_cache_id)
                l3 = local_layers[2].load(cache_id=local_cache_id)
                return (l1, l2, l3)

            timing.benchmark('C_02__local__load_pipeline', stage_C_02__local_load_pipeline)

    # ═══════════════════════════════════════════════════════════════════════════
    # Section D: Live Serverless
    # ═══════════════════════════════════════════════════════════════════════════

    def benchmarks__section_D__live_server(self, timing: Perf_Benchmark__Timing):
        """Live serverless benchmarks (real-world latency)."""

        if not self.live_available:
            return

        load_env_vars__cache_service()
        with Temp_Env_Vars(env_vars={ENV_VAR__URL__CACHE_SERVICE: URL__LIVE_SERVER}):
            live_cache_client   = Client__Cache__Service().client()
            live_client_wrapper = Cache_Service__Client(cache_client=live_cache_client)

            # D_01: Full save pipeline (live)
            def stage_D_01__live_save_pipeline():
                target   = self.next_target()
                storage  = self.create_storage(live_client_wrapper, 'live-save', target)
                cache_id = storage.create_file__perf_entry()

                layer_html, layer_dict, layer_mgraph, _ = self.create_layers(storage)
                layer_html.save  (cache_id=cache_id, html=self.html_str, source='benchmark')
                layer_dict.save  (cache_id=cache_id, html_dict=self.html_dict)
                layer_mgraph.save(cache_id=cache_id, document=self.mgraph_doc)
                return cache_id

            timing.benchmark('D_01__live__save_pipeline', stage_D_01__live_save_pipeline)

            # D_02: Full load pipeline (live) - pre-populate
            live_storage_for_load = self.create_storage(live_client_wrapper, 'live-load', 'load-target')
            live_cache_id         = live_storage_for_load.create_file__perf_entry()
            live_layers           = self.create_layers(live_storage_for_load)
            live_layers[0].save(cache_id=live_cache_id, html=self.html_str, source='benchmark')
            live_layers[1].save(cache_id=live_cache_id, html_dict=self.html_dict)
            live_layers[2].save(cache_id=live_cache_id, document=self.mgraph_doc)

            def stage_D_02__live_load_pipeline():
                l1 = live_layers[0].load(cache_id=live_cache_id)
                l2 = live_layers[1].load(cache_id=live_cache_id)
                l3 = live_layers[2].load(cache_id=live_cache_id)
                return (l1, l2, l3)

            timing.benchmark('D_02__live__load_pipeline', stage_D_02__live_load_pipeline)

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Benchmark Orchestrator
    # ═══════════════════════════════════════════════════════════════════════════

    def benchmarks(self, timing: Perf_Benchmark__Timing):
        """Run all benchmark sections."""
        self.benchmarks__section_A__inmem_pipelines(timing)
        self.benchmarks__section_B__inmem_breakdown(timing)
        self.benchmarks__section_C__local_server   (timing)
        self.benchmarks__section_D__live_server    (timing)

    # ═══════════════════════════════════════════════════════════════════════════
    # Test Method
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test__backend_comparison(self):
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

        # Print report to console
        print(Perf_Report__Renderer__Text().render(report))