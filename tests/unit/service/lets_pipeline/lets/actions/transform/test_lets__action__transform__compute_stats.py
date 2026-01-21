# ═══════════════════════════════════════════════════════════════════════════════
# test_lets__action__transform__compute_stats - Tests for compute stats action
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                                           import TestCase
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.actions.transform.lets__action__transform__compute_stats   import lets__action__transform__compute_stats
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_extract.Schema__LETS__Extract__Output         import Schema__LETS__Extract__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_transform.Schema__LETS__Transform__Output     import Schema__LETS__Transform__Output
from mgraph_ai_service_html_graph.utils.testing.Html_Generator__For_Tests                                               import Html_Generator__For_Tests
from osbot_utils.helpers.flows.Flow                                                                                     import Flow
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                                               import Safe_Str__Html


class test_lets__action__transform__compute_stats(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.html_gen = Html_Generator__For_Tests()

    # ═══════════════════════════════════════════════════════════════════════════
    # Basic Functionality Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_compute_stats__minimal_html(self):
        html       = self.html_gen.minimal_html()
        input_data = Schema__LETS__Extract__Output(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__transform__compute_stats(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert type(result)       is Schema__LETS__Transform__Output
        assert result.html        == html
        assert result.stats       is not None
        assert type(result.stats) is dict

    def test_compute_stats__has_char_count(self):
        html       = self.html_gen.minimal_html()
        input_data = Schema__LETS__Extract__Output(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__transform__compute_stats(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert 'char_count'              in result.stats
        assert result.stats['char_count'] == len(str(html))

    def test_compute_stats__has_tag_count(self):
        html       = self.html_gen.minimal_html()
        input_data = Schema__LETS__Extract__Output(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__transform__compute_stats(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert 'tag_count'              in result.stats
        assert result.stats['tag_count'] == str(html).count('<')

    def test_compute_stats__has_line_count(self):
        html       = self.html_gen.simple_html()
        input_data = Schema__LETS__Extract__Output(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__transform__compute_stats(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert 'line_count'              in result.stats
        assert result.stats['line_count'] == str(html).count('\n') + 1

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Accuracy Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_compute_stats__single_line(self):
        html       = Safe_Str__Html('<html><body>test</body></html>')
        input_data = Schema__LETS__Extract__Output(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__transform__compute_stats(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert result.stats['line_count'] == 1
        assert result.stats['tag_count']  == 4
        assert result.stats['char_count'] == 30

    def test_compute_stats__nested_html(self):
        html       = self.html_gen.nested_html()
        input_data = Schema__LETS__Extract__Output(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__transform__compute_stats(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert result.stats['tag_count']  > 5
        assert result.stats['line_count'] > 1

    def test_compute_stats__with_paragraphs(self):
        html       = self.html_gen.html_with_paragraphs(count=10)
        input_data = Schema__LETS__Extract__Output(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__transform__compute_stats(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert result.stats['tag_count'] >= 22

    # ═══════════════════════════════════════════════════════════════════════════
    # Edge Case Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_compute_stats__empty_html(self):
        html       = Safe_Str__Html('')
        input_data = Schema__LETS__Extract__Output(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__transform__compute_stats(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert result.stats['char_count'] == 0
        assert result.stats['tag_count']  == 0
        assert result.stats['line_count'] == 1

    def test_compute_stats__none_html(self):
        input_data = Schema__LETS__Extract__Output(html=None)

        with Flow() as flow:
            flow.setup(lambda: lets__action__transform__compute_stats(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert result.html  is None
        assert result.stats == {'char_count': 0, 'tag_count': 0, 'line_count': 1}

    # ═══════════════════════════════════════════════════════════════════════════
    # Type Safety Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_compute_stats__preserves_html_type(self):
        html       = self.html_gen.minimal_html()
        input_data = Schema__LETS__Extract__Output(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__transform__compute_stats(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert type(result.html) is Safe_Str__Html

    def test_compute_stats__output_type(self):
        input_data = Schema__LETS__Extract__Output(html=self.html_gen.minimal_html())

        with Flow() as flow:
            flow.setup(lambda: lets__action__transform__compute_stats(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert type(result) is Schema__LETS__Transform__Output