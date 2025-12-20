from unittest                                                               import TestCase
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Scripts  import Html_MGraph__Scripts
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id           import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id            import Obj_Id


class test_Html_MGraph__Scripts(TestCase):                                      # Test scripts graph

    def test__init__(self):                                                     # Test initialization
        with Html_MGraph__Scripts() as _:
            assert type(_) is Html_MGraph__Scripts

    def test_register_inline_script(self):                                      # Test inline script


        with Html_MGraph__Scripts().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_script(node_id, content="console.log('hello')")

            assert _.is_inline_script(node_id)  is True
            assert _.is_external_script(node_id) is False
            assert _.get_script_content(node_id) == "console.log('hello')"

    def test_register_external_script(self):                                    # Test external script

        with Html_MGraph__Scripts().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_script(node_id, content=None)

            assert _.is_inline_script(node_id)   is False
            assert _.is_external_script(node_id) is True
            assert _.get_script_content(node_id) is None
