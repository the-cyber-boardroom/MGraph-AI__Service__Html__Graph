# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Html_Graph__Service__Client
# Validates dual-mode client functionality (IN_MEMORY and REMOTE)
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                       import TestCase
from fastapi                                                                                        import FastAPI
from mgraph_ai_service_html_graph.client.Html_Graph__Service__Client                                import Html_Graph__Service__Client
from mgraph_ai_service_html_graph.client.Html_Graph__Service__Client__Config                        import Html_Graph__Service__Client__Config
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode import Enum__Fast_API__Service__Registry__Client__Mode


class test_Html_Graph__Service__Client(TestCase):

    def test__init__(self):                                                     # Test client auto-initialization
        with Html_Graph__Service__Client() as _:
            assert type(_)        is Html_Graph__Service__Client
            assert type(_.config) is Html_Graph__Service__Client__Config

    def test__url_to_cache_key(self):                                           # Test URL conversion
        with Html_Graph__Service__Client() as _:
            assert _.url_to_cache_key("https://example.com")           == "example.com/root"
            assert _.url_to_cache_key("https://example.com/path")      == "example.com/path"
            assert _.url_to_cache_key("https://example.com/path/sub")  == "example.com/path/sub"
            assert _.url_to_cache_key("https://sub.example.com/page")  == "sub.example.com/page"

    def test__client__remote_mode(self):                                        # Test client in remote mode (default)
        config = Html_Graph__Service__Client__Config()
        client = Html_Graph__Service__Client(config=config)

        assert client.config.mode         == Enum__Fast_API__Service__Registry__Client__Mode.REMOTE
        assert client.config.fast_api_app is None

    def test__client__in_memory_mode(self):                                     # Test client in in-memory mode
        fastapi = FastAPI()
        config   = Html_Graph__Service__Client__Config(fast_api_app = fastapi                     ,
                                                       mode         = Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY )
        client   = Html_Graph__Service__Client(config=config)

        assert client.config.mode         == Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY
        assert client.config.fast_api_app is fastapi
