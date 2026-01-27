# ═══════════════════════════════════════════════════════════════════════════════
# test_Html_Graph__Service__Client
# Tests for the stateless Html Graph service client
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from mgraph_ai_service_html_graph.client.Html_Graph__Service__Client                                    import Html_Graph__Service__Client
from mgraph_ai_service_html_graph.client.Html_Graph__Service__Client__Requests                          import Html_Graph__Service__Client__Requests
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url import Safe_Str__Url
from osbot_utils.utils.Objects                                                                          import base_classes
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe


class test_Html_Graph__Service__Client(TestCase):

    def test__init__(self):                                                     # Test auto-initialization
        with Html_Graph__Service__Client() as _:
            assert type(_)         is Html_Graph__Service__Client
            assert base_classes(_) == [Type_Safe, object]

    def test__no_config_attribute(self):                                        # Client is stateless - no config
        client = Html_Graph__Service__Client()
        assert hasattr(client, 'config') is False

    def test__requests__returns_transport(self):                                # Test requests creates transport
        with Html_Graph__Service__Client() as _:
            requests = _.requests()
            assert type(requests) is Html_Graph__Service__Client__Requests

    def test__requests__sets_service_type(self):                                # Test service_type is set for registry lookup
        with Html_Graph__Service__Client() as _:
            requests = _.requests()
            assert requests.service_type is Html_Graph__Service__Client

    def test__requests__cached_on_self(self):                                   # Test requests is cached
        with Html_Graph__Service__Client() as _:
            requests_1 = _.requests()
            requests_2 = _.requests()
            assert requests_1 is requests_2

    def test__url_to_cache_key(self):                                           # Test URL conversion
        with Html_Graph__Service__Client() as _:
            assert _.url_to_cache_key("https://example.com")          == "example.com/root"
            assert _.url_to_cache_key("https://example.com/path")     == "example.com/path"
            assert _.url_to_cache_key("https://example.com/path/sub") == "example.com/path/sub"
            assert _.url_to_cache_key("https://sub.example.com/page") == "sub.example.com/page"

