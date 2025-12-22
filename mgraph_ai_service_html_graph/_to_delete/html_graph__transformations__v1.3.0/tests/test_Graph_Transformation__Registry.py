from unittest                                                                                      import TestCase
from enum                                                                                          import Enum
from osbot_utils.type_safe.Type_Safe                                                               import Type_Safe
from osbot_utils.utils.Objects                                                                     import base_classes
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base   import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Registry import Graph_Transformation__Registry
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Registry import transformation_registry
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Registry import Transformation_Type


class test_Graph_Transformation__Registry(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.registry = Graph_Transformation__Registry()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with self.registry as _:
            assert type(_)         is Graph_Transformation__Registry
            assert base_classes(_) == [Type_Safe, object]
            assert _._initialized  == True
            assert len(_._transformations) > 0

    def test__singleton_instance(self):
        assert transformation_registry is not None
        assert type(transformation_registry) is Graph_Transformation__Registry

    # ═══════════════════════════════════════════════════════════════════════════════
    # Registration Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__register__adds_transformation(self):
        registry = Graph_Transformation__Registry()
        initial_count = len(registry._transformations)

        # Create a custom transformation
        class Custom_Transform(Graph_Transformation__Base):
            name = "test_custom"

        registry.register(Custom_Transform)
        assert len(registry._transformations) == initial_count + 1
        assert registry.exists("test_custom")

    def test__register_all__includes_defaults(self):
        expected = ['default', 'body_only', 'structure_only',
                    'attributes_view', 'clean', 'semantic']

        for name in expected:
            assert self.registry.exists(name), f"Missing transformation: {name}"

    # ═══════════════════════════════════════════════════════════════════════════════
    # Lookup Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get__returns_instance(self):
        result = self.registry.get('default')
        assert result is not None
        assert isinstance(result, Graph_Transformation__Base)

    def test__get__returns_correct_type(self):
        result = self.registry.get('body_only')
        assert result.name == 'body_only'

    def test__get__unknown_raises(self):
        with self.assertRaises(ValueError) as context:
            self.registry.get('nonexistent')
        assert 'Unknown transformation' in str(context.exception)

    def test__exists__true_for_registered(self):
        assert self.registry.exists('default')    == True
        assert self.registry.exists('body_only')  == True
        assert self.registry.exists('clean')      == True

    def test__exists__false_for_unknown(self):
        assert self.registry.exists('nonexistent') == False
        assert self.registry.exists('')            == False

    def test__names__returns_list(self):
        names = self.registry.names()
        assert type(names) is list
        assert 'default' in names
        assert 'body_only' in names

    def test__names__count(self):
        names = self.registry.names()
        assert len(names) == 6                                                        # 6 registered transformations

    # ═══════════════════════════════════════════════════════════════════════════════
    # Enumeration Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__list_all__returns_list(self):
        result = self.registry.list_all()
        assert type(result) is list
        assert len(result) == 6

    def test__list_all__contains_metadata(self):
        result = self.registry.list_all()
        for item in result:
            assert 'name'        in item
            assert 'label'       in item
            assert 'description' in item

    def test__list_all__includes_all_transformations(self):
        result = self.registry.list_all()
        names  = [item['name'] for item in result]
        assert 'default'         in names
        assert 'body_only'       in names
        assert 'structure_only'  in names
        assert 'attributes_view' in names
        assert 'clean'           in names
        assert 'semantic'        in names

    def test__create_enum__returns_enum(self):
        result = self.registry.create_enum()
        assert issubclass(result, Enum)

    def test__create_enum__has_values(self):
        result = self.registry.create_enum()
        assert hasattr(result, 'DEFAULT')
        assert hasattr(result, 'BODY_ONLY')
        assert hasattr(result, 'CLEAN')

    # ═══════════════════════════════════════════════════════════════════════════════
    # Static Enum Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__Transformation_Type__is_enum(self):
        assert issubclass(Transformation_Type, Enum)

    def test__Transformation_Type__values(self):
        assert Transformation_Type.default.value         == 'default'
        assert Transformation_Type.body_only.value       == 'body_only'
        assert Transformation_Type.structure_only.value  == 'structure_only'
        assert Transformation_Type.attributes_view.value == 'attributes_view'
        assert Transformation_Type.clean.value           == 'clean'
        assert Transformation_Type.semantic.value        == 'semantic'