from unittest                                                                             import TestCase
from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from osbot_utils.utils.Objects                                                            import base_classes
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph                          import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__VisJs       import Html_MGraph__To__VisJs
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config         import Html_MGraph__Render__Config


class test_Html_MGraph__To__VisJs(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simple_html_dict  = SIMPLE_HTML_DICT
        cls.complex_html_dict = COMPLEX_HTML_DICT
        cls.html_mgraph_simple  = Html_MGraph.from_html_dict(cls.simple_html_dict)
        cls.html_mgraph_complex = Html_MGraph.from_html_dict(cls.complex_html_dict)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                   # Test auto-initialization
        with Html_MGraph__To__VisJs(mgraph=self.html_mgraph_simple.mgraph) as _:
            assert type(_)         is Html_MGraph__To__VisJs
            assert base_classes(_) == [Type_Safe, object]
            assert _.mgraph        is self.html_mgraph_simple.mgraph
            assert _.config        is None

    def test__init__with_config(self):                                                        # Test initialization with config
        config = Html_MGraph__Render__Config()
        with Html_MGraph__To__VisJs(mgraph = self.html_mgraph_simple.mgraph,
                                    config = config                        ) as _:
            assert _.config is config

    # ═══════════════════════════════════════════════════════════════════════════════
    # export Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__returns_dict(self):                                                     # Test export returns dict
        with Html_MGraph__To__VisJs(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()

            assert type(result) is dict
            assert 'nodes'  in result
            assert 'edges'  in result
            assert 'rootId' in result

    def test__export__nodes_is_list(self):                                                    # Test nodes is a list
        with Html_MGraph__To__VisJs(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()

            assert type(result['nodes']) is list
            assert len(result['nodes']) > 0

    def test__export__edges_is_list(self):                                                    # Test edges is a list
        with Html_MGraph__To__VisJs(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()

            assert type(result['edges']) is list
            assert len(result['edges']) > 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Format Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__node_has_required_fields(self):                                         # Test node has vis.js required fields
        with Html_MGraph__To__VisJs(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()
            node   = result['nodes'][0]

            assert 'id'    in node
            assert 'label' in node
            assert 'shape' in node
            assert 'color' in node
            assert 'font'  in node

    def test__export__node_color_structure(self):                                             # Test node color has vis.js structure
        with Html_MGraph__To__VisJs(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()
            node   = result['nodes'][0]

            assert 'background' in node['color']
            assert 'border'     in node['color']
            assert 'highlight'  in node['color']

    def test__export__node_font_structure(self):                                              # Test node font has vis.js structure
        with Html_MGraph__To__VisJs(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()
            node   = result['nodes'][0]

            assert 'color' in node['font']
            assert 'size'  in node['font']

    def test__export__node_has_semantic_metadata(self):                                       # Test node has semantic metadata
        with Html_MGraph__To__VisJs(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()
            node   = result['nodes'][0]

            assert 'nodeType' in node
            assert 'domPath'  in node
            assert 'category' in node
            assert 'depth'    in node

    def test__export__node_types_correct(self):                                               # Test node types are valid
        with Html_MGraph__To__VisJs(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()

            valid_types = {'element', 'tag', 'attr', 'text'}
            for node in result['nodes']:
                assert node['nodeType'] in valid_types

    # ═══════════════════════════════════════════════════════════════════════════════
    # Edge Format Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__edge_has_required_fields(self):                                         # Test edge has vis.js required fields
        with Html_MGraph__To__VisJs(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()
            edge   = result['edges'][0]

            assert 'id'     in edge
            assert 'from'   in edge
            assert 'to'     in edge
            assert 'dashes' in edge
            assert 'color'  in edge

    def test__export__edge_color_structure(self):                                             # Test edge color has vis.js structure
        with Html_MGraph__To__VisJs(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()
            edge   = result['edges'][0]

            assert 'color'     in edge['color']
            assert 'highlight' in edge['color']

    def test__export__edge_has_predicate(self):                                               # Test edge has predicate metadata
        with Html_MGraph__To__VisJs(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()
            edge   = result['edges'][0]

            assert 'predicate' in edge

    def test__export__edge_references_valid_nodes(self):                                      # Test edge references valid node IDs
        with Html_MGraph__To__VisJs(mgraph=self.html_mgraph_simple.mgraph) as _:
            result   = _.export()
            node_ids = {n['id'] for n in result['nodes']}

            for edge in result['edges']:
                assert edge['from'] in node_ids
                assert edge['to']   in node_ids

    # ═══════════════════════════════════════════════════════════════════════════════
    # Shape Mapping Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___map_shape__box(self):                                                          # Test box shape mapping
        with Html_MGraph__To__VisJs(mgraph=self.html_mgraph_simple.mgraph) as _:
            assert _._map_shape('box') == 'box'

    def test___map_shape__ellipse(self):                                                      # Test ellipse shape mapping
        with Html_MGraph__To__VisJs(mgraph=self.html_mgraph_simple.mgraph) as _:
            assert _._map_shape('ellipse') == 'ellipse'

    def test___map_shape__unknown_defaults_to_box(self):                                      # Test unknown shape defaults to box
        with Html_MGraph__To__VisJs(mgraph=self.html_mgraph_simple.mgraph) as _:
            assert _._map_shape('unknown') == 'box'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Color Helper Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___lighten__valid_hex(self):                                                      # Test color lightening
        with Html_MGraph__To__VisJs(mgraph=self.html_mgraph_simple.mgraph) as _:
            lighter = _._lighten('#000000')
            assert lighter.startswith('#')
            assert lighter != '#000000'

    def test___lighten__invalid_hex(self):                                                    # Test lightening with invalid input
        with Html_MGraph__To__VisJs(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _._lighten('invalid')
            assert result == '#FFFFFF'                                                        # Should return default

    # ═══════════════════════════════════════════════════════════════════════════════
    # Complex Graph Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__complex_html(self):                                                     # Test export with complex HTML
        with Html_MGraph__To__VisJs(mgraph=self.html_mgraph_complex.mgraph) as _:
            result = _.export()

            assert len(result['nodes']) >= 3                                                  # div, h1, p at minimum
            assert len(result['edges']) >= 2                                                  # At least parent-child edges

    def test__export__with_config_filters(self):                                              # Test export respects config filters
        config = Html_MGraph__Render__Config()
        config.show_tag_nodes = False

        with Html_MGraph__To__VisJs(mgraph = self.html_mgraph_simple.mgraph,
                                    config = config                        ) as _:
            result = _.export()

            tag_nodes = [n for n in result['nodes'] if n['nodeType'] == 'tag']
            assert len(tag_nodes) == 0                                                        # Tag nodes filtered out


# ═══════════════════════════════════════════════════════════════════════════════
# Test Data
# ═══════════════════════════════════════════════════════════════════════════════

SIMPLE_HTML_DICT = { 'tag'        : 'div'                                      ,
                     'attrs'      : {'class': 'main'}                          ,
                     'child_nodes': []                                         ,
                     'text_nodes' : [{'data': 'Hello World', 'position': 0}]   }

COMPLEX_HTML_DICT = { 'tag'        : 'div'                                     ,
                      'attrs'      : {'class': 'main', 'id': 'content'}        ,
                      'child_nodes': [
                          { 'tag'        : 'h1'                                ,
                            'attrs'      : {}                                  ,
                            'child_nodes': []                                  ,
                            'text_nodes' : [{'data': 'Title', 'position': 0}]  ,
                            'position'   : 0                                   },
                          { 'tag'        : 'p'                                 ,
                            'attrs'      : {}                                  ,
                            'child_nodes': []                                  ,
                            'text_nodes' : [{'data': 'Paragraph', 'position': 0}],
                            'position'   : 1                                   }
                      ],
                      'text_nodes' : []                                        }
