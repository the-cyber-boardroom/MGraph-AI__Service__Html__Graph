from unittest                                                                   import TestCase
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.utils.Objects                                                  import base_classes
from mgraph_db.mgraph.MGraph                                                    import MGraph
from mgraph_ai_service_html_graph.service.html_graph.Html_Dict__To__Html_MGraph import Html_Dict__To__Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph__Path import Html_MGraph__Path
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph__To__Html_Dict import Html_MGraph__To__Html_Dict


class test_Html_MGraph__To__Html_Dict(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.to_graph_converter = Html_Dict__To__Html_MGraph()
        cls.to_dict_converter  = Html_MGraph__To__Html_Dict()

        cls.simple_html_dict = { 'tag'        : 'div'                                      ,
                                 'attrs'      : {'class': 'main'}                          ,
                                 'child_nodes': []                                         ,
                                 'text_nodes' : [{'data': 'Hello', 'position': 0}]         }

        cls.nested_html_dict = { 'tag'        : 'div'                                      ,
                                 'attrs'      : {}                                         ,
                                 'child_nodes': [
                                     { 'tag'        : 'p'                                  ,
                                       'attrs'      : {}                                   ,
                                       'child_nodes': []                                   ,
                                       'text_nodes' : [{'data': 'Paragraph', 'position': 0}],
                                       'position'   : 0                                    }
                                 ],
                                 'text_nodes' : []                                         }

        cls.multi_attr_dict = { 'tag'        : 'a'                                         ,
                                'attrs'      : {'href': '/link', 'class': 'btn', 'id': 'submit'},
                                'child_nodes': []                                          ,
                                'text_nodes' : [{'data': 'Click me', 'position': 0}]       }

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                     # Test auto-initialization
        with Html_MGraph__To__Html_Dict() as _:
            assert type(_)            is Html_MGraph__To__Html_Dict
            assert base_classes(_)    == [Type_Safe, object]
            assert _.mgraph           is None
            assert type(_.path_utils) is Html_MGraph__Path

    # ═══════════════════════════════════════════════════════════════════════════════
    # Round-Trip Tests - Simple
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_convert__round_trip_simple_tag(self):                              # Test round-trip preserves tag
        mgraph = self.to_graph_converter.convert(self.simple_html_dict)
        result = self.to_dict_converter.convert(mgraph)

        assert result['tag'] == 'div'

    def test_convert__round_trip_simple_attrs(self):                            # Test round-trip preserves attributes
        mgraph = self.to_graph_converter.convert(self.simple_html_dict)
        result = self.to_dict_converter.convert(mgraph)

        assert result['attrs'] == {'class': 'main'}

    def test_convert__round_trip_simple_text(self):                             # Test round-trip preserves text
        mgraph = self.to_graph_converter.convert(self.simple_html_dict)
        result = self.to_dict_converter.convert(mgraph)

        assert len(result['text_nodes'])        == 1
        assert result['text_nodes'][0]['data']  == 'Hello'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Round-Trip Tests - Nested
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_convert__round_trip_nested_structure(self):                        # Test round-trip preserves nested structure
        mgraph = self.to_graph_converter.convert(self.nested_html_dict)
        result = self.to_dict_converter.convert(mgraph)

        assert result['tag']                        == 'div'
        assert len(result['child_nodes'])           == 1
        assert result['child_nodes'][0]['tag']      == 'p'
        assert result['child_nodes'][0]['text_nodes'][0]['data'] == 'Paragraph'

    def test_convert__round_trip_preserves_child_order(self):                   # Test round-trip preserves child order
        html_dict = { 'tag'        : 'ul'                                      ,
                      'attrs'      : {}                                        ,
                      'child_nodes': [
                          {'tag': 'li', 'attrs': {}, 'child_nodes': [],
                           'text_nodes': [{'data': 'First', 'position': 0}], 'position': 0},
                          {'tag': 'li', 'attrs': {}, 'child_nodes': [],
                           'text_nodes': [{'data': 'Second', 'position': 0}], 'position': 1},
                          {'tag': 'li', 'attrs': {}, 'child_nodes': [],
                           'text_nodes': [{'data': 'Third', 'position': 0}], 'position': 2}
                      ],
                      'text_nodes' : []                                        }

        mgraph = self.to_graph_converter.convert(html_dict)
        result = self.to_dict_converter.convert(mgraph)

        assert len(result['child_nodes']) == 3
        assert result['child_nodes'][0]['text_nodes'][0]['data'] == 'First'
        assert result['child_nodes'][1]['text_nodes'][0]['data'] == 'Second'
        assert result['child_nodes'][2]['text_nodes'][0]['data'] == 'Third'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Round-Trip Tests - Attributes
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_convert__round_trip_multiple_attrs(self):                          # Test round-trip preserves multiple attributes
        mgraph = self.to_graph_converter.convert(self.multi_attr_dict)
        result = self.to_dict_converter.convert(mgraph)

        assert result['attrs']['href']  == '/link'
        assert result['attrs']['class'] == 'btn'
        assert result['attrs']['id']    == 'submit'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Round-Trip Tests - Mixed Content
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_convert__round_trip_mixed_content(self):                           # Test round-trip preserves mixed content order
        mixed_dict = { 'tag'        : 'div'                                    ,
                       'attrs'      : {}                                       ,
                       'child_nodes': [
                           {'tag': 'span', 'attrs': {}, 'child_nodes': [],
                            'text_nodes': [{'data': 'middle', 'position': 0}], 'position': 1}
                       ],
                       'text_nodes' : [
                           {'data': 'before', 'position': 0},
                           {'data': 'after' , 'position': 2}
                       ]}

        mgraph = self.to_graph_converter.convert(mixed_dict)
        result = self.to_dict_converter.convert(mgraph)

        assert len(result['text_nodes'])  == 2
        assert len(result['child_nodes']) == 1

        text_positions = [t['position'] for t in result['text_nodes']]
        assert 0 in text_positions
        assert 2 in text_positions

    # ═══════════════════════════════════════════════════════════════════════════════
    # Empty Graph Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_convert__empty_graph(self):                                        # Test converting empty graph returns empty dict
        empty_graph = MGraph()
        result      = self.to_dict_converter.convert(empty_graph)

        assert result == {}

    # ═══════════════════════════════════════════════════════════════════════════════
    # find_root_element Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_find_root_element__returns_shortest_path(self):                    # Test root is element with shortest path
        mgraph    = self.to_graph_converter.convert(self.nested_html_dict)
        converter = Html_MGraph__To__Html_Dict(mgraph=mgraph)
        root_id   = converter.find_root_element()

        assert root_id is not None

        node      = mgraph.data().node(root_id).node
        node_path = str(node.data.node_path)
        assert node_path == 'div'                                               # Root should be 'div', not 'div.p[0]'