from unittest                                                                             import TestCase
from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from osbot_utils.utils.Objects                                                            import base_classes
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                         import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Export__Base    import Html_MGraph__Export__Base
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__VisJs       import Html_MGraph__To__VisJs
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config         import Html_MGraph__Render__Config


class test_Html_MGraph__To__VisJs(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simple_html   = '<div class="main">Hello World</div>'
        cls.complex_html  = '<div class="main" id="content"><h1>Title</h1><p>Paragraph</p></div>'
        cls.html_mgraph_simple  = Html_MGraph.from_html(cls.simple_html)
        cls.html_mgraph_complex = Html_MGraph.from_html(cls.complex_html)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                   # Test auto-initialization
        with Html_MGraph__To__VisJs(html_mgraph=self.html_mgraph_simple) as _:
            assert type(_)         is Html_MGraph__To__VisJs
            assert base_classes(_) == [Html_MGraph__Export__Base, Type_Safe, object]
            assert _.html_mgraph   is self.html_mgraph_simple
            assert _.config        is None

    def test__init__with_config(self):                                                        # Test initialization with config
        config = Html_MGraph__Render__Config()
        with Html_MGraph__To__VisJs(html_mgraph = self.html_mgraph_simple,
                                    config      = config                 ) as _:
            assert _.config is config

    # ═══════════════════════════════════════════════════════════════════════════════
    # export Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__returns_dict(self):                                                     # Test export returns dict
        with Html_MGraph__To__VisJs(html_mgraph=self.html_mgraph_simple) as _:
            result = _.export()

            assert type(result) is dict
            assert 'nodes'  in result
            assert 'edges'  in result
            assert 'rootId' in result

    def test__export__nodes_is_list(self):                                                    # Test nodes is a list
        with Html_MGraph__To__VisJs(html_mgraph=self.html_mgraph_simple) as _:
            result = _.export()

            assert type(result['nodes']) is list
            assert len(result['nodes']) > 0

    def test__export__edges_is_list(self):                                                    # Test edges is a list
        with Html_MGraph__To__VisJs(html_mgraph=self.html_mgraph_complex) as _:
            result = _.export()

            assert type(result['edges']) is list

    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Format Tests (vis.js specific fields)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__node_has_required_fields(self):                                         # Test node has vis.js required fields
        with Html_MGraph__To__VisJs(html_mgraph=self.html_mgraph_simple) as _:
            result = _.export()
            node   = result['nodes'][0]

            assert 'id'    in node
            assert 'label' in node
            assert 'title' in node                                                            # Tooltip
            assert 'shape' in node
            assert 'color' in node
            assert 'font'  in node

    def test__export__node_color_structure(self):                                             # Test node color has vis.js structure
        with Html_MGraph__To__VisJs(html_mgraph=self.html_mgraph_simple) as _:
            result = _.export()
            color  = result['nodes'][0]['color']

            assert 'background' in color
            assert 'border'     in color
            assert 'highlight'  in color

    def test__export__node_font_structure(self):                                              # Test node font has vis.js structure
        with Html_MGraph__To__VisJs(html_mgraph=self.html_mgraph_simple) as _:
            result = _.export()
            font   = result['nodes'][0]['font']

            assert 'color' in font
            assert 'size'  in font

    def test__export__node_has_semantic_metadata(self):                                       # Test node has semantic metadata
        with Html_MGraph__To__VisJs(html_mgraph=self.html_mgraph_simple) as _:
            result = _.export()
            node   = result['nodes'][0]

            assert 'nodeType'    in node
            assert 'domPath'     in node
            assert 'category'    in node
            assert 'depth'       in node
            assert 'graphSource' in node

    def test__export__node_types_correct(self):                                               # Test node types are valid
        with Html_MGraph__To__VisJs(html_mgraph=self.html_mgraph_simple) as _:
            result = _.export()

            valid_types = {'element', 'tag', 'attr', 'text', 'script', 'style'}
            for node in result['nodes']:
                assert node['nodeType'] in valid_types

    # ═══════════════════════════════════════════════════════════════════════════════
    # Edge Format Tests (vis.js specific fields)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__edge_has_required_fields(self):                                         # Test edge has vis.js required fields
        with Html_MGraph__To__VisJs(html_mgraph=self.html_mgraph_complex) as _:
            result = _.export()
            if result['edges']:
                edge = result['edges'][0]

                assert 'id'     in edge
                assert 'from'   in edge                                                       # vis.js uses 'from' not 'source'
                assert 'to'     in edge                                                       # vis.js uses 'to' not 'target'
                assert 'dashes' in edge                                                       # vis.js uses 'dashes' not 'dashed'
                assert 'color'  in edge

    def test__export__edge_has_predicate(self):                                               # Test edge has predicate metadata
        with Html_MGraph__To__VisJs(html_mgraph=self.html_mgraph_complex) as _:
            result = _.export()
            if result['edges']:
                edge = result['edges'][0]

                assert 'predicate'   in edge
                assert 'graphSource' in edge

    def test__export__edge_color_structure(self):                                             # Test edge color has vis.js structure
        with Html_MGraph__To__VisJs(html_mgraph=self.html_mgraph_complex) as _:
            result = _.export()
            if result['edges']:
                color = result['edges'][0]['color']

                assert 'color'     in color
                assert 'highlight' in color

    # ═══════════════════════════════════════════════════════════════════════════════
    # _map_shape Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___map_shape__known_shapes(self):                                                 # Test shape mapping for known shapes
        with Html_MGraph__To__VisJs(html_mgraph=self.html_mgraph_simple) as _:
            assert _._map_shape('box')     == 'box'
            assert _._map_shape('ellipse') == 'ellipse'
            assert _._map_shape('circle')  == 'circle'
            assert _._map_shape('diamond') == 'diamond'

    def test___map_shape__unknown_shape(self):                                                # Test shape mapping for unknown shape
        with Html_MGraph__To__VisJs(html_mgraph=self.html_mgraph_simple) as _:
            assert _._map_shape('unknown') == 'box'                                           # Default to box

    # ═══════════════════════════════════════════════════════════════════════════════
    # Complex Graph Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__complex_html(self):                                                     # Test export with complex HTML
        with Html_MGraph__To__VisJs(html_mgraph=self.html_mgraph_complex) as _:
            result = _.export()

            assert len(result['nodes']) >= 3                                                  # div, h1, p at minimum

    def test__export__with_config_filters(self):                                              # Test export respects config filters
        config = Html_MGraph__Render__Config()
        config.show_tag_nodes = False

        with Html_MGraph__To__VisJs(html_mgraph = self.html_mgraph_simple,
                                    config      = config                 ) as _:
            result = _.export()

            tag_nodes = [n for n in result['nodes'] if n['nodeType'] == 'tag']
            assert len(tag_nodes) == 0                                                        # Tag nodes filtered out

    def test__export__highlight_colors(self):                                                 # Test highlight colors are set
        with Html_MGraph__To__VisJs(html_mgraph=self.html_mgraph_simple) as _:
            result = _.export()
            node   = result['nodes'][0]

            highlight = node['color']['highlight']
            assert 'background' in highlight
            assert 'border'     in highlight