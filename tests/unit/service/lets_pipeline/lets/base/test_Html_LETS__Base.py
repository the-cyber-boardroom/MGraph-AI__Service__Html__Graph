# ═══════════════════════════════════════════════════════════════════════════════
# test_Html_LETS__Base - Tests for base LETS class
# Tests the abstract LETS pattern and configuration
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                            import TestCase
from osbot_utils.type_safe.Type_Safe                                                                     import Type_Safe
from osbot_utils.utils.Objects                                                                           import base_types
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.base.Html_LETS__Base                        import Html_LETS__Base
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Config                import Schema__LETS__Config
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_load.Schema__LETS__Load__Input import Schema__LETS__Load__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.safe_str.Safe_Str__LETS__Name       import Safe_Str__LETS__Name


class test_Html_LETS__Base(TestCase):

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with Html_LETS__Base() as _:
            assert type(_)       is Html_LETS__Base
            assert base_types(_) == [Type_Safe, object]

    def test__init____config(self):
        config = Schema__LETS__Config(name        = 'test-lets'  ,
                                      description = 'Test config')
        with Html_LETS__Base(config=config) as _:
            assert _.config      is config
            assert _.config.name == 'test-lets'


    def test__init____document_is_none(self):
        with Html_LETS__Base() as _:
            assert _.document is None

    def test__init____flow_is_none(self):
        with Html_LETS__Base() as _:
            assert _.flow is None

    def test__init____output_is_none(self):
        with Html_LETS__Base() as _:
            assert _.output is None

    # ═══════════════════════════════════════════════════════════════════════════
    # Setup Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_setup__raises_not_implemented(self):
        with Html_LETS__Base() as _:
            with self.assertRaises(NotImplementedError) as context:
                _.setup()
            assert 'Subclasses must implement setup()' in str(context.exception)

    # ═══════════════════════════════════════════════════════════════════════════
    # Validate Actions Tests
    # ═══════════════════════════════════════════════════════════════════════════




    def test_validate_actions__all_wired(self):
        with Html_LETS__Base() as _:
            _.load      = lambda x: x
            _.extract   = lambda x: x
            _.transform = lambda x: x
            _.save      = lambda x: x
            _.validate_actions()                                                 # Should not raise

    # ═══════════════════════════════════════════════════════════════════════════
    # Observability Tests (before execute)
    # ═══════════════════════════════════════════════════════════════════════════

    def test_durations__before_execute(self):
        with Html_LETS__Base() as _:
            assert _.durations() == {}

    def test_captured_logs__before_execute(self):
        with Html_LETS__Base() as _:
            assert _.captured_logs() == []

    def test_flow_data__before_execute(self):
        with Html_LETS__Base() as _:
            assert _.flow_data() == {}

    # ═══════════════════════════════════════════════════════════════════════════
    # Config Schema Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_config_schema__empty(self):
        config = Schema__LETS__Config()
        assert config.name        == ''
        assert config.description == ''

    def test_config_schema__with_values(self):
        config = Schema__LETS__Config(name           = 'my-lets'             ,
                                      description    = 'My LETS description' ,
                                      schema__input  = None                  ,
                                      schema__output = None                  )
        assert config.name        == 'my-lets'
        assert config.description == 'My LETS description'

    def test_config_schema__safe_str_name(self):
        config = Schema__LETS__Config(name='valid-name-123')
        assert type(config.name) is Safe_Str__LETS__Name
        assert str(config.name)  == 'valid-name-123'