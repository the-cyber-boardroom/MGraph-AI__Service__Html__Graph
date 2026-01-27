from unittest                                                                                           import TestCase
from mgraph_ai_service_html_graph.client.Html_Graph__Service__Client                                    import Html_Graph__Service__Client
from mgraph_ai_service_html_graph.client.Html_Graph__Service__Client__Requests                          import Html_Graph__Service__Client__Requests
from osbot_fast_api.services.registry.Fast_API__Client__Requests                                        import Fast_API__Client__Requests
from osbot_utils.utils.Objects                                                                          import base_classes
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe


class test_Html_Graph__Service__Client__Requests(TestCase):

    def test__init__(self):                                                     # Test auto-initialization
        with Html_Graph__Service__Client__Requests() as _:
            assert type(_)         is Html_Graph__Service__Client__Requests
            assert base_classes(_) == [Fast_API__Client__Requests, Type_Safe, object]

    def test__inherits_from_Fast_API__Client__Requests(self):                   # Test inheritance
        requests = Html_Graph__Service__Client__Requests()
        assert isinstance(requests, Fast_API__Client__Requests)

    def test__service_type__default_is_none(self):                              # Test default service_type
        with Html_Graph__Service__Client__Requests() as _:
            assert _.service_type is None

    def test__config__raises_when_not_registered(self):                         # Test error when not registered
        requests              = Html_Graph__Service__Client__Requests()
        requests.service_type = Html_Graph__Service__Client

        with self.assertRaises(ValueError) as context:
            requests.config()

        assert "Html_Graph__Service__Client not registered" in str(context.exception)