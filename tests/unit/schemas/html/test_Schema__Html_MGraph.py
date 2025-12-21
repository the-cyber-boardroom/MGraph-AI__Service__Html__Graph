from unittest                                                                               import TestCase
from mgraph_ai_service_html_graph.schemas.html.Schema__Html_MGraph           import (
    Schema__Html_MGraph__Stats__Base      ,
    Schema__Html_MGraph__Stats__Head      ,
    Schema__Html_MGraph__Stats__Body      ,
    Schema__Html_MGraph__Stats__Attributes,
    Schema__Html_MGraph__Stats__Scripts   ,
    Schema__Html_MGraph__Stats__Styles    ,
    Schema__Html_MGraph__Stats__Document  ,
    Schema__Html_MGraph__Json__Base       ,
    Schema__Html_MGraph__Json__Document   ,
    Schema__Html_MGraph__Element_Info     ,
)
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.utils.Objects                                                              import base_classes


class test_Schema__Html_MGraph(TestCase):                                       # Test Schema classes

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Base Schema Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__Schema__Html_MGraph__Stats__Base(self):                           # Test base stats schema
        with Schema__Html_MGraph__Stats__Base() as _:
            assert type(_)         is Schema__Html_MGraph__Stats__Base
            assert base_classes(_) == [Type_Safe, object]
            assert _.total_nodes   == 0
            assert _.total_edges   == 0
            assert _.root_id       is None

    def test__Schema__Html_MGraph__Stats__Base__with_values(self):              # Test base stats with values
        with Schema__Html_MGraph__Stats__Base(total_nodes=10, total_edges=15) as _:
            assert _.total_nodes == 10
            assert _.total_edges == 15

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Component Schema Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__Schema__Html_MGraph__Stats__Head(self):                           # Test head stats schema
        with Schema__Html_MGraph__Stats__Head() as _:
            assert type(_)          is Schema__Html_MGraph__Stats__Head
            assert base_classes(_)  == [Schema__Html_MGraph__Stats__Base, Type_Safe, object]
            assert _.total_nodes    == 0
            assert _.element_nodes  == 0
            assert _.text_nodes     == 0

    def test__Schema__Html_MGraph__Stats__Body(self):                           # Test body stats schema
        with Schema__Html_MGraph__Stats__Body() as _:
            assert type(_)          is Schema__Html_MGraph__Stats__Body
            assert _.element_nodes  == 0
            assert _.text_nodes     == 0

    def test__Schema__Html_MGraph__Stats__Attributes(self):                     # Test attributes stats schema
        with Schema__Html_MGraph__Stats__Attributes() as _:
            assert type(_)              is Schema__Html_MGraph__Stats__Attributes
            assert _.registered_elements == 0
            assert _.total_attributes    == 0
            assert _.unique_tags         == 0

    def test__Schema__Html_MGraph__Stats__Scripts(self):                        # Test scripts stats schema
        with Schema__Html_MGraph__Stats__Scripts() as _:
            assert type(_)            is Schema__Html_MGraph__Stats__Scripts
            assert _.total_scripts    == 0
            assert _.inline_scripts   == 0
            assert _.external_scripts == 0

    def test__Schema__Html_MGraph__Stats__Styles(self):                         # Test styles stats schema
        with Schema__Html_MGraph__Stats__Styles() as _:
            assert type(_)           is Schema__Html_MGraph__Stats__Styles
            assert _.total_styles    == 0
            assert _.inline_styles   == 0
            assert _.external_styles == 0

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Document Schema Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__Schema__Html_MGraph__Stats__Document(self):                       # Test document stats schema
        with Schema__Html_MGraph__Stats__Document() as _:
            assert type(_)     is Schema__Html_MGraph__Stats__Document
            assert _.document   is None
            assert _.head       is None
            assert _.body       is None
            assert _.attributes is None
            assert _.scripts    is None
            assert _.styles     is None

    def test__Schema__Html_MGraph__Stats__Document__with_components(self):      # Test document stats with components
        head_stats = Schema__Html_MGraph__Stats__Head(total_nodes=5, element_nodes=3, text_nodes=2)
        body_stats = Schema__Html_MGraph__Stats__Body(total_nodes=10, element_nodes=7, text_nodes=3)

        with Schema__Html_MGraph__Stats__Document(head=head_stats, body=body_stats) as _:
            assert _.head.total_nodes    == 5
            assert _.head.element_nodes  == 3
            assert _.body.total_nodes    == 10
            assert _.body.text_nodes     == 3

    # ═══════════════════════════════════════════════════════════════════════════
    # JSON Schema Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__Schema__Html_MGraph__Json__Base(self):                            # Test base JSON schema
        with Schema__Html_MGraph__Json__Base() as _:
            assert type(_)   is Schema__Html_MGraph__Json__Base
            assert _.nodes   is None
            assert _.edges   is None
            assert _.root_id is None

    def test__Schema__Html_MGraph__Json__Base__with_values(self):               # Test base JSON with values
        nodes = {'node1': {'type': 'element'}}
        edges = {'edge1': {'from': 'node1', 'to': 'node2'}}

        with Schema__Html_MGraph__Json__Base(nodes=nodes, edges=edges, root_id='node1') as _:
            assert _.nodes   == nodes
            assert _.edges   == edges
            assert _.root_id == 'node1'

    def test__Schema__Html_MGraph__Json__Document(self):                        # Test document JSON schema
        with Schema__Html_MGraph__Json__Document() as _:
            assert type(_)     is Schema__Html_MGraph__Json__Document
            assert _.document   is None
            assert _.head       is None
            assert _.body       is None
            assert _.attributes is None
            assert _.scripts    is None
            assert _.styles     is None

    # ═══════════════════════════════════════════════════════════════════════════
    # Element Info Schema Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__Schema__Html_MGraph__Element_Info(self):                          # Test element info schema
        with Schema__Html_MGraph__Element_Info() as _:
            assert type(_)          is Schema__Html_MGraph__Element_Info
            assert _.node_id        is None
            assert _.tag            is None
            assert _.attrs          is None
            assert _.in_head        is False
            assert _.in_body        is False
            assert _.script_content is None
            assert _.style_content  is None

    def test__Schema__Html_MGraph__Element_Info__with_values(self):             # Test element info with values
        from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id import Node_Id
        from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id  import Obj_Id

        node_id = Node_Id(Obj_Id())
        attrs   = {'class': 'main', 'id': 'app'}

        with Schema__Html_MGraph__Element_Info(node_id=node_id, tag='div', attrs=attrs, in_body=True) as _:
            assert _.node_id        == node_id
            assert _.tag            == 'div'
            assert _.attrs['class'] == 'main'
            assert _.attrs['id']    == 'app'
            assert _.in_body        is True
            assert _.in_head        is False

    def test__Schema__Html_MGraph__Element_Info__script(self):                  # Test element info for script
        with Schema__Html_MGraph__Element_Info(tag='script', script_content='console.log("hi");', in_head=True) as _:
            assert _.tag            == 'script'
            assert _.script_content == 'console.log("hi");'
            assert _.in_head        is True

    def test__Schema__Html_MGraph__Element_Info__style(self):                   # Test element info for style
        with Schema__Html_MGraph__Element_Info(tag='style', style_content='body {}', in_head=True) as _:
            assert _.tag           == 'style'
            assert _.style_content == 'body {}'

    # ═══════════════════════════════════════════════════════════════════════════
    # Serialization Tests (json() method)
    # ═══════════════════════════════════════════════════════════════════════════

    def test__stats_to_dict(self):                                              # Test converting stats schema to dict
        stats = Schema__Html_MGraph__Stats__Head(total_nodes=5, total_edges=3, element_nodes=4, text_nodes=1)
        stats_dict = stats.json()

        assert type(stats_dict)              is dict
        assert stats_dict['total_nodes']     == 5
        assert stats_dict['total_edges']     == 3
        assert stats_dict['element_nodes']   == 4
        assert stats_dict['text_nodes']      == 1

    def test__element_info_to_dict(self):                                       # Test converting element info to dict
        info = Schema__Html_MGraph__Element_Info(tag='div', attrs={'class': 'test'}, in_body=True)
        info_dict = info.json()

        assert type(info_dict)        is dict
        assert info_dict['tag']       == 'div'
        assert info_dict['in_body']   is True
        assert info_dict['attrs']     == {'class': 'test'}