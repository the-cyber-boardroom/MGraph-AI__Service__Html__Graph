from unittest import TestCase
from osbot_utils.type_safe.Type_Safe                             import Type_Safe
from osbot_utils.utils.Objects                                   import base_types
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph import Html_MGraph
from tests.unit.service.html_graph.test_Html_MGraph              import SIMPLE_HTML_DICT


class test_Html_MGraph__Screenshot(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.html_mgraph = Html_MGraph.from_html_dict(SIMPLE_HTML_DICT)

    def test__setUpClass(self):
        with self.html_mgraph as _:
            assert type(_) is Html_MGraph
            assert base_types(_) == [Type_Safe, object]