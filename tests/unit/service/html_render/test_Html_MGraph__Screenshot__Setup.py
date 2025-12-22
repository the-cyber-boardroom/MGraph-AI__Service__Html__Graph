from unittest                                                                 import TestCase
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph             import Html_MGraph
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Screenshot import Html_MGraph__Screenshot


class test_Html_MGraph__Screenshot__Setup(TestCase):                                        # Tests that require setup() to be called

    @classmethod
    def setUpClass(cls):
        cls.simple_html  = '<div class="main" id="content">Hello World</div>'
        cls.html_mgraph  = Html_MGraph.from_html(cls.simple_html)

    def test_setup__creates_screenshot(self):                                               # Test setup creates screenshot instance
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            _.setup()
            assert _.screenshot is not None

    def test_setup__returns_self(self):                                                     # Test setup returns self for chaining
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            result = _.setup()
            assert result is _

    def test_setup__without_html_mgraph_raises(self):                                       # Test setup raises without html_mgraph
        with Html_MGraph__Screenshot(html_mgraph=None) as _:
            with self.assertRaises(ValueError) as context:
                _.setup()
            assert 'html_mgraph must be provided' in str(context.exception)