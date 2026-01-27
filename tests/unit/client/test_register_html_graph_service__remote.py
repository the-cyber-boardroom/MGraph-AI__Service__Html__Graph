# ═══════════════════════════════════════════════════════════════════════════════
# register_html_graph_service__remote Tests
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from mgraph_ai_service_html_graph.client.Html_Graph__Service__Client                                    import Html_Graph__Service__Client
from mgraph_ai_service_html_graph.client.register_html_graph_service                                    import register_html_graph_service__remote
from mgraph_ai_service_html_graph.schemas.client.consts__html_graph_client                              import ENV_VAR__HTML_GRAPH__BASE_URL
from mgraph_ai_service_html_graph.schemas.client.consts__html_graph_client                              import ENV_VAR__HTML_GRAPH__KEY_NAME
from mgraph_ai_service_html_graph.schemas.client.consts__html_graph_client                              import ENV_VAR__HTML_GRAPH__KEY_VALUE
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                       import Fast_API__Service__Registry
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode     import Enum__Fast_API__Service__Registry__Client__Mode
from osbot_utils.utils.Env                                                                              import set_env, del_env


class test_register_html_graph_service__remote(TestCase):

    def test__registers_with_explicit_values(self):                             # Test explicit registration
        registry = Fast_API__Service__Registry()

        register_html_graph_service__remote(registry      = registry                        ,
                                            base_url      = 'https://html-graph.example.com',
                                            api_key_name  = 'X-API-KEY'                     ,
                                            api_key_value = 'secret-123'                    )

        assert registry.is_registered(Html_Graph__Service__Client) is True

    def test__config__mode_is_remote(self):                                     # Test mode is REMOTE
        registry = Fast_API__Service__Registry()

        register_html_graph_service__remote(registry = registry                        ,
                                            base_url = 'https://html-graph.example.com')

        config = registry.config(Html_Graph__Service__Client)
        assert config.mode == Enum__Fast_API__Service__Registry__Client__Mode.REMOTE

    def test__config__has_base_url(self):                                       # Test base_url is set
        registry = Fast_API__Service__Registry()

        register_html_graph_service__remote(registry = registry                        ,
                                            base_url = 'https://html-graph.example.com')

        config = registry.config(Html_Graph__Service__Client)
        assert str(config.base_url) == 'https://html-graph.example.com'

    def test__raises_without_base_url(self):                                    # Test error without base_url
        registry = Fast_API__Service__Registry()

        with self.assertRaises(ValueError) as context:
            register_html_graph_service__remote(registry=registry)

        assert "REMOTE mode requires base_url" in str(context.exception)

    def test__reads_from_env_vars(self):                                        # Test env var fallback
        registry = Fast_API__Service__Registry()

        set_env(ENV_VAR__HTML_GRAPH__BASE_URL , 'https://env.html-graph.example.com')
        set_env(ENV_VAR__HTML_GRAPH__KEY_NAME , 'X-ENV-KEY'                         )
        set_env(ENV_VAR__HTML_GRAPH__KEY_VALUE, 'env-secret'                        )

        try:
            register_html_graph_service__remote(registry=registry)

            config = registry.config(Html_Graph__Service__Client)
            assert str(config.base_url)      == 'https://env.html-graph.example.com'
            assert str(config.api_key_name)  == 'x-env-key'
            assert str(config.api_key_value) == 'env-secret'
        finally:
            del_env(ENV_VAR__HTML_GRAPH__BASE_URL )
            del_env(ENV_VAR__HTML_GRAPH__KEY_NAME )
            del_env(ENV_VAR__HTML_GRAPH__KEY_VALUE)