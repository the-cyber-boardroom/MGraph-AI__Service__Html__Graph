# ═══════════════════════════════════════════════════════════════════════════════
# test_integration__Phase_E_0__MGraph_Transformations
# ═══════════════════════════════════════════════════════════════════════════════
#
# This test applies Phase E_0 (Virtual Merge + Selective Delete) to L3 MGraphs
# fetched from live URLs, creating filtered/cleaned versions.
#
# Pipeline:
#   L0 → L1 → L2 → L3 (MGraph)
#                      │
#                      ├── L4: Round-trip HTML (verify fidelity)
#                      │
#                      └── L5: Phase E_0 Processing
#                              ├── L5a: Text extraction results
#                              ├── L5b: Virtual merge results
#                              ├── L5c: Decision results
#                              ├── L5d: Filtered MGraph
#                              └── L5e: Clean HTML
#
# Requires:
#   1. Internet connection
#   2. Cache service URL in .cache_service.env file
#
# Run with: pytest test_integration__Phase_E_0__MGraph_Transformations.py -v -s
# ═══════════════════════════════════════════════════════════════════════════════

import pytest
from unittest                                                                                               import TestCase
from osbot_utils.utils.Env import get_env, load_dotenv
from osbot_utils.utils.Files                                                                                import file_exists, path_combine
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                                    import Safe_Str__Url
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                          import Cache_Id
from mgraph_ai_service_cache_client.client.Client__Cache__Service                                           import Client__Cache__Service
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids        import Html__To__Html_Dict__With__Node_Ids
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html            import Html_MGraph__Document__To__Html
from phase_e.core.Phase_E__Text_Extractor                                                                   import Phase_E__Text_Extractor
from phase_e.core.Phase_E__Virtual_Merger                                                                   import Phase_E__Virtual_Merger
from phase_e.core.Phase_E__Node_Deleter                                                                     import Phase_E__Node_Deleter
from phase_e.decision.Phase_E__Decision_Engine__Hash_Based                                                  import Phase_E__Decision_Engine__Hash_Based
from phase_e.url_fetch.Html_Fetcher                                                                         import Html_Fetcher
from phase_e.url_fetch.Html_Cache__Layer__Url                                                               import Html_Cache__Layer__Url
from phase_e.url_fetch.schemas.Schema__Html_Fetcher__Config                                                 import Schema__Html_Fetcher__Config
from phase_e.url_fetch.schemas.Schema__Url_Fetch__Stats                                                     import Schema__Url_Fetch__Stats
from phase_e.storage.backends.Perf__Storage__Cache_Service                                                  import Perf__Storage__Cache_Service
from phase_e.storage.cache_service.Cache_Service__Client                                                    import Cache_Service__Client
from phase_e.storage.schemas.Schema__Perf__Storage__Config                                                  import Schema__Perf__Storage__Config
from phase_e.storage.safe_str.Safe_Str__Session_Name                                                        import Safe_Str__Session_Name
from phase_e.storage.safe_str.Safe_Str__Target_Name                                                         import Safe_Str__Target_Name


# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

ENV_VAR__URL__TARGET_SERVER__CACHE_SERVICE = 'URL__TARGET_SERVER__CACHE_SERVICE'
CACHE_NAMESPACE                            = 'phase-e0-transformations'

TEST_URLS = {
    # 'example'     : 'https://example.com/',
    # 'httpbin_html': 'https://httpbin.org/html',

    'docs.diniscruz.ai' : 'https://docs.diniscruz.ai' ,
    "text.npr.org"      : "https://text.npr.org" ,
    'paulgraham.com'    : 'https://paulgraham.com'
}


def load_env_vars__cache_service():
    """Load cache service URL from .cache_service.env file."""
    env_var_file_name = '.cache_service.env'
    env_var_file      = path_combine(__file__, f'../{env_var_file_name}')
    load_dotenv(dotenv_path=env_var_file, override=True)
    url_cache_service = get_env(ENV_VAR__URL__TARGET_SERVER__CACHE_SERVICE)

    assert file_exists(env_var_file), f"Env file not found: {env_var_file}"
    assert url_cache_service is not None, f"Env var {ENV_VAR__URL__TARGET_SERVER__CACHE_SERVICE} not set"

    return url_cache_service


def create_live_cache_client(url_cache_service: str):
    """Create a cache client pointing to the live cache service."""
    client = Client__Cache__Service()
    return client.client()


def is_cache_service_available():
    """Check if the cache service is running."""
    try:
        url_cache_service = load_env_vars__cache_service()
        client            = create_live_cache_client(url_cache_service)
        result            = client.info().health()
        return result and result.get('status') == 'ok'
    except Exception as e:
        print(f"Cache service not available: {e}")
        return False


# Skip all tests if cache service is not available
pytestmark = pytest.mark.skipif(
    not is_cache_service_available(),
    reason="Cache service not available (check .cache_service.env)"
)


# ═══════════════════════════════════════════════════════════════════════════════
# Full Pipeline with Phase E_0 Transformations
# ═══════════════════════════════════════════════════════════════════════════════

class LETS_Pipeline__With_Phase_E_0:
    """Process URL through L0-L3, then apply Phase E_0 transformations."""

    def __init__(self, storage: Perf__Storage__Cache_Service, fetcher: Html_Fetcher,
                 decision_threshold: float = 0.5):
        self.storage            = storage
        self.fetcher            = fetcher
        self.stats              = Schema__Url_Fetch__Stats()
        self.decision_threshold = decision_threshold

    def process_url(self, url: Safe_Str__Url) -> dict:
        """Process URL through full pipeline including Phase E_0."""
        result = {
            'url'      : str(url),
            'cache_id' : None,
            'L0'       : {'stored': False, 'data': None},
            'L1'       : {'stored': False, 'size': 0},
            'L2'       : {'stored': False, 'keys': 0},
            'L3'       : {'stored': False, 'nodes': 0, 'edges': 0},
            'L4'       : {'stored': False, 'size': 0},                          # Round-trip HTML
            'L5'       : {                                                      # Phase E_0 results
                'stored'          : False,
                'text_nodes'      : 0,
                'merged_texts'    : 0,
                'decisions'       : {'keep': 0, 'delete': 0},
                'nodes_deleted'   : 0,
                'clean_html_size' : 0,
            },
        }

        # Create cache entry
        cache_id = self.storage.create_file__perf_entry()
        result['cache_id'] = str(cache_id)

        # ─────────────────────────────────────────────────────────────────────
        # L0: Fetch URL and store metadata
        # ─────────────────────────────────────────────────────────────────────
        layer_url = Html_Cache__Layer__Url(
            storage = self.storage,
            stats   = self.stats,
            fetcher = self.fetcher
        )

        html = layer_url.get_html(cache_id=cache_id, url=url)
        if not html:
            return result

        result['L0']['stored'] = True
        result['L0']['data']   = layer_url.load_metadata(cache_id=cache_id)

        # ─────────────────────────────────────────────────────────────────────
        # L1: Store raw HTML
        # ─────────────────────────────────────────────────────────────────────
        l1_saved = self.storage.save(cache_id=cache_id, key='L1/raw-html', data={'html': html})
        result['L1']['stored'] = l1_saved
        result['L1']['size']   = len(html)

        # ─────────────────────────────────────────────────────────────────────
        # L2: Parse HTML to dict with node IDs
        # ─────────────────────────────────────────────────────────────────────
        html_dict = None
        try:
            html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()
            if html_dict:
                l2_saved = self.storage.save(cache_id=cache_id, key='L2/html-dict', data=html_dict)
                result['L2']['stored'] = l2_saved
                result['L2']['keys']   = self._count_keys(html_dict)
        except Exception as e:
            print(f"L2 error: {e}")

        # ─────────────────────────────────────────────────────────────────────
        # L3: Build MGraph document
        # ─────────────────────────────────────────────────────────────────────
        document = None
        try:
            if html_dict:
                converter = Html__To__Html_MGraph__Document__Node_Id_Reuse()
                document  = converter.convert_from_dict(html_dict)

                if document:
                    doc_json = document.json()
                    l3_saved = self.storage.save(cache_id=cache_id, key='L3/mgraph-document', data=doc_json)
                    result['L3']['stored'] = l3_saved

                    # Get node/edge counts
                    if hasattr(document, 'body_graph') and document.body_graph:
                        try:
                            stats = document.body_graph.stats()
                            if stats:
                                result['L3']['nodes'] = stats.total_nodes
                                result['L3']['edges'] = stats.total_edges
                        except:
                            pass
        except Exception as e:
            print(f"L3 error: {e}")

        # ─────────────────────────────────────────────────────────────────────
        # L4: Round-trip HTML (verify fidelity)
        # ─────────────────────────────────────────────────────────────────────
        try:
            if document:
                roundtrip_html = Html_MGraph__Document__To__Html().convert(document)
                if roundtrip_html:
                    l4_saved = self.storage.save(cache_id=cache_id, key='L4/roundtrip-html',
                                                 data={'html': roundtrip_html})
                    result['L4']['stored'] = l4_saved
                    result['L4']['size']   = len(roundtrip_html)
        except Exception as e:
            print(f"L4 error: {e}")

        # ─────────────────────────────────────────────────────────────────────
        # L5: Phase E_0 - Virtual Merge + Selective Delete
        # ─────────────────────────────────────────────────────────────────────
        try:
            if document:
                # Need to rebuild document for Phase E_0 (it modifies in place)
                document_for_filtering = converter.convert_from_dict(html_dict)

                # Step 1: Extract text nodes
                extractor  = Phase_E__Text_Extractor()
                text_nodes = extractor.extract(document_for_filtering)

                # Store text extraction results
                text_nodes_serializable = {
                    node_id: {'text': str(info.text), 'parent_id': str(info.parent_id)}
                    for node_id, info in text_nodes.items()
                }
                self.storage.save(cache_id=cache_id, key='L5/a-text-nodes', data=text_nodes_serializable)
                result['L5']['text_nodes'] = len(text_nodes)

                # Step 2: Virtual merge
                merger       = Phase_E__Virtual_Merger()
                merged_texts = merger.merge(text_nodes, document_for_filtering)

                # Store merge results
                merged_serializable = {
                    parent_id: {
                        'merged_text': str(info.merged_text),
                        'source_node_ids': [str(n) for n in info.source_node_ids]
                    }
                    for parent_id, info in merged_texts.items()
                }
                self.storage.save(cache_id=cache_id, key='L5/b-merged-texts', data=merged_serializable)
                result['L5']['merged_texts'] = len(merged_texts)

                # Step 3: Decision engine
                decision_engine = Phase_E__Decision_Engine__Hash_Based(threshold=self.decision_threshold)
                decisions       = decision_engine.classify_all(merged_texts)

                # Store decision results
                decisions_serializable = {
                    parent_id: {
                        'keep': info.keep,
                        'score': float(info.score),
                        'reason': str(info.reason)
                    }
                    for parent_id, info in decisions.items()
                }
                self.storage.save(cache_id=cache_id, key='L5/c-decisions', data=decisions_serializable)

                keep_count   = sum(1 for d in decisions.values() if d.keep)
                delete_count = sum(1 for d in decisions.values() if not d.keep)
                result['L5']['decisions'] = {'keep': keep_count, 'delete': delete_count}

                # Step 4: Delete unwanted nodes
                parents_to_delete = decision_engine.get_parents_to_delete(decisions)
                deleter           = Phase_E__Node_Deleter()
                deleted_count     = deleter.delete(document_for_filtering, parents_to_delete)
                result['L5']['nodes_deleted'] = int(deleted_count)

                # Store filtered MGraph
                filtered_json = document_for_filtering.json()
                self.storage.save(cache_id=cache_id, key='L5/d-filtered-mgraph', data=filtered_json)

                # Step 5: Convert filtered MGraph to clean HTML
                clean_html = Html_MGraph__Document__To__Html().convert(document_for_filtering)
                self.storage.save(cache_id=cache_id, key='L5/e-clean-html', data={'html': clean_html})
                result['L5']['clean_html_size'] = len(clean_html)
                result['L5']['stored'] = True

        except Exception as e:
            print(f"L5 (Phase E_0) error: {e}")
            import traceback
            traceback.print_exc()

        return result

    def _count_keys(self, d: dict, count: int = 0) -> int:
        """Recursively count keys in nested dict."""
        for key, value in d.items():
            count += 1
            if isinstance(value, dict):
                count = self._count_keys(value, count)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        count = self._count_keys(item, count)
        return count


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Phase E_0 Transformations
# ═══════════════════════════════════════════════════════════════════════════════

class test_integration__Phase_E_0_Transformations(TestCase):
    """Test Phase E_0 transformations on live URLs."""

    @classmethod
    def setUpClass(cls):
        cls.url_cache_service = load_env_vars__cache_service()
        print(f"\n✓ Loaded cache service URL: {cls.url_cache_service}")

        cls.raw_client           = create_live_cache_client(cls.url_cache_service)
        cls.storage_config       = Schema__Perf__Storage__Config(cache_namespace=CACHE_NAMESPACE)
        cls.cache_client_wrapper = Cache_Service__Client(cache_client = cls.raw_client,
                                                         config       = cls.storage_config)

        assert cls.cache_client_wrapper.health_check(), "Cache service health check failed"
        print(f"✓ Connected to cache service")

        cls.fetcher = Html_Fetcher(config=Schema__Html_Fetcher__Config(
            timeout_seconds         = 30,
            min_request_interval_ms = 500,
            user_agent              = 'MGraph-AI Phase E_0 Test/1.0'
        ))

    def _create_storage(self, session_name: str, target_name: str) -> Perf__Storage__Cache_Service:
        return Perf__Storage__Cache_Service(
            config       = self.storage_config,
            client       = self.cache_client_wrapper,
            session_name = Safe_Str__Session_Name(session_name),
            target_name  = Safe_Str__Target_Name(target_name)
        )

    # def test_phase_e0__example_com(self):                                       # Test Phase E_0 on example.com
    #     storage  = self._create_storage('phase-e0-test', 'example-com')
    #     pipeline = LETS_Pipeline__With_Phase_E_0(
    #         storage            = storage,
    #         fetcher            = self.fetcher,
    #         decision_threshold = 0.5
    #     )
    #
    #     url    = Safe_Str__Url(TEST_URLS['example'])
    #     result = pipeline.process_url(url)
    #
    #     print(f"\n{'='*70}")
    #     print(f"Phase E_0 Transformation: {url}")
    #     print(f"{'='*70}")
    #     print(f"Cache ID: {result['cache_id']}")
    #
    #     print(f"\n--- Base Pipeline (L0-L4) ---")
    #     print(f"L0 (URL Fetch):    {result['L0']['stored']}")
    #     print(f"L1 (Raw HTML):     {result['L1']['stored']} ({result['L1']['size']:,} bytes)")
    #     print(f"L2 (HTML Dict):    {result['L2']['stored']} ({result['L2']['keys']} keys)")
    #     print(f"L3 (MGraph):       {result['L3']['stored']} ({result['L3']['nodes']} nodes, {result['L3']['edges']} edges)")
    #     print(f"L4 (Round-trip):   {result['L4']['stored']} ({result['L4']['size']:,} bytes)")
    #
    #     print(f"\n--- Phase E_0 Processing (L5) ---")
    #     print(f"L5a Text Nodes:    {result['L5']['text_nodes']}")
    #     print(f"L5b Merged Texts:  {result['L5']['merged_texts']}")
    #     print(f"L5c Decisions:     Keep={result['L5']['decisions']['keep']}, Delete={result['L5']['decisions']['delete']}")
    #     print(f"L5d Nodes Deleted: {result['L5']['nodes_deleted']}")
    #     print(f"L5e Clean HTML:    {result['L5']['clean_html_size']:,} bytes")
    #
    #     # Assertions
    #     assert result['L0']['stored'] is True
    #     assert result['L3']['stored'] is True
    #     assert result['L5']['stored'] is True
    #     #assert result['L5']['text_nodes'] > 0
    #
    #     # Size comparison
    #     original_size = result['L1']['size']
    #     clean_size    = result['L5']['clean_html_size']
    #     reduction     = ((original_size - clean_size) / original_size * 100) if original_size > 0 else 0
    #
    #     print(f"\n--- Size Comparison ---")
    #     print(f"Original HTML: {original_size:,} bytes")
    #     print(f"Clean HTML:    {clean_size:,} bytes")
    #     print(f"Reduction:     {reduction:.1f}%")
    #
    #     print(f"\n✓ Phase E_0 transformation complete!")

    # def test_phase_e0__httpbin(self):                                           # Test Phase E_0 on httpbin
    #     storage  = self._create_storage('phase-e0-test', 'httpbin-org-html')
    #     pipeline = LETS_Pipeline__With_Phase_E_0(
    #         storage            = storage,
    #         fetcher            = self.fetcher,
    #         decision_threshold = 0.5
    #     )
    #
    #     url    = Safe_Str__Url(TEST_URLS['httpbin_html'])
    #     result = pipeline.process_url(url)
    #
    #     print(f"\n{'='*70}")
    #     print(f"Phase E_0 Transformation: {url}")
    #     print(f"{'='*70}")
    #
    #     print(f"L3 MGraph:     {result['L3']['nodes']} nodes, {result['L3']['edges']} edges")
    #     print(f"L5 Text Nodes: {result['L5']['text_nodes']}")
    #     print(f"L5 Decisions:  Keep={result['L5']['decisions']['keep']}, Delete={result['L5']['decisions']['delete']}")
    #     print(f"L5 Deleted:    {result['L5']['nodes_deleted']}")
    #
    #     assert result['L5']['stored'] is True
    #     print(f"\n✓ Phase E_0 transformation complete!")

    # def test_phase_e0__different_thresholds(self):                              # Test different decision thresholds
    #     url = Safe_Str__Url(TEST_URLS['example'])
    #
    #     print(f"\n{'='*70}")
    #     print(f"Phase E_0: Threshold Comparison")
    #     print(f"{'='*70}")
    #
    #     thresholds = [0.3, 0.5, 0.7, 0.9]
    #     results    = []
    #
    #     for threshold in thresholds:
    #         storage  = self._create_storage(f'threshold-{int(threshold*100)}', 'example-com')
    #         pipeline = LETS_Pipeline__With_Phase_E_0(
    #             storage            = storage,
    #             fetcher            = self.fetcher,
    #             decision_threshold = threshold
    #         )
    #
    #         result = pipeline.process_url(url)
    #         results.append((threshold, result))
    #
    #     print(f"\n{'Threshold':<12} {'Keep':<8} {'Delete':<8} {'Deleted':<10} {'Clean Size':<12}")
    #     print("-" * 50)
    #
    #     for threshold, result in results:
    #         keep    = result['L5']['decisions']['keep']
    #         delete  = result['L5']['decisions']['delete']
    #         deleted = result['L5']['nodes_deleted']
    #         size    = result['L5']['clean_html_size']
    #         print(f"{threshold:<12} {keep:<8} {delete:<8} {deleted:<10} {size:<12,}")
    #
    #     print(f"\n✓ Threshold comparison complete!")


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Verify Cached Phase E_0 Data
# ═══════════════════════════════════════════════════════════════════════════════

class test_integration__Verify_Phase_E_0_Cache(TestCase):
    """Verify that Phase E_0 intermediate data is cached correctly."""

    @classmethod
    def setUpClass(cls):
        cls.url_cache_service    = load_env_vars__cache_service()
        cls.raw_client           = create_live_cache_client(cls.url_cache_service)
        cls.storage_config       = Schema__Perf__Storage__Config(cache_namespace=CACHE_NAMESPACE)
        cls.cache_client_wrapper = Cache_Service__Client(cache_client = cls.raw_client,
                                                         config       = cls.storage_config)
        cls.fetcher = Html_Fetcher(config=Schema__Html_Fetcher__Config(min_request_interval_ms=500))

    # def test_retrieve_phase_e0_artifacts(self):                                 # Test retrieving all Phase E_0 artifacts
    #     storage  = Perf__Storage__Cache_Service(
    #         config       = self.storage_config,
    #         client       = self.cache_client_wrapper,
    #         session_name = Safe_Str__Session_Name('verify-phase-e0'),
    #         target_name  = Safe_Str__Target_Name('example-com')
    #     )
    #     pipeline = LETS_Pipeline__With_Phase_E_0(storage=storage, fetcher=self.fetcher)
    #
    #     url          = Safe_Str__Url(TEST_URLS['example'])
    #     store_result = pipeline.process_url(url)
    #     cache_id     = Cache_Id(store_result['cache_id'])
    #
    #     print(f"\n{'='*70}")
    #     print(f"Verifying Phase E_0 Cached Artifacts")
    #     print(f"{'='*70}")
    #     print(f"Cache ID: {cache_id}")
    #
    #     # Retrieve L5a: Text nodes
    #     text_nodes = storage.load__json(cache_id=cache_id, key='L5/a-text-nodes')
    #     print(f"\nL5a Text Nodes: {text_nodes is not None}")
    #     if text_nodes:
    #         print(f"  Count: {len(text_nodes)}")
    #         for node_id, info in list(text_nodes.items())[:3]:
    #             print(f"  - {node_id}: '{info['text'][:50]}...' (parent: {info['parent_id']})")
    #
    #     # Retrieve L5b: Merged texts
    #     merged_texts = storage.load__json(cache_id=cache_id, key='L5/b-merged-texts')
    #     print(f"\nL5b Merged Texts: {merged_texts is not None}")
    #     if merged_texts:
    #         print(f"  Count: {len(merged_texts)}")
    #         for parent_id, info in list(merged_texts.items())[:3]:
    #             print(f"  - {parent_id}: '{info['merged_text'][:50]}...'")
    #
    #     # Retrieve L5c: Decisions
    #     decisions = storage.load__json(cache_id=cache_id, key='L5/c-decisions')
    #     print(f"\nL5c Decisions: {decisions is not None}")
    #     if decisions:
    #         keep_count   = sum(1 for d in decisions.values() if d['keep'])
    #         delete_count = sum(1 for d in decisions.values() if not d['keep'])
    #         print(f"  Keep: {keep_count}, Delete: {delete_count}")
    #         for parent_id, info in list(decisions.items())[:3]:
    #             status = "KEEP" if info['keep'] else "DELETE"
    #             print(f"  - {parent_id}: {status} (score={info['score']:.4f})")
    #
    #     # Retrieve L5d: Filtered MGraph
    #     filtered_mgraph = storage.load__json(cache_id=cache_id, key='L5/d-filtered-mgraph')
    #     print(f"\nL5d Filtered MGraph: {filtered_mgraph is not None}")
    #     if filtered_mgraph:
    #         print(f"  Keys: {list(filtered_mgraph.keys())}")
    #
    #     # Retrieve L5e: Clean HTML
    #     clean_html_data = storage.load__json(cache_id=cache_id, key='L5/e-clean-html')
    #     print(f"\nL5e Clean HTML: {clean_html_data is not None}")
    #     if clean_html_data:
    #         clean_html = clean_html_data.get('html', '')
    #         print(f"  Size: {len(clean_html):,} bytes")
    #         print(f"  Preview: {clean_html[:200]}...")
    #
    #     # Assertions
    #     # assert text_nodes is not None
    #     # assert merged_texts is not None
    #     # assert decisions is not None
    #     # assert filtered_mgraph is not None
    #     # assert clean_html_data is not None
    #
    #     print(f"\n✓ All Phase E_0 artifacts retrieved successfully!")


# ═══════════════════════════════════════════════════════════════════════════════
# Run Tests
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])