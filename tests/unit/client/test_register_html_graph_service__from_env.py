# ═══════════════════════════════════════════════════════════════════════════════
# register_html_graph_service__from_env Tests
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from mgraph_ai_service_html_graph.client.Html_Graph__Service__Client                                    import Html_Graph__Service__Client
from mgraph_ai_service_html_graph.client.register_html_graph_service                                    import register_html_graph_service__from_env
from mgraph_ai_service_html_graph.schemas.client.consts__html_graph_client                              import ENV_VAR__HTML_GRAPH__BASE_URL
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                       import Fast_API__Service__Registry
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode     import Enum__Fast_API__Service__Registry__Client__Mode
from osbot_utils.utils.Env                                                                              import set_env, del_env


class test_register_html_graph_service__from_env(TestCase):

    def test__uses_in_memory_when_no_url(self):                                 # Test defaults to IN_MEMORY
        registry = Fast_API__Service__Registry()

        del_env(ENV_VAR__HTML_GRAPH__BASE_URL)

        register_html_graph_service__from_env(registry=registry)

        config = registry.config(Html_Graph__Service__Client)
        assert config.mode == Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY

    def test__uses_remote_when_url_set(self):                                   # Test uses REMOTE when URL set
        registry = Fast_API__Service__Registry()

        set_env(ENV_VAR__HTML_GRAPH__BASE_URL, 'https://auto.html-graph.example.com')

        try:
            register_html_graph_service__from_env(registry=registry)

            config = registry.config(Html_Graph__Service__Client)
            assert config.mode          == Enum__Fast_API__Service__Registry__Client__Mode.REMOTE
            assert str(config.base_url) == 'https://auto.html-graph.example.com'
        finally:
            del_env(ENV_VAR__HTML_GRAPH__BASE_URL)