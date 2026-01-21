# ═══════════════════════════════════════════════════════════════════════════════
# test_lets__action__load__passthrough - Tests for load passthrough action
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                               import TestCase
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.actions.load.lets__action__load__passthrough   import lets__action__load__passthrough
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_load.Schema__LETS__Load__Input    import Schema__LETS__Load__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_load.Schema__LETS__Load__Output   import Schema__LETS__Load__Output
from mgraph_ai_service_html_graph.utils.testing.Html_Generator__For_Tests                                   import Html_Generator__For_Tests
from osbot_utils.helpers.flows.Flow                                                                         import Flow
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                                   import Safe_Str__Html


class test_lets__action__load__passthrough(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.html_gen = Html_Generator__For_Tests()

    # ═══════════════════════════════════════════════════════════════════════════
    # Basic Functionality Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_passthrough__minimal_html(self):
        html       = self.html_gen.minimal_html()
        input_data = Schema__LETS__Load__Input(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__load__passthrough(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert type(result)      is Schema__LETS__Load__Output
        assert type(result.html) is Safe_Str__Html
        assert result.html       == html

    def test_passthrough__simple_html(self):
        html       = self.html_gen.simple_html()
        input_data = Schema__LETS__Load__Input(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__load__passthrough(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert result.html                       == html
        assert '<title>Test Page</title>'        in str(result.html)

    def test_passthrough__nested_html(self):
        html       = self.html_gen.nested_html()
        input_data = Schema__LETS__Load__Input(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__load__passthrough(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert result.html            == html
        assert 'class="container"'    in str(result.html)

    # ═══════════════════════════════════════════════════════════════════════════
    # Edge Case Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_passthrough__empty_html(self):
        html       = Safe_Str__Html('<html></html>')
        input_data = Schema__LETS__Load__Input(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__load__passthrough(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert result.html == html

    def test_passthrough__preserves_whitespace(self):
        html       = Safe_Str__Html('<html>\n  <body>\n    <p>Test</p>\n  </body>\n</html>')
        input_data = Schema__LETS__Load__Input(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__load__passthrough(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert '\n' in str(result.html)

    def test_passthrough__preserves_special_chars(self):
        html       = Safe_Str__Html('<html><body>&amp; &lt; &gt; &quot;</body></html>')
        input_data = Schema__LETS__Load__Input(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__load__passthrough(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert '&amp;' in str(result.html)

    # ═══════════════════════════════════════════════════════════════════════════
    # Type Safety Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_passthrough__output_type(self):
        input_data = Schema__LETS__Load__Input(html=self.html_gen.minimal_html())

        with Flow() as flow:
            flow.setup(lambda: lets__action__load__passthrough(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert type(result)      is Schema__LETS__Load__Output
        assert type(result.html) is Safe_Str__Html

    def test_passthrough__none_input(self):
        input_data = Schema__LETS__Load__Input(html=None)

        with Flow() as flow:
            flow.setup(lambda: lets__action__load__passthrough(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert result.html is None