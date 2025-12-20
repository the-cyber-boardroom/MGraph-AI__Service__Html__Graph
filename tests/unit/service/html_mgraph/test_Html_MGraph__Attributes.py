from unittest                                                                   import TestCase
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Attributes   import Html_MGraph__Attributes
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Base         import Html_MGraph__Base
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id import Obj_Id
from osbot_utils.utils.Objects                                                  import base_classes


class test_Html_MGraph__Attributes(TestCase):                                   # Test attributes graph

    def test__init__(self):                                                     # Test initialization
        with Html_MGraph__Attributes() as _:
            assert type(_)          is Html_MGraph__Attributes
            assert  base_classes(_) == [Html_MGraph__Base, Type_Safe, object]

    def test_setup_creates_root(self):                                          # Test setup creates root
        with Html_MGraph__Attributes().setup() as _:
            assert _.root_id is not None

    def test_register_element_and_get_tag(self):                                # Test element registration and tag lookup
        from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid import Random_Guid

        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'div')

            assert _.get_tag(node_id)          == 'div'
            assert _.get_elements_by_tag('div') == [node_id]

    def test_add_attribute(self):                                               # Test attribute addition
        from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid import Random_Guid

        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'div')
            _.add_attribute(node_id, 'class', 'container', position=0)
            _.add_attribute(node_id, 'id'   , 'main'     , position=1)

            attrs = _.get_attributes(node_id)
            assert attrs == {'class': 'container', 'id': 'main'}

    def test_get_all_tags(self):                                                # Test getting all tags
        from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid import Random_Guid

        with Html_MGraph__Attributes().setup() as _:
            _.register_element(Node_Id(Obj_Id()), 'div')
            _.register_element(Node_Id(Obj_Id()), 'p')
            _.register_element(Node_Id(Obj_Id()), 'div')                            # Second div

            tags = _.get_all_tags()
            assert set(tags) == {'div', 'p'}                                    # Unique tags