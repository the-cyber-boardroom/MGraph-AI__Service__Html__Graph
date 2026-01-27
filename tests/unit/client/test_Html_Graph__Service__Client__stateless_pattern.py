# ═══════════════════════════════════════════════════════════════════════════════
# Stateless Pattern Tests
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from mgraph_ai_service_html_graph.client.Html_Graph__Service__Client                                    import Html_Graph__Service__Client
from mgraph_ai_service_html_graph.client.register_html_graph_service                                    import register_html_graph_service__in_memory
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                       import fast_api__service__registry
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode     import Enum__Fast_API__Service__Registry__Client__Mode




class test_Html_Graph__Service__Client__stateless_pattern(TestCase):

    @classmethod
    def setUpClass(cls):
        fast_api__service__registry.configs__save()
        fast_api__service__registry.clear()
        register_html_graph_service__in_memory()

    @classmethod
    def tearDownClass(cls):
        fast_api__service__registry.configs__restore()

    def test__multiple_client_instances__all_work(self):                        # Multiple clients all work
        client_1 = Html_Graph__Service__Client()
        client_2 = Html_Graph__Service__Client()
        client_3 = Html_Graph__Service__Client()

        assert client_1.health() is True
        assert client_2.health() is True
        assert client_3.health() is True

    def test__multiple_client_instances__same_config(self):                     # All get same config from registry
        client_1 = Html_Graph__Service__Client()
        client_2 = Html_Graph__Service__Client()

        config_1 = client_1.requests().config()
        config_2 = client_2.requests().config()

        assert config_1 is config_2                                             # Same config object

    def test__client_created_inline(self):                                      # Client can be created on the fly
        def some_business_logic():
            client = Html_Graph__Service__Client()                              # Create inline
            return client.health()

        result = some_business_logic()
        assert result is True