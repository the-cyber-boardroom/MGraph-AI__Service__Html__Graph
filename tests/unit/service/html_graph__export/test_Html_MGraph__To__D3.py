from unittest                                                                             import TestCase
from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from osbot_utils.utils.Objects                                                            import base_classes
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                         import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Export__Base    import Html_MGraph__Export__Base
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__D3          import Html_MGraph__To__D3
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Data__Extractor import Extracted__Node
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config         import Html_MGraph__Render__Config


class test_Html_MGraph__To__D3(TestCase):

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
        with Html_MGraph__To__D3(html_mgraph=self.html_mgraph_simple) as _:
            assert type(_)         is Html_MGraph__To__D3
            assert base_classes(_) == [Html_MGraph__Export__Base, Type_Safe, object]
            assert _.html_mgraph   is self.html_mgraph_simple
            assert _.config        is None

    def test__init__with_config(self):                                                        # Test initialization with config
        config = Html_MGraph__Render__Config()
        with Html_MGraph__To__D3(html_mgraph = self.html_mgraph_simple,
                                 config      = config                 ) as _:
            assert _.config is config

    # ═══════════════════════════════════════════════════════════════════════════════
    # export Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__returns_dict(self):                                                     # Test export returns dict
        with Html_MGraph__To__D3(html_mgraph=self.html_mgraph_simple) as _:
            result = _.export()

            assert type(result) is dict
            assert 'nodes'  in result
            assert 'links'  in result                                                         # D3 uses 'links' not 'edges'
            assert 'rootId' in result

    def test__export__nodes_is_list(self):                                                    # Test nodes is a list
        with Html_MGraph__To__D3(html_mgraph=self.html_mgraph_simple) as _:
            result = _.export()

            assert type(result['nodes']) is list
            assert len(result['nodes']) > 0

    def test__export__links_is_list(self):                                                    # Test links is a list
        with Html_MGraph__To__D3(html_mgraph=self.html_mgraph_complex) as _:
            result = _.export()

            assert type(result['links']) is list

    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Format Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__node_has_required_fields(self):                                         # Test node has D3 required fields
        with Html_MGraph__To__D3(html_mgraph=self.html_mgraph_simple) as _:
            result = _.export()
            node   = result['nodes'][0]

            assert 'id'        in node
            assert 'label'     in node
            assert 'color'     in node
            assert 'fontColor' in node
            assert 'radius'    in node

    def test__export__node_has_semantic_metadata(self):                                       # Test node has semantic metadata
        with Html_MGraph__To__D3(html_mgraph=self.html_mgraph_simple) as _:
            result = _.export()
            node   = result['nodes'][0]

            assert 'nodeType'    in node
            assert 'domPath'     in node
            assert 'category'    in node
            assert 'depth'       in node
            assert 'graphSource' in node

    def test__export__node_radius_is_positive(self):                                          # Test node radius is positive
        with Html_MGraph__To__D3(html_mgraph=self.html_mgraph_simple) as _:
            result = _.export()

            for node in result['nodes']:
                assert node['radius'] > 0

    def test__export__node_types_correct(self):                                               # Test node types are valid
        with Html_MGraph__To__D3(html_mgraph=self.html_mgraph_simple) as _:
            result = _.export()

            valid_types = {'element', 'tag', 'attr', 'text', 'script', 'style'}
            for node in result['nodes']:
                assert node['nodeType'] in valid_types

    # ═══════════════════════════════════════════════════════════════════════════════
    # Link Format Tests (D3 terminology)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__link_has_required_fields(self):                                         # Test link has D3 required fields
        with Html_MGraph__To__D3(html_mgraph=self.html_mgraph_complex) as _:
            result = _.export()
            if result['links']:
                link = result['links'][0]

                assert 'source' in link
                assert 'target' in link
                assert 'color'  in link
                assert 'dashed' in link
                assert 'width'  in link

    def test__export__link_has_predicate(self):                                               # Test link has predicate metadata
        with Html_MGraph__To__D3(html_mgraph=self.html_mgraph_complex) as _:
            result = _.export()
            if result['links']:
                link = result['links'][0]

                assert 'predicate'   in link
                assert 'graphSource' in link

    def test__export__link_width_varies_by_predicate(self):                                   # Test child links have different width
        with Html_MGraph__To__D3(html_mgraph=self.html_mgraph_complex) as _:
            result = _.export()

            child_links = [l for l in result['links'] if l['predicate'] == 'child']
            other_links = [l for l in result['links'] if l['predicate'] != 'child']

            if child_links:
                for link in child_links:
                    assert link['width'] == 2                                                 # Child edges are thicker

            if other_links:
                for link in other_links:
                    assert link['width'] == 1                                                 # Other edges are thinner

    # ═══════════════════════════════════════════════════════════════════════════════
    # _calculate_radius Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___calculate_radius__element(self):                                               # Test radius calculation for element
        with Html_MGraph__To__D3(html_mgraph=self.html_mgraph_simple) as _:
            node   = Extracted__Node(id='n1', node_type='element', label='<div>')
            radius = _._calculate_radius(node)
            assert radius >= 25                                                               # Base element radius

    def test___calculate_radius__tag(self):                                                   # Test radius calculation for tag
        with Html_MGraph__To__D3(html_mgraph=self.html_mgraph_simple) as _:
            node   = Extracted__Node(id='n1', node_type='tag', label='<div>')
            radius = _._calculate_radius(node)
            assert radius >= 20                                                               # Base tag radius

    def test___calculate_radius__longer_label(self):                                          # Test radius increases with label length
        with Html_MGraph__To__D3(html_mgraph=self.html_mgraph_simple) as _:
            short_node = Extracted__Node(id='n1', node_type='element', label='a')
            long_node  = Extracted__Node(id='n2', node_type='element', label='a' * 50)

            short_radius = _._calculate_radius(short_node)
            long_radius  = _._calculate_radius(long_node)

            assert long_radius > short_radius                                                 # Longer label = larger radius

    # ═══════════════════════════════════════════════════════════════════════════════
    # Complex Graph Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__complex_html(self):                                                     # Test export with complex HTML
        with Html_MGraph__To__D3(html_mgraph=self.html_mgraph_complex) as _:
            result = _.export()

            assert len(result['nodes']) >= 3                                                  # div, h1, p at minimum

    def test__export__with_config_filters(self):                                              # Test export respects config filters
        config = Html_MGraph__Render__Config()
        config.show_tag_nodes = False

        with Html_MGraph__To__D3(html_mgraph = self.html_mgraph_simple,
                                 config      = config                 ) as _:
            result = _.export()

            tag_nodes = [n for n in result['nodes'] if n['nodeType'] == 'tag']
            assert len(tag_nodes) == 0                                                        # Tag nodes filtered out