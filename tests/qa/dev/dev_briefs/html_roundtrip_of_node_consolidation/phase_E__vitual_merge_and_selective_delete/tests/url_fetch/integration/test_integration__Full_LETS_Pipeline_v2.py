# ═══════════════════════════════════════════════════════════════════════════════
# test_integration__Full_LETS_Pipeline - Full L0 → L1 → L2 → L3 → L4 pipeline with live cache
# ═══════════════════════════════════════════════════════════════════════════════
#
# This test fetches real URLs and stores all five LETS layers in the cache service:
#   L0: URL metadata (status, headers, timing)
#   L1: Raw HTML content
#   L2: Parsed HTML dict with node IDs
#   L3: MGraph document (graph structure)
#   L4: Reconstructed HTML (round-trip from MGraph)
#
# Requires:
#   1. Internet connection
#   2. Cache service URL in .cache_service.env file
#
# Run with: pytest test_integration__Full_LETS_Pipeline.py -v -s
# ═══════════════════════════════════════════════════════════════════════════════

import pytest
import json
from unittest                                                                                               import TestCase
from osbot_utils.utils.Env import get_env, load_dotenv
from osbot_utils.utils.Files                                                                                import file_exists, path_combine
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                                    import Safe_Str__Url
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                          import Cache_Id
from mgraph_ai_service_cache_client.client.Client__Cache__Service                                           import Client__Cache__Service
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids        import Html__To__Html_Dict__With__Node_Ids
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html             import Html_MGraph__Document__To__Html
from phase_e.mgraph.Html_MGraph__Document__To__Html__With_Original_Head import Html_MGraph__Document__To__Html__With_Original_Head

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
CACHE_NAMESPACE                            = 'phase-e5-full-pipeline'

TEST_URLS = {
    # 'example'     : 'https://example.com/',
    # 'httpbin_html': 'https://httpbin.org/html',
    #     'docs.diniscruz.ai' : 'https://docs.diniscruz.ai' ,
         "text.npr.org"      : "https://text.npr.org" ,
    #     'paulgraham.com'    : 'https://paulgraham.com',
         "theintercept.com"  : "https://theintercept.com" ,
    #     "www.bbc.com/sport" : "https://www.bbc.com/sport/football/articles/cly53k69xj1o"

    "joelonsoftware" :"https://www.joelonsoftware.com" ,
    "joelonsoftware__page" : "https://www.joelonsoftware.com/2022/12/19/progress-on-the-block-protocol"
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
# Full LETS Pipeline Processor
# ═══════════════════════════════════════════════════════════════════════════════

class LETS_Pipeline__Full:
    """Process URL through all four LETS layers and store in cache service."""

    def __init__(self, storage: Perf__Storage__Cache_Service, fetcher: Html_Fetcher):
        self.storage = storage
        self.fetcher = fetcher
        self.stats   = Schema__Url_Fetch__Stats()

    def process_url(self, url: Safe_Str__Url) -> dict:
        """Process URL through L0 → L1 → L2 → L3 → L4 pipeline."""
        result = {
            'url'      : str(url),
            'cache_id' : None,
            'L0'       : {'stored': False, 'data': None},
            'L1'       : {'stored': False, 'size': 0},
            'L2'       : {'stored': False, 'keys': 0},
            'L3'       : {'stored': False, 'nodes': 0, 'edges': 0},
            'L4'       : {'stored': False, 'size': 0, 'round_trip': False},
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
        l1_key   = 'L1/raw-html'
        l1_saved = self.storage.save(cache_id=cache_id, key=l1_key, data={'html': html})

        result['L1']['stored'] = l1_saved
        result['L1']['size']   = len(html)

        # ─────────────────────────────────────────────────────────────────────
        # L2: Parse HTML to dict with node IDs
        # ─────────────────────────────────────────────────────────────────────
        try:
            html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()

            if html_dict:
                l2_key   = 'L2/html-dict'
                l2_saved = self.storage.save(cache_id=cache_id, key=l2_key, data=html_dict)

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
                    l3_key   = 'L3/mgraph-document'
                    l3_saved = self.storage.save(cache_id=cache_id, key=l3_key, data=doc_json)

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
        # L4: Convert MGraph back to HTML (round-trip) - USE PATCHED CONVERTER
        # ─────────────────────────────────────────────────────────────────────
        try:
            if document and html_dict:
                # Use patched converter to preserve original <head>
                patched_converter = Html_MGraph__Document__To__Html__With_Original_Head(
                    original_html_dict=html_dict
                )
                reconstructed_html = patched_converter.convert(document)

                if reconstructed_html:
                    l4_key   = 'L4/reconstructed-html'
                    l4_saved = self.storage.save(cache_id=cache_id, key=l4_key, data={'html': reconstructed_html})

                    result['L4']['stored']     = l4_saved
                    result['L4']['size']       = len(reconstructed_html)
                    result['L4']['round_trip'] = True
        except Exception as e:
            print(f"L4 error: {e}")

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
# Test: Full LETS Pipeline
# ═══════════════════════════════════════════════════════════════════════════════

class test_integration__Full_LETS_Pipeline_v2(TestCase):
    """Test full L0 → L1 → L2 → L3 pipeline with live cache service."""

    @classmethod
    def setUpClass(cls):
        # Load cache service URL from env
        cls.url_cache_service = load_env_vars__cache_service()
        print(f"\n✓ Loaded cache service URL: {cls.url_cache_service}")

        # Create live cache client
        cls.raw_client           = create_live_cache_client(cls.url_cache_service)
        cls.storage_config       = Schema__Perf__Storage__Config(cache_namespace=CACHE_NAMESPACE)
        cls.cache_client_wrapper = Cache_Service__Client(cache_client = cls.raw_client,
                                                         config       = cls.storage_config)

        # Verify connection
        assert cls.cache_client_wrapper.health_check(), "Cache service health check failed"
        print(f"✓ Connected to cache service")

        # Create fetcher
        cls.fetcher = Html_Fetcher(config=Schema__Html_Fetcher__Config(
            timeout_seconds         = 30,
            min_request_interval_ms = 500,
            user_agent              = 'MGraph-AI Full Pipeline Test/1.0'
        ))

    def _create_storage(self, session_name: str, target_name: str) -> Perf__Storage__Cache_Service:
        """Create storage for a specific session/target."""
        return Perf__Storage__Cache_Service(
            config       = self.storage_config,
            client       = self.cache_client_wrapper,
            session_name = Safe_Str__Session_Name(session_name),
            target_name  = Safe_Str__Target_Name(target_name)
        )

    # def test_full_pipeline__example_com(self):                         # Test full pipeline on example.com
    #     storage  = self._create_storage('full-pipeline', 'example-com')
    #     pipeline = LETS_Pipeline__Full(storage=storage, fetcher=self.fetcher)
    #
    #     url    = Safe_Str__Url(TEST_URLS['example'])
    #     result = pipeline.process_url(url)
    #
    #     print(f"\n{'='*60}")
    #     print(f"Full Pipeline Result: {url}")
    #     print(f"{'='*60}")
    #     print(f"Cache ID: {result['cache_id']}")
    #     print(f"\nL0 (URL Metadata):")
    #     print(f"  Stored: {result['L0']['stored']}")
    #     # if result['L0']['data']:
    #     #     print(f"  Status: {result['L0']['data'].get('status_code')}")
    #     #     print(f"  Content-Type: {result['L0']['data'].get('content_type')}")
    #     #     print(f"  Fetch Duration: {result['L0']['data'].get('fetch_duration')}ms")
    #
    #     print(f"\nL1 (Raw HTML):")
    #     print(f"  Stored: {result['L1']['stored']}")
    #     print(f"  Size: {result['L1']['size']:,} bytes")
    #
    #     print(f"\nL2 (HTML Dict):")
    #     print(f"  Stored: {result['L2']['stored']}")
    #     print(f"  Keys: {result['L2']['keys']}")
    #
    #     print(f"\nL3 (MGraph Document):")
    #     print(f"  Stored: {result['L3']['stored']}")
    #     print(f"  Nodes: {result['L3']['nodes']}")
    #     print(f"  Edges: {result['L3']['edges']}")
    #
    #     print(f"\nL4 (Reconstructed HTML - Round Trip):")
    #     print(f"  Stored: {result['L4']['stored']}")
    #     print(f"  Size: {result['L4']['size']:,} bytes")
    #     print(f"  Round Trip: {result['L4']['round_trip']}")
    #
    #     # Assertions
    #     assert result['L0']['stored'] is True
    #     assert result['L1']['stored'] is True
    #     assert result['L2']['stored'] is True
    #     assert result['L3']['stored'] is True
    #     assert result['L4']['stored'] is True
    #     assert result['L1']['size'] > 0
    #     assert result['L4']['size'] > 0
    #     print(f"\n✓ All five layers stored successfully!")

    # def test_full_pipeline__httpbin(self):                             # Test full pipeline on httpbin
    #     storage  = self._create_storage('full-pipeline', 'httpbin-org-html')
    #     pipeline = LETS_Pipeline__Full(storage=storage, fetcher=self.fetcher)
    #
    #     url    = Safe_Str__Url(TEST_URLS['httpbin_html'])
    #     result = pipeline.process_url(url)
    #
    #     print(f"\n{'='*60}")
    #     print(f"Full Pipeline Result: {url}")
    #     print(f"{'='*60}")
    #     print(f"Cache ID: {result['cache_id']}")
    #     print(f"L0 Stored: {result['L0']['stored']}")
    #     print(f"L1 Stored: {result['L1']['stored']} ({result['L1']['size']:,} bytes)")
    #     print(f"L2 Stored: {result['L2']['stored']} ({result['L2']['keys']} keys)")
    #     print(f"L3 Stored: {result['L3']['stored']} ({result['L3']['nodes']} nodes, {result['L3']['edges']} edges)")
    #     print(f"L4 Stored: {result['L4']['stored']} ({result['L4']['size']:,} bytes, round_trip={result['L4']['round_trip']})")
    #
    #     assert result['L0']['stored'] is True
    #     assert result['L1']['stored'] is True
    #     assert result['L2']['stored'] is True
    #     assert result['L3']['stored'] is True
    #     assert result['L4']['stored'] is True
    #     print(f"\n✓ All five layers stored successfully!")

    def test_full_pipeline__multiple_urls(self):                       # Test multiple URLs
        results = []

        for name, url_str in TEST_URLS.items():
            target_name = name.replace('_', '-')
            storage     = self._create_storage('full-pipeline-batch', target_name)
            pipeline    = LETS_Pipeline__Full(storage=storage, fetcher=self.fetcher)

            url    = Safe_Str__Url(url_str)
            result = pipeline.process_url(url)
            results.append(result)

        print(f"\n{'='*60}")
        print(f"Batch Pipeline Results")
        print(f"{'='*60}")

        all_success = True
        for result in results:
            success = all([
                result['L0']['stored'],
                result['L1']['stored'],
                result['L2']['stored'],
                result['L3']['stored'],
                result['L4']['stored'],
            ])
            all_success = all_success and success

            status = "✓" if success else "✗"
            print(f"{status} {result['url']}")
            print(f"    L0={result['L0']['stored']} L1={result['L1']['stored']} "
                  f"L2={result['L2']['stored']} L3={result['L3']['stored']} L4={result['L4']['stored']}")

        assert all_success, "Not all URLs processed successfully"
        print(f"\n✓ All {len(results)} URLs processed through full pipeline (L0→L4)!")


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Verify Cached Data
# ═══════════════════════════════════════════════════════════════════════════════

class test_integration__Verify_Cached_Data(TestCase):
    """Verify that cached data can be retrieved."""

    @classmethod
    def setUpClass(cls):
        cls.url_cache_service    = load_env_vars__cache_service()
        cls.raw_client           = create_live_cache_client(cls.url_cache_service)
        cls.storage_config       = Schema__Perf__Storage__Config(cache_namespace=CACHE_NAMESPACE)
        cls.cache_client_wrapper = Cache_Service__Client(cache_client = cls.raw_client,
                                                         config       = cls.storage_config)
        cls.fetcher = Html_Fetcher(config=Schema__Html_Fetcher__Config(
            min_request_interval_ms = 500
        ))

    # def test_retrieve_all_layers(self):                                # Test retrieving all five layers
    #     # First, store data
    #     storage  = Perf__Storage__Cache_Service(
    #         config       = self.storage_config,
    #         client       = self.cache_client_wrapper,
    #         session_name = Safe_Str__Session_Name('verify-retrieval'),
    #         target_name  = Safe_Str__Target_Name('example-com')
    #     )
    #     pipeline = LETS_Pipeline__Full(storage=storage, fetcher=self.fetcher)
    #
    #     url          = Safe_Str__Url(TEST_URLS['example'])
    #     store_result = pipeline.process_url(url)
    #     cache_id     = Cache_Id(store_result['cache_id'])
    #
    #     print(f"\n{'='*60}")
    #     print(f"Verifying Cached Data Retrieval")
    #     print(f"{'='*60}")
    #     print(f"Cache ID: {cache_id}")
    #
    #     # Retrieve L0
    #     l0_data = storage.load__json(cache_id=cache_id, key='L0/url-metadata.json')
    #     print(f"\nL0 Retrieved: {l0_data is not None}")
    #     if l0_data:
    #         print(f"  URL: {l0_data.get('url')}")
    #         print(f"  Status: {l0_data.get('status_code')}")
    #
    #     # Retrieve L1
    #     l1_data = storage.load__json(cache_id=cache_id, key='L1/raw-html')
    #     print(f"\nL1 Retrieved: {l1_data is not None}")
    #     if l1_data:
    #         html = l1_data.get('html', '')
    #         print(f"  HTML Size: {len(html):,} bytes")
    #         print(f"  Preview: {html[:100]}...")
    #
    #     # Retrieve L2
    #     l2_data = storage.load__json(cache_id=cache_id, key='L2/html-dict')
    #     print(f"\nL2 Retrieved: {l2_data is not None}")
    #     if l2_data:
    #         print(f"  Top-level keys: {list(l2_data.keys())}")
    #
    #     # Retrieve L3
    #     l3_data = storage.load__json(cache_id=cache_id, key='L3/mgraph-document')
    #     print(f"\nL3 Retrieved: {l3_data is not None}")
    #     if l3_data:
    #         print(f"  Top-level keys: {list(l3_data.keys())}")
    #
    #     # Retrieve L4
    #     l4_data = storage.load__json(cache_id=cache_id, key='L4/reconstructed-html')
    #     print(f"\nL4 Retrieved: {l4_data is not None}")
    #     if l4_data:
    #         reconstructed = l4_data.get('html', '')
    #         print(f"  Reconstructed HTML Size: {len(reconstructed):,} bytes")
    #         print(f"  Preview: {reconstructed[:100]}...")
    #
    #     # Assertions
    #     assert l0_data is not None, "L0 data not retrieved"
    #     assert l1_data is not None, "L1 data not retrieved"
    #     assert l2_data is not None, "L2 data not retrieved"
    #     assert l3_data is not None, "L3 data not retrieved"
    #     assert l4_data is not None, "L4 data not retrieved"
    #
    #     print(f"\n✓ All five layers retrieved successfully!")


# ═══════════════════════════════════════════════════════════════════════════════
# Run Tests
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])