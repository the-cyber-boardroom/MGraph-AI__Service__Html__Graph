# ═══════════════════════════════════════════════════════════════════════════════
# test_register_html_graph_service
# Tests for Html Graph service registration helpers
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from mgraph_ai_service_html_graph.client.Html_Graph__Service__Client                                    import Html_Graph__Service__Client
from mgraph_ai_service_html_graph.client.register_html_graph_service                                    import register_html_graph_service__in_memory
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                       import Fast_API__Service__Registry
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode     import Enum__Fast_API__Service__Registry__Client__Mode


# ═══════════════════════════════════════════════════════════════════════════════
# register_html_graph_service__in_memory Tests
# ═══════════════════════════════════════════════════════════════════════════════

class test_register_html_graph_service__in_memory(TestCase):

    def test__registers_config(self):                                           # Test config is registered
        registry = Fast_API__Service__Registry()

        register_html_graph_service__in_memory(registry=registry)

        assert registry.is_registered(Html_Graph__Service__Client) is True

    def test__config__mode_is_in_memory(self):                                  # Test mode is IN_MEMORY
        registry = Fast_API__Service__Registry()

        register_html_graph_service__in_memory(registry=registry)

        config = registry.config(Html_Graph__Service__Client)
        assert config.mode == Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY

    def test__config__has_fast_api_app(self):                                   # Test config has FastAPI app
        registry = Fast_API__Service__Registry()

        register_html_graph_service__in_memory(registry=registry)

        config = registry.config(Html_Graph__Service__Client)
        assert config.fast_api_app is not None

    def test__config__has_fast_api_wrapper(self):                               # Test config has wrapper for test access
        registry = Fast_API__Service__Registry()

        register_html_graph_service__in_memory(registry=registry)

        config = registry.config(Html_Graph__Service__Client)
        assert config.fast_api is not None

    def test__return_client(self):                                              # Test return_client option
        registry = Fast_API__Service__Registry()

        client = register_html_graph_service__in_memory(registry=registry, return_client=True)

        assert type(client) is Html_Graph__Service__Client





