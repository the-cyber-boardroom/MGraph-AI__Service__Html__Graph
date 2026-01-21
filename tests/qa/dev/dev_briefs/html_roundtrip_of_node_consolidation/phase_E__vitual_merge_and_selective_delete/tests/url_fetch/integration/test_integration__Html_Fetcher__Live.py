# ═══════════════════════════════════════════════════════════════════════════════
# test_integration__Live_Url_Fetch - Integration tests with live HTTP and cache service
# ═══════════════════════════════════════════════════════════════════════════════
#
# These tests require:
#   1. Internet connection (to fetch from live test sites)
#   2. Cache service running at http://localhost:10017/
#
# Run with: pytest test_integration__Live_Url_Fetch.py -v
# ═══════════════════════════════════════════════════════════════════════════════

import pytest
from unittest                                                                      import TestCase
from mgraph_ai_service_cache_client.client.Client__Cache__Service                  import Client__Cache__Service
from mgraph_ai_service_cache_client.schemas.consts.consts__Cache_Client import ENV_VAR__URL__TARGET_SERVER__CACHE_SERVICE

from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url           import Safe_Str__Url
from osbot_utils.utils.Env import get_env, load_dotenv
from osbot_utils.utils.Files import path_combine, file_exists
from phase_e.url_fetch.Html_Fetcher                                                import Html_Fetcher
from phase_e.url_fetch.Html_Cache__Session                                         import Html_Cache__Session
from phase_e.url_fetch.Html_Cache__Session_Factory                                 import Html_Cache__Session_Factory
from phase_e.url_fetch.Html_Cache__Layer__Url                                      import Html_Cache__Layer__Url
from phase_e.url_fetch.schemas.Schema__Html_Cache__L0__Url_Metadata import Schema__Html_Cache__L0__Url_Metadata
from phase_e.url_fetch.schemas.Schema__Html_Fetcher__Config                        import Schema__Html_Fetcher__Config
from phase_e.url_fetch.schemas.Schema__Url_Fetch__Stats                            import Schema__Url_Fetch__Stats
from phase_e.storage.backends.Perf__Storage__Cache_Service                         import Perf__Storage__Cache_Service
from phase_e.storage.cache_service.Cache_Service__Client                           import Cache_Service__Client
from phase_e.storage.schemas.Schema__Perf__Storage__Config                         import Schema__Perf__Storage__Config
from phase_e.storage.safe_str.Safe_Str__Session_Name                               import Safe_Str__Session_Name


# ═══════════════════════════════════════════════════════════════════════════════
# Test Configuration
# ═══════════════════════════════════════════════════════════════════════════════

TEST_ENABLED      = False
CACHE_SERVICE_URL = 'http://localhost:10017'
CACHE_NAMESPACE   = 'phase-e5-integration-tests'

# Common test sites for web testing
TEST_URLS = {
    'example'     : 'https://example.com/',                           # Simple static HTML
    'httpbin_html': 'https://httpbin.org/html',                       # Returns HTML page
    'httpbin_get' : 'https://httpbin.org/get',                        # Returns JSON (tests non-HTML)
    'iana'        : 'https://www.iana.org/domains/reserved',          # Another simple page
}

def load_env_vars__cache_service():
    if TEST_ENABLED:
        env_var_file_name      = '.cache_service.env'
        env_var_file           = path_combine(__file__, f'../{env_var_file_name}')
        load_dotenv(dotenv_path=env_var_file, override=True)
        url_cache_service =  get_env(ENV_VAR__URL__TARGET_SERVER__CACHE_SERVICE)

        assert file_exists(env_var_file)
        assert url_cache_service is not None


def create_live_cache_client():
    """Create a cache client pointing to the live cache service."""
    client = Client__Cache__Service()
    #client.set__server_url(CACHE_SERVICE_URL)
    return client.client()


def is_cache_service_available():
    load_env_vars__cache_service()
    """Check if the cache service is running."""
    try:
        client = create_live_cache_client()
        result = client.info().health()
        return result and result.get('status') == 'ok'
    except Exception as e:
        print(f"Cache service not available: {e}")
        return False


# Skip all tests if cache service is not available
pytestmark = pytest.mark.skipif(
    not is_cache_service_available(),
    reason=f"Cache service not available at {CACHE_SERVICE_URL}"
)


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Html_Fetcher with Live Sites
# ═══════════════════════════════════════════════════════════════════════════════

class test_integration__Html_Fetcher__Live(TestCase):
    """Test Html_Fetcher against real websites."""

    @classmethod
    def setUpClass(cls):
        cls.fetcher = Html_Fetcher(config=Schema__Html_Fetcher__Config(timeout_seconds         = 30,
                                                                       max_retries             = 3,
                                                                       min_request_interval_ms = 500,                            # Be nice to servers
                                                                       user_agent              = 'MGraph-AI Integration Test/1.0'))

    # def test_fetch__example_com(self):                                 # Test fetching example.com
    #     url      = Safe_Str__Url(TEST_URLS['example'])
    #     response = self.fetcher.fetch(url)
    #
    #     assert response.ok is True
    #     assert int(response.status_code) == 200
    #     assert 'Example Domain' in response.html
    #     assert '<html' in response.html.lower()
    #     print(f"\n✓ Fetched example.com: {len(response.html)} bytes in {response.duration_ms}ms")

    def test_fetch__httpbin_html(self):                                # Test fetching httpbin HTML page
        url      = Safe_Str__Url(TEST_URLS['httpbin_html'])
        response = self.fetcher.fetch(url)

        assert response.ok is True
        assert int(response.status_code) == 200
        assert '<html' in response.html.lower()
        print(f"\n✓ Fetched httpbin.org/html: {len(response.html)} bytes in {response.duration_ms}ms")

    def test_fetch__response_headers(self):                            # Test that headers are captured
        url      = Safe_Str__Url(TEST_URLS['example'])
        response = self.fetcher.fetch(url)

        assert response.headers is not None
        assert len(response.headers) > 0
        # Most servers return Content-Type
        content_type = response.headers.get('Content-Type', '')
        assert 'text/html' in content_type.lower()
        print(f"\n✓ Headers captured: {list(response.headers.keys())}")

    def test_fetch__duration_reasonable(self):                         # Test that duration is tracked
        url      = Safe_Str__Url(TEST_URLS['example'])
        response = self.fetcher.fetch(url)

        assert int(response.duration_ms) > 0
        assert int(response.duration_ms) < 30000                       # Should complete within timeout
        print(f"\n✓ Duration tracked: {response.duration_ms}ms")


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Full Pipeline with Live Cache Service
# ═══════════════════════════════════════════════════════════════════════════════

class test_integration__Session__Live_Cache(TestCase):
    """Test Html_Cache__Session with live cache service."""

    @classmethod
    def setUpClass(cls):
        # Create live cache client
        cls.raw_client           = create_live_cache_client()
        cls.storage_config       = Schema__Perf__Storage__Config(cache_namespace=CACHE_NAMESPACE)
        cls.cache_client_wrapper = Cache_Service__Client(cache_client = cls.raw_client   ,
                                                         config       = cls.storage_config)

        # Verify connection
        assert cls.cache_client_wrapper.health_check(), "Cache service health check failed"
        print(f"\n✓ Connected to cache service at {CACHE_SERVICE_URL}")

        # Create session factory
        cls.factory = Html_Cache__Session_Factory(
            cache_client   = cls.cache_client_wrapper,
            storage_config = cls.storage_config,
            fetcher_config = Schema__Html_Fetcher__Config(
                timeout_seconds         = 30,
                min_request_interval_ms = 500,
                user_agent              = 'MGraph-AI Integration Test/1.0'
            )
        )

    def test_session__fetch_single_url(self):                          # Test single URL fetch with caching
        with self.factory.create_session_with_name('integration-single') as session:
            url  = Safe_Str__Url(TEST_URLS['example'])
            html = session.get_html_from_url(url)

            assert html is not None
            assert 'Example Domain' in html

            stats = session.get_stats()
            print(f"\n✓ Fetched and cached: {len(html)} bytes")
            print(f"  Stats: {stats}")

    def test_session__fetch_cached_second_time(self):                  # Test cache hit on second fetch
        with self.factory.create_session_with_name('integration-cached') as session:
            url = Safe_Str__Url(TEST_URLS['example'])

            # First fetch - should go to network
            html1 = session.get_html_from_url(url)
            first_misses = int(session.url_stats.l0_misses)

            print(f"\n  First fetch: l0_misses={first_misses}")

            # Reset stats
            session.url_stats.l0_hits   = 0
            session.url_stats.l0_misses = 0

            # Second fetch - should hit cache
            html2 = session.get_html_from_url(url)
            second_hits = int(session.url_stats.l0_hits)

            print(f"  Second fetch: l0_hits={second_hits}")

            assert html1 == html2                                      # Same content
            assert second_hits >= 1                                    # Cache hit
            print(f"✓ Cache hit confirmed!")

    def test_session__batch_fetch_multiple_urls(self):                 # Test batch fetching
        with self.factory.create_session_with_name('integration-batch') as session:
            urls = [
                TEST_URLS['example'],
                TEST_URLS['httpbin_html'],
            ]

            results = session.batch_fetch_urls(urls)

            print(f"\n✓ Batch results:")
            print(f"  Fetched: {results['fetched']}")
            print(f"  Cached:  {results['cached']}")
            print(f"  Failed:  {results['failed']}")

            assert results['failed'] == 0
            assert results['fetched'] + results['cached'] == 2
            assert len(results['html']) == 2

            for url, html in results['html'].items():
                print(f"  - {url}: {len(html)} bytes")

    def test_session__force_refresh(self):                             # Test force refresh bypasses cache
        with self.factory.create_session_with_name('integration-refresh') as session:
            url = Safe_Str__Url(TEST_URLS['example'])

            # First fetch
            html1 = session.get_html_from_url(url)

            # Force refresh
            session.url_stats.l0_misses         = 0
            session.url_stats.network_requests  = 0

            html2 = session.get_html_from_url(url, force_refresh=True)

            assert html2 is not None
            assert int(session.url_stats.l0_misses) == 1               # Network fetch
            assert int(session.url_stats.network_requests) == 1
            print(f"\n✓ Force refresh: network request made")


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Cache Persistence Across Sessions
# ═══════════════════════════════════════════════════════════════════════════════

class test_integration__Cache_Persistence(TestCase):
    """Test that cached data persists across sessions."""

    @classmethod
    def setUpClass(cls):
        cls.raw_client           = create_live_cache_client()
        cls.storage_config       = Schema__Perf__Storage__Config(cache_namespace=CACHE_NAMESPACE)
        cls.cache_client_wrapper = Cache_Service__Client(cache_client = cls.raw_client   ,
                                                         config       = cls.storage_config)

        cls.factory = Html_Cache__Session_Factory(
            cache_client   = cls.cache_client_wrapper,
            storage_config = cls.storage_config,
            fetcher_config = Schema__Html_Fetcher__Config(
                min_request_interval_ms = 500,
                user_agent              = 'MGraph-AI Integration Test/1.0'
            )
        )

    def test_persistence__across_sessions(self):                       # Test data survives session close
        session_name = 'integration-persistence'
        url          = Safe_Str__Url(TEST_URLS['example'])

        # Session 1: Fetch and cache
        with self.factory.create_session_with_name(session_name) as session1:
            html1 = session1.get_html_from_url(url)
            print(f"\n  Session 1: Fetched {len(html1)} bytes")

        # Session 2: Should get from cache
        with self.factory.create_session_with_name(session_name) as session2:
            session2.url_stats.l0_hits   = 0
            session2.url_stats.l0_misses = 0

            html2 = session2.get_html_from_url(url)

            print(f"  Session 2: Got {len(html2)} bytes")
            print(f"  Session 2: l0_hits={session2.url_stats.l0_hits}")

            assert html1 == html2
            assert int(session2.url_stats.l0_hits) >= 1
            print(f"✓ Cache persisted across sessions!")


# ═══════════════════════════════════════════════════════════════════════════════
# Test: L0 Layer Direct Access
# ═══════════════════════════════════════════════════════════════════════════════

class test_integration__Layer_Url__Live(TestCase):
    """Test Html_Cache__Layer__Url directly with live service."""

    @classmethod
    def setUpClass(cls):
        cls.raw_client           = create_live_cache_client()
        cls.storage_config       = Schema__Perf__Storage__Config(cache_namespace=CACHE_NAMESPACE)
        cls.cache_client_wrapper = Cache_Service__Client(cache_client = cls.raw_client   ,
                                                         config       = cls.storage_config)

        # Create storage directly
        cls.storage = Perf__Storage__Cache_Service(
            config       = cls.storage_config,
            client       = cls.cache_client_wrapper,
            session_name = Safe_Str__Session_Name('integration-layer-test'),
            target_name  = 'example-com'
        )

        # Create fetcher and stats
        cls.fetcher = Html_Fetcher(config=Schema__Html_Fetcher__Config(
            min_request_interval_ms = 500,
            user_agent              = 'MGraph-AI Integration Test/1.0'
        ))
        cls.stats = Schema__Url_Fetch__Stats()

        # Create layer
        cls.layer = Html_Cache__Layer__Url(
            storage = cls.storage,
            stats   = cls.stats,
            fetcher = cls.fetcher
        )

        # Create cache entry
        cls.cache_id = cls.storage.create_file__perf_entry()

    def test_layer__fetch_and_cache_metadata(self):                    # Test L0 metadata caching
        url  = Safe_Str__Url(TEST_URLS['example'])
        html = self.layer.get_html(cache_id=self.cache_id, url=url)

        assert html is not None
        assert 'Example Domain' in html
        print(f"\n✓ Fetched via layer: {len(html)} bytes")

        # Check metadata was cached
        metadata = self.layer.load_metadata(cache_id=self.cache_id)
        assert type(metadata) is Schema__Html_Cache__L0__Url_Metadata

        print(f"✓ Metadata cached:")
        print(f"  url: {metadata.url}")
        print(f"  status_code: {metadata.status_code}")
        print(f"  content_hash: {metadata.content_hash}")


# ═══════════════════════════════════════════════════════════════════════════════
# Run Tests
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])