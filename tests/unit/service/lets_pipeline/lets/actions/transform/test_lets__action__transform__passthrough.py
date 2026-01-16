# ═══════════════════════════════════════════════════════════════════════════════
# test_lets__action__transform__passthrough - Tests for transform passthrough action
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                                           import TestCase
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.actions.transform.lets__action__transform__passthrough     import lets__action__transform__passthrough
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_extract.Schema__LETS__Extract__Output         import Schema__LETS__Extract__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_transform.Schema__LETS__Transform__Output     import Schema__LETS__Transform__Output
from mgraph_ai_service_html_graph.utils.testing.Html_Generator__For_Tests                                               import Html_Generator__For_Tests
from osbot_utils.helpers.flows.Flow                                                                                     import Flow
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                                               import Safe_Str__Html


class test_lets__action__transform__passthrough(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.html_gen = Html_Generator__For_Tests()

    # ═══════════════════════════════════════════════════════════════════════════
    # Basic Functionality Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_passthrough__minimal_html(self):
        html       = self.html_gen.minimal_html()
        input_data = Schema__LETS__Extract__Output(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__transform__passthrough(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert type(result)      is Schema__LETS__Transform__Output
        assert type(result.html) is Safe_Str__Html
        assert result.html       == html

    def test_passthrough__simple_html(self):
        html       = self.html_gen.simple_html()
        input_data = Schema__LETS__Extract__Output(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__transform__passthrough(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert result.html == html

    # ═══════════════════════════════════════════════════════════════════════════
    # Type Safety Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_passthrough__input_is_extract_output(self):
        html       = self.html_gen.minimal_html()
        input_data = Schema__LETS__Extract__Output(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__transform__passthrough(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert type(result) is Schema__LETS__Transform__Output

    def test_passthrough__no_stats(self):
        html       = self.html_gen.minimal_html()
        input_data = Schema__LETS__Extract__Output(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__transform__passthrough(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert result.stats is None

    def test_passthrough__none_input(self):
        input_data = Schema__LETS__Extract__Output(html=None)

        with Flow() as flow:
            flow.setup(lambda: lets__action__transform__passthrough(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert result.html is None