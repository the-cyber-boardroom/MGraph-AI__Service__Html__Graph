# ═══════════════════════════════════════════════════════════════════════════════
# test_lets__action__save__passthrough - Tests for save passthrough (no-op) action
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                                       import TestCase
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.actions.save.lets__action__save__passthrough            import lets__action__save__passthrough
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_save.Schema__LETS__Save__Output            import Schema__LETS__Save__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_transform.Schema__LETS__Transform__Output  import Schema__LETS__Transform__Output
from mgraph_ai_service_html_graph.utils.testing.Html_Generator__For_Tests                                            import Html_Generator__For_Tests
from osbot_utils.helpers.flows.Flow                                                                                  import Flow


class test_lets__action__save__passthrough(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.html_gen = Html_Generator__For_Tests()

    # ═══════════════════════════════════════════════════════════════════════════
    # Basic Functionality Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_passthrough__returns_success(self):
        html       = self.html_gen.minimal_html()
        input_data = Schema__LETS__Transform__Output(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__save__passthrough(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert type(result)   is Schema__LETS__Save__Output
        assert result.success is True

    def test_passthrough__not_cached(self):
        html       = self.html_gen.minimal_html()
        input_data = Schema__LETS__Transform__Output(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__save__passthrough(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert result.cached is False

    def test_passthrough__no_layer(self):
        html       = self.html_gen.minimal_html()
        input_data = Schema__LETS__Transform__Output(html=html)

        with Flow() as flow:
            flow.setup(lambda: lets__action__save__passthrough(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert result.layer   is None
        assert result.file_id is None

    # ═══════════════════════════════════════════════════════════════════════════
    # Edge Case Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_passthrough__with_stats(self):
        html       = self.html_gen.minimal_html()
        stats      = {'char_count': 100, 'tag_count': 5}
        input_data = Schema__LETS__Transform__Output(html=html, stats=stats)

        with Flow() as flow:
            flow.setup(lambda: lets__action__save__passthrough(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert result.success is True

    def test_passthrough__none_html(self):
        input_data = Schema__LETS__Transform__Output(html=None)

        with Flow() as flow:
            flow.setup(lambda: lets__action__save__passthrough(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert result.success is True

    # ═══════════════════════════════════════════════════════════════════════════
    # Type Safety Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_passthrough__input_type(self):
        input_data = Schema__LETS__Transform__Output(html=self.html_gen.minimal_html())

        with Flow() as flow:
            flow.setup(lambda: lets__action__save__passthrough(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert type(result) is Schema__LETS__Save__Output

    def test_passthrough__output_fields(self):
        input_data = Schema__LETS__Transform__Output(html=self.html_gen.minimal_html())

        with Flow() as flow:
            flow.setup(lambda: lets__action__save__passthrough(input_data))
            flow.execute()
            result = flow.flow_return_value

        assert hasattr(result, 'success')
        assert hasattr(result, 'cached')
        assert hasattr(result, 'layer')
        assert hasattr(result, 'file_id')