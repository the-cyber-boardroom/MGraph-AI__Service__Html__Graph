# ═══════════════════════════════════════════════════════════════════════════════
# test_Html_Graph__Service__Client__integration
# Integration tests for Html Graph service client with actual FastAPI app
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from mgraph_ai_service_cache_client.client.cache_service.register_cache_service                         import register_cache_service__in_memory
from mgraph_ai_service_html_graph.client.Html_Graph__Service__Client                                    import Html_Graph__Service__Client
from mgraph_ai_service_html_graph.client.register_html_graph_service                                    import register_html_graph_service__in_memory
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Store__Response import Schema__Html__Store__Response
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                       import fast_api__service__registry
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode     import Enum__Fast_API__Service__Registry__Client__Mode
from osbot_utils.testing.__ import __, __SKIP__


class test_Html_Graph__Service__Client__integration(TestCase):

    @classmethod
    def setUpClass(cls):                                                        # Setup once for all tests
        fast_api__service__registry.configs__save(clear_configs=True)           # save configs
        register_cache_service__in_memory    ()                                 # wire up cache_service         :)
        register_html_graph_service__in_memory()                                # wire up html_graph service    :)

        cls.html_graph_client = Html_Graph__Service__Client()

    @classmethod
    def tearDownClass(cls):                                                     # Restore global registry
        fast_api__service__registry.configs__restore()

    # ───────────────────────────────────────────────────────────────────────────
    # Health Check Tests
    # ───────────────────────────────────────────────────────────────────────────

    def test__health__returns_true(self):                                       # Test health() method
        with self.html_graph_client as _:
            assert _.health() is True

    # ───────────────────────────────────────────────────────────────────────────
    # Config Lookup Tests
    # ───────────────────────────────────────────────────────────────────────────

    def test__requests__config__returns_registered_config(self):                # Test config lookup
        with self.html_graph_client as _:
            config = _.requests().config()

            assert config is not None
            assert config.mode == Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY

    def test__requests__config__has_fast_api_app(self):                         # Test config has app
        with self.html_graph_client as _:
            config = _.requests().config()

            assert config.fast_api_app is not None

    # ───────────────────────────────────────────────────────────────────────────
    # Store and Load Tests
    # ───────────────────────────────────────────────────────────────────────────

    def test__store_html(self):                                                 # Test store HTML
        with self.html_graph_client as _:
            url  = "https://example.com/test-page"
            html = "<html><body>Test content</body></html>"

            result = _.store_html(url=url, html=html)

            assert result       is not None
            assert type(result) is Schema__Html__Store__Response
            assert result.obj() == __(success    = True                     ,
                                      cache_id   = __SKIP__                 ,
                                      cache_key  = 'example.com/test-page'  ,
                                      cache_hash = '232ee122bfc62a75'       ,
                                      char_count = 38                       ,
                                      final_url  = ''                       )

    def test__store_and_load_html(self):                                        # Test store then load
        with self.html_graph_client as _:
            url  = "https://example.com/roundtrip-test"
            html = "<html><body>Roundtrip test content</body></html>"

            # Store
            store_result = _.store_html(url=url, html=html)
            assert store_result is not None

            # Load
            load_result = _.load_html(url=url)
            assert load_result is not None

    def test__store_html__with_custom_namespace(self):                          # Test store with namespace
        with self.html_graph_client as _:
            url       = "https://example.com/custom-ns-test"
            html      = "<html><body>Custom namespace test</body></html>"
            namespace = "test-namespace"

            result = _.store_html(url=url, html=html, namespace=namespace)

            assert result is not None



