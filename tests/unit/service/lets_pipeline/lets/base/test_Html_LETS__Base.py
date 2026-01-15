# ═══════════════════════════════════════════════════════════════════════════════
# test_Html_LETS__Base - Tests for base LETS class
# Tests the abstract LETS pattern and configuration
# ═══════════════════════════════════════════════════════════════════════════════
from unittest                                                                               import TestCase
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.base.Html_LETS__Base           import Html_LETS__Base
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.safe_str.Safe_Str__LETS__Name  import Safe_Str__LETS__Name
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Config   import Schema__LETS__Config
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Input    import Schema__LETS__Extract__Input
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.utils.Objects                                                              import base_types


class test_Html_LETS__Base(TestCase):

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test auto-initialization
        with Html_LETS__Base() as _:
            assert type(_)       is Html_LETS__Base
            assert base_types(_) == [Type_Safe, object]

    def test__init____config(self):                                              # Test config initialization
        config = Schema__LETS__Config(name        = 'test-lets'  ,
                                      description = 'Test config')
        with Html_LETS__Base(config=config) as _:
            assert _.config           is config
            assert _.config.name      == 'test-lets'

    # ═══════════════════════════════════════════════════════════════════════════
    # Abstract Method Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_load__raises_not_implemented(self):                                 # Test load is abstract
        with Html_LETS__Base() as _:
            with self.assertRaises(NotImplementedError):
                _.load(load_input=None)

    def test_transform__raises_not_implemented(self):                            # Test transform is abstract
        with Html_LETS__Base() as _:
            with self.assertRaises(NotImplementedError):
                _.transform(transform_input=None)

    def test_save__raises_not_implemented(self):                                 # Test save is abstract
        with Html_LETS__Base() as _:
            with self.assertRaises(NotImplementedError):
                _.save(save_input=None)

    def test_extract__default_passthrough(self):                                 # Test extract passes through
        with Html_LETS__Base() as _:
            with self.assertRaises(NotImplementedError):
                _.extract(extract_input=Schema__LETS__Extract__Input())


    # ═══════════════════════════════════════════════════════════════════════════
    # Config Schema Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_config_schema__empty(self):                                         # Test empty config
        config = Schema__LETS__Config()
        assert config.name        == ''
        assert config.description == ''

    def test_config_schema__with_values(self):                                   # Test config with values
        config = Schema__LETS__Config(name           = 'my-lets'             ,
                                      description    = 'My LETS description' ,
                                      schema__input  = None                  ,
                                      schema__output = None                  )
        assert config.name        == 'my-lets'
        assert config.description == 'My LETS description'

    def test_config_schema__safe_str_name(self):                                 # Test name uses Safe_Str
        config = Schema__LETS__Config(name='valid-name-123')
        assert type(config.name) is Safe_Str__LETS__Name
        assert str(config.name)  == 'valid-name-123'
