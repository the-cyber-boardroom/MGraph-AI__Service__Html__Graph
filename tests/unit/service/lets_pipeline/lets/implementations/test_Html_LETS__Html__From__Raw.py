# ═══════════════════════════════════════════════════════════════════════════════
# test_Html_LETS__Html__From__Raw - Tests for raw HTML input LETS
# Tests loading and passing through raw HTML content
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.base.Html_LETS__Base                       import Html_LETS__Base
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.utils.Objects                                                                          import base_types
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                               import Safe_Str__Html
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.implementations.Html_LETS__Html__From__Raw import Schema__Html_From_Raw__Load__Input, Schema__Html_From_Raw__Load__Output, Schema__Html_From_Raw__Transform__Input, Schema__Html_From_Raw__Save__Input, Schema__Html_From_Raw__Transform__Output, Html_LETS__Html__From__Raw
from mgraph_ai_service_html_graph.utils.testing.Html_Generator__For_Tests                               import Html_Generator__For_Tests


class test_Html_LETS__Html__From__Raw(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup
        cls.html_generator = Html_Generator__For_Tests()
        cls.sample_html    = cls.html_generator.simple_html()

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test auto-initialization
        with Html_LETS__Html__From__Raw() as _:
            assert type(_)       is Html_LETS__Html__From__Raw
            assert base_types(_) == [Html_LETS__Base, Type_Safe, object]

    def test__init____config_is_none(self):                                      # Test config starts None
        with Html_LETS__Html__From__Raw() as _:
            assert _.config is None                                              # Config set in setup()

    # ═══════════════════════════════════════════════════════════════════════════
    # Setup Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_setup(self):                                                        # Test setup initializes config
        with Html_LETS__Html__From__Raw() as _:
            result = _.setup()

            assert result             is _                                       # Returns self for chaining
            assert _.config           is not None
            assert _.config.name      == 'html-from-raw'
            assert 'raw HTML'         in _.config.description

    def test_setup__returns_self(self):                                          # Test chaining
        lets = Html_LETS__Html__From__Raw().setup()
        assert type(lets)        is Html_LETS__Html__From__Raw
        assert lets.config.name  == 'html-from-raw'

    # ═══════════════════════════════════════════════════════════════════════════
    # Load Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_load(self):                                                         # Test load returns HTML
        with Html_LETS__Html__From__Raw().setup() as _:
            load_input  = Schema__Html_From_Raw__Load__Input(html=self.sample_html)
            load_output = _.load(load_input=load_input)

            assert type(load_output)      is Schema__Html_From_Raw__Load__Output
            assert type(load_output.html) is Safe_Str__Html
            assert load_output.html       == self.sample_html

    def test_load__minimal_html(self):                                           # Test with minimal HTML
        with Html_LETS__Html__From__Raw().setup() as _:
            minimal_html = self.html_generator.minimal_html()
            load_input   = Schema__Html_From_Raw__Load__Input(html=minimal_html)
            load_output  = _.load(load_input=load_input)

            assert '<p>Hello</p>' in str(load_output.html)

    # ═══════════════════════════════════════════════════════════════════════════
    # Transform Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_transform(self):                                                    # Test transform passes through
        with Html_LETS__Html__From__Raw().setup() as _:
            transform_input  = Schema__Html_From_Raw__Transform__Input(html=self.sample_html)
            transform_output = _.transform(transform_input=transform_input)

            assert type(transform_output) is Schema__Html_From_Raw__Transform__Output
            assert transform_output.html  == self.sample_html

    # ═══════════════════════════════════════════════════════════════════════════
    # Save Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_save(self):                                                         # Test save returns success
        with Html_LETS__Html__From__Raw().setup() as _:
            save_input  = Schema__Html_From_Raw__Save__Input(html=self.sample_html)
            save_output = _.save(save_input=save_input)

            assert save_output.success is True

    # ═══════════════════════════════════════════════════════════════════════════
    # Schema Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_Schema__Html_From_Raw__Load__Input(self):                           # Test load input schema
        schema = Schema__Html_From_Raw__Load__Input(html=self.sample_html)
        assert type(schema.html) is Safe_Str__Html

    def test_Schema__Html_From_Raw__Load__Output(self):                          # Test load output schema
        schema = Schema__Html_From_Raw__Load__Output(html=self.sample_html)
        assert type(schema.html) is Safe_Str__Html

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_integration__full_pipeline(self):                                   # Test L-E-T-S flow
        with Html_LETS__Html__From__Raw().setup() as _:
            html = self.html_generator.nested_html()

            # Load
            load_input  = Schema__Html_From_Raw__Load__Input(html=html)
            load_output = _.load(load_input=load_input)

            # Transform
            transform_input  = Schema__Html_From_Raw__Transform__Input(html=load_output.html)
            transform_output = _.transform(transform_input=transform_input)

            # Save
            save_input  = Schema__Html_From_Raw__Save__Input(html=transform_output.html)
            save_output = _.save(save_input=save_input)

            assert save_output.success is True
            assert transform_output.html == html
