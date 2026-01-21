# ═══════════════════════════════════════════════════════════════════════════════
# test_Html_LETS__Html__To__Dict - Tests for HTML to dictionary LETS
# Tests parsing HTML into structured dictionary
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                 import TestCase
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.base.Html_LETS__Base             import Html_LETS__Base
from osbot_utils.type_safe.Type_Safe                                                          import Type_Safe
from osbot_utils.utils.Objects                                                                import base_types
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                     import Safe_Str__Html
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.steps.Html_LETS__Html__To__Dict  import Schema__Html_To_Dict__Load__Input, Schema__Html_To_Dict__Load__Output, Schema__Html_To_Dict__Transform__Input, Schema__Html_To_Dict__Transform__Output, Schema__Html_Dict, Schema__Html_To_Dict__Save__Input, Html_LETS__Html__To__Dict
from mgraph_ai_service_html_graph.utils.testing.Html_Generator__For_Tests                     import Html_Generator__For_Tests


class test_Html_LETS__Html__To__Dict(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup
        cls.html_generator = Html_Generator__For_Tests()
        cls.sample_html    = cls.html_generator.simple_html()

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test auto-initialization
        with Html_LETS__Html__To__Dict() as _:
            assert type(_)       is Html_LETS__Html__To__Dict
            assert base_types(_) == [Html_LETS__Base, Type_Safe, object]

    def test__init____config_is_none(self):                                      # Test config starts None
        with Html_LETS__Html__To__Dict() as _:
            assert _.config is None

    # ═══════════════════════════════════════════════════════════════════════════
    # Setup Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_setup(self):                                                        # Test setup initializes config
        with Html_LETS__Html__To__Dict() as _:
            result = _.setup()

            assert result             is _
            assert _.config           is not None
            assert _.config.name      == 'html-to-dict'
            assert 'dictionary'       in _.config.description

    def test_setup__returns_self(self):                                          # Test chaining
        lets = Html_LETS__Html__To__Dict().setup()
        assert type(lets)        is Html_LETS__Html__To__Dict
        assert lets.config.name  == 'html-to-dict'

    # ═══════════════════════════════════════════════════════════════════════════
    # Load Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_load(self):                                                         # Test load returns HTML
        with Html_LETS__Html__To__Dict().setup() as _:
            load_input  = Schema__Html_To_Dict__Load__Input(html=self.sample_html)
            load_output = _.load(load_input=load_input)

            assert type(load_output)      is Schema__Html_To_Dict__Load__Output
            assert type(load_output.html) is Safe_Str__Html
            assert load_output.html       == self.sample_html

    # ═══════════════════════════════════════════════════════════════════════════
    # Transform Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_transform(self):                                                    # Test transform creates dict
        with Html_LETS__Html__To__Dict().setup() as _:
            transform_input  = Schema__Html_To_Dict__Transform__Input(html=self.sample_html)
            transform_output = _.transform(transform_input=transform_input)

            assert type(transform_output)          is Schema__Html_To_Dict__Transform__Output
            assert type(transform_output.html_dict) is Schema__Html_Dict
            assert transform_output.html_dict.html_dict is not None

    def test_transform__output_has_structure(self):                              # Test output dict structure
        with Html_LETS__Html__To__Dict().setup() as _:
            transform_input  = Schema__Html_To_Dict__Transform__Input(html=self.sample_html)
            transform_output = _.transform(transform_input=transform_input)

            html_dict = transform_output.html_dict.html_dict
            assert 'tag'     in html_dict                                        # Has tag key
            assert 'node_id' in html_dict                                        # Has node_id key

    # ═══════════════════════════════════════════════════════════════════════════
    # Save Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_save(self):                                                         # Test save returns success
        with Html_LETS__Html__To__Dict().setup() as _:
            html_dict   = Schema__Html_Dict(html_dict={'tag': 'html', 'children': []})
            save_input  = Schema__Html_To_Dict__Save__Input(html_dict=html_dict)
            save_output = _.save(save_input=save_input)

            assert save_output.success is True

    # ═══════════════════════════════════════════════════════════════════════════
    # parse_html_to_dict Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_parse_html_to_dict(self):                                           # Test helper method
        with Html_LETS__Html__To__Dict().setup() as _:
            result = _.parse_html_to_dict(self.sample_html)

            assert type(result) is dict
            assert 'tag'        in result
            assert 'node_id'    in result

    # ═══════════════════════════════════════════════════════════════════════════
    # Schema Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_Schema__Html_Dict(self):                                            # Test html dict schema
        data   = {'tag': 'div', 'children': []}
        schema = Schema__Html_Dict(html_dict=data)

        assert schema.html_dict         == data
        assert schema.html_dict['tag']  == 'div'

    def test_Schema__Html_Dict__nested(self):                                    # Test nested dict
        data = {'tag': 'html',
                'children': [{'tag': 'body',
                              'children': [{'tag': 'p', 'text': 'Hello'}]}]}
        schema = Schema__Html_Dict(html_dict=data)

        assert len(schema.html_dict['children'])    == 1
        assert schema.html_dict['children'][0]['tag'] == 'body'

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_integration__full_pipeline(self):                                   # Test L-E-T-S flow
        with Html_LETS__Html__To__Dict().setup() as _:
            html = self.html_generator.nested_html()

            # Load
            load_input  = Schema__Html_To_Dict__Load__Input(html=html)
            load_output = _.load(load_input=load_input)

            # Transform
            transform_input  = Schema__Html_To_Dict__Transform__Input(html=load_output.html)
            transform_output = _.transform(transform_input=transform_input)

            # Save
            save_input  = Schema__Html_To_Dict__Save__Input(html_dict=transform_output.html_dict)
            save_output = _.save(save_input=save_input)

            assert save_output.success                          is True
            assert transform_output.html_dict.html_dict         is not None
            assert transform_output.html_dict.html_dict['tag']  == 'html'
