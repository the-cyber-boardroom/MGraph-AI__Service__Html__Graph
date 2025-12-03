from unittest                                                                 import TestCase
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph              import Html_MGraph
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Screenshot import Html_MGraph__Screenshot
from tests.unit.service.html_graph.test_Html_MGraph                           import SIMPLE_HTML_DICT


class test_Html_MGraph__Screenshot__Setup(TestCase):                                        # Tests that require setup() to be called

    @classmethod
    def setUpClass(cls):
        cls.html_mgraph = Html_MGraph.from_html_dict(SIMPLE_HTML_DICT)

    def test_setup__creates_screenshot(self):                                               # Test setup creates screenshot instance
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph.mgraph) as _:
            _.setup()
            assert _.screenshot is not None

    def test_setup__returns_self(self):                                                     # Test setup returns self for chaining
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph.mgraph) as _:
            result = _.setup()
            assert result is _

    def test_setup__without_mgraph_raises(self):                                            # Test setup raises without mgraph
        with Html_MGraph__Screenshot(mgraph=None) as _:
            with self.assertRaises(ValueError) as context:
                _.setup()
            assert 'mgraph must be provided' in str(context.exception)
