from unittest                                                                                       import TestCase
from fastapi                                                                                        import FastAPI
from mgraph_ai_service_html_graph.schemas.client.consts__html_graph_client                          import DEFAULT__HTML_GRAPH__NAMESPACE, DEFAULT__HTML_GRAPH__TIMEOUT
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode import Enum__Fast_API__Service__Registry__Client__Mode
from osbot_utils.utils.Objects                                                                      import base_classes
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from mgraph_ai_service_html_graph.client.Html_Graph__Service__Client__Config                        import Html_Graph__Service__Client__Config


class test_Html_Graph__Service__Client__Config(TestCase):

    def test__init__(self):                                                     # Test config auto-initialization
        with Html_Graph__Service__Client__Config() as _:
            assert type(_)         is Html_Graph__Service__Client__Config
            assert base_classes(_) == [Type_Safe, object]
            assert _.mode          == Enum__Fast_API__Service__Registry__Client__Mode.REMOTE                 # Default mode
            assert _.fast_api_app  is None
            assert _.namespace     == DEFAULT__HTML_GRAPH__NAMESPACE
            assert _.timeout       == DEFAULT__HTML_GRAPH__TIMEOUT

    def test__config__in_memory_mode(self):                                     # Test config with in-memory app
        fastapi = FastAPI()
        config   = Html_Graph__Service__Client__Config(fast_api_app = fastapi                      ,
                                                       mode         = Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY )

        assert config.fast_api_app is fastapi
        assert config.mode         == Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY
