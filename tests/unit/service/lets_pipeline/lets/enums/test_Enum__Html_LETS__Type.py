# ═══════════════════════════════════════════════════════════════════════════════
# test_Enum__Html_LETS__Type - Tests for LETS type enum
# Tests that enum values ARE the class types (not strings)
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                    import TestCase
from enum                                                                        import Enum
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.base.Html_LETS__Base import Html_LETS__Base
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.enums.Enum__Html_LETS__Type import Enum__Html_LETS__Type
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.steps.Html_LETS__Dict__To__MGraph import Html_LETS__Dict__To__MGraph
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.steps.Html_LETS__Html__From__Raw import Html_LETS__Html__From__Raw
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.steps.Html_LETS__Html__To__Dict import Html_LETS__Html__To__Dict


class test_Enum__Html_LETS__Type(TestCase):

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        assert issubclass(Enum__Html_LETS__Type, Enum)

    def test_enum_members(self):
        members      = list(Enum__Html_LETS__Type)
        member_names = [m.name for m in members]

        assert len(members)         >= 3
        assert 'HTML_FROM_RAW'      in member_names
        assert 'HTML_TO_DICT'       in member_names
        assert 'DICT_TO_MGRAPH'     in member_names

    # ═══════════════════════════════════════════════════════════════════════════
    # Value Tests - Values ARE Classes
    # ═══════════════════════════════════════════════════════════════════════════

    def test_HTML_FROM_RAW__value_is_class(self):
        value = Enum__Html_LETS__Type.HTML_FROM_RAW.value
        assert value is Html_LETS__Html__From__Raw

    def test_HTML_TO_DICT__value_is_class(self):
        value = Enum__Html_LETS__Type.HTML_TO_DICT.value
        assert value is Html_LETS__Html__To__Dict

    def test_DICT_TO_MGRAPH__value_is_class(self):
        value = Enum__Html_LETS__Type.DICT_TO_MGRAPH.value
        assert value is Html_LETS__Dict__To__MGraph

    # ═══════════════════════════════════════════════════════════════════════════
    # Instantiation Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_HTML_FROM_RAW__can_instantiate(self):
        lets_class = Enum__Html_LETS__Type.HTML_FROM_RAW.value
        instance   = lets_class()

        assert type(instance)             is Html_LETS__Html__From__Raw
        assert isinstance(instance, Html_LETS__Base)

    def test_HTML_TO_DICT__can_instantiate(self):
        lets_class = Enum__Html_LETS__Type.HTML_TO_DICT.value
        instance   = lets_class()

        assert type(instance)             is Html_LETS__Html__To__Dict
        assert isinstance(instance, Html_LETS__Base)

    def test_DICT_TO_MGRAPH__can_instantiate(self):
        lets_class = Enum__Html_LETS__Type.DICT_TO_MGRAPH.value
        instance   = lets_class()

        assert type(instance)             is Html_LETS__Dict__To__MGraph
        assert isinstance(instance, Html_LETS__Base)

    # ═══════════════════════════════════════════════════════════════════════════
    # Setup Chain Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_instantiate_and_setup(self):
        lets_class = Enum__Html_LETS__Type.HTML_FROM_RAW.value                   # Use one that's refactored
        instance   = lets_class().setup()

        assert instance.config      is not None
        assert instance.config.name == 'html-from-raw'

    def test_all_lets_types_instantiate(self):
        for lets_type in Enum__Html_LETS__Type:
            lets_class = lets_type.value
            instance   = lets_class().setup()

            assert instance.config      is not None
            assert instance.config.name != ''

    # ═══════════════════════════════════════════════════════════════════════════
    # Enum Lookup Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_lookup_by_name(self):
        lets_type = Enum__Html_LETS__Type['HTML_FROM_RAW']

        assert lets_type       == Enum__Html_LETS__Type.HTML_FROM_RAW
        assert lets_type.value is Html_LETS__Html__From__Raw

    def test_lookup_by_name__all_types(self):
        names = ['HTML_FROM_RAW', 'HTML_TO_DICT', 'DICT_TO_MGRAPH']

        for name in names:
            lets_type = Enum__Html_LETS__Type[name]
            assert lets_type.name == name

    # ═══════════════════════════════════════════════════════════════════════════
    # Inheritance Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_all_values_are_LETS_subclasses(self):
        for lets_type in Enum__Html_LETS__Type:
            lets_class = lets_type.value
            assert issubclass(lets_class, Html_LETS__Base)

    def test_values_are_distinct_classes(self):
        classes = [lets_type.value for lets_type in Enum__Html_LETS__Type]
        assert len(classes) == len(set(classes))

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_integration__pipeline_from_enum(self):
        pipeline = [Enum__Html_LETS__Type.HTML_FROM_RAW.value ,
                    Enum__Html_LETS__Type.HTML_TO_DICT.value  ]

        assert len(pipeline) == 2
        assert pipeline[0]   is Html_LETS__Html__From__Raw
        assert pipeline[1]   is Html_LETS__Html__To__Dict

        instances = [cls().setup() for cls in pipeline]
        assert len(instances)           == 2
        assert instances[0].config.name == 'html-from-raw'
        assert instances[1].config.name == 'html-to-dict'