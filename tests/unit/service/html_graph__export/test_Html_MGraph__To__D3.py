from unittest                                                                             import TestCase
from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from osbot_utils.utils.Objects                                                            import base_classes
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph                          import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__D3          import Html_MGraph__To__D3
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Data__Extractor import Extracted__Node
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config         import Html_MGraph__Render__Config


class test_Html_MGraph__To__D3(TestCase):

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
        with Html_MGraph__To__D3(mgraph=self.html_mgraph_simple.mgraph) as _:
            assert type(_)         is Html_MGraph__To__D3
            assert base_classes(_) == [Type_Safe, object]
            assert _.mgraph        is self.html_mgraph_simple.mgraph
            assert _.config        is None

    def test__init__with_config(self):                                                        # Test initialization with config
        config = Html_MGraph__Render__Config()
        with Html_MGraph__To__D3(mgraph = self.html_mgraph_simple.mgraph,
                                 config = config                        ) as _:
            assert _.config is config

    # ═══════════════════════════════════════════════════════════════════════════════
    # export Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__returns_dict(self):                                                     # Test export returns dict
        with Html_MGraph__To__D3(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()

            assert type(result) is dict
            assert 'nodes'  in result
            assert 'links'  in result                                                         # D3 uses 'links' not 'edges'
            assert 'rootId' in result

    def test__export__nodes_is_list(self):                                                    # Test nodes is a list
        with Html_MGraph__To__D3(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()

            assert type(result['nodes']) is list
            assert len(result['nodes']) > 0

    def test__export__links_is_list(self):                                                    # Test links is a list
        with Html_MGraph__To__D3(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()

            assert type(result['links']) is list
            assert len(result['links']) > 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Format Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__node_has_required_fields(self):                                         # Test node has D3 required fields
        with Html_MGraph__To__D3(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()
            node   = result['nodes'][0]

            assert 'id'        in node
            assert 'label'     in node
            assert 'color'     in node
            assert 'fontColor' in node
            assert 'radius'    in node

    def test__export__node_has_semantic_metadata(self):                                       # Test node has semantic metadata
        with Html_MGraph__To__D3(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()
            node   = result['nodes'][0]

            assert 'nodeType' in node
            assert 'domPath'  in node
            assert 'category' in node
            assert 'depth'    in node

    def test__export__node_radius_is_positive(self):                                          # Test node radius is positive
        with Html_MGraph__To__D3(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()

            for node in result['nodes']:
                assert node['radius'] > 0

    def test__export__node_types_correct(self):                                               # Test node types are valid
        with Html_MGraph__To__D3(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()

            valid_types = {'element', 'tag', 'attr', 'text'}
            for node in result['nodes']:
                assert node['nodeType'] in valid_types

    # ═══════════════════════════════════════════════════════════════════════════════
    # Link Format Tests (D3 terminology)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__link_has_required_fields(self):                                         # Test link has D3 required fields
        with Html_MGraph__To__D3(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()
            link   = result['links'][0]

            assert 'source' in link
            assert 'target' in link
            assert 'color'  in link
            assert 'dashed' in link
            assert 'width'  in link

    def test__export__link_has_predicate(self):                                               # Test link has predicate metadata
        with Html_MGraph__To__D3(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()
            link   = result['links'][0]

            assert 'predicate' in link

    def test__export__link_references_valid_nodes(self):                                      # Test link references valid node IDs
        with Html_MGraph__To__D3(mgraph=self.html_mgraph_simple.mgraph) as _:
            result   = _.export()
            node_ids = {n['id'] for n in result['nodes']}

            for link in result['links']:
                assert link['source'] in node_ids
                assert link['target'] in node_ids

    def test__export__link_width_varies_by_predicate(self):                                   # Test child links have different width
        with Html_MGraph__To__D3(mgraph=self.html_mgraph_complex.mgraph) as _:
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
        with Html_MGraph__To__D3(mgraph=self.html_mgraph_simple.mgraph) as _:
            node   = Extracted__Node(id='n1', node_type='element', label='<div>')
            radius = _._calculate_radius(node)
            assert radius >= 25                                                               # Base element radius

    def test___calculate_radius__tag(self):                                                   # Test radius calculation for tag
        with Html_MGraph__To__D3(mgraph=self.html_mgraph_simple.mgraph) as _:
            node   = Extracted__Node(id='n1', node_type='tag', label='<div>')
            radius = _._calculate_radius(node)
            assert radius >= 20                                                               # Base tag radius

    def test___calculate_radius__longer_label(self):                                          # Test radius increases with label length
        with Html_MGraph__To__D3(mgraph=self.html_mgraph_simple.mgraph) as _:
            short_node = Extracted__Node(id='n1', node_type='element', label='a')
            long_node  = Extracted__Node(id='n2', node_type='element', label='a' * 50)

            short_radius = _._calculate_radius(short_node)
            long_radius  = _._calculate_radius(long_node)

            assert long_radius > short_radius                                                 # Longer label = larger radius

    # ═══════════════════════════════════════════════════════════════════════════════
    # Complex Graph Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__complex_html(self):                                                     # Test export with complex HTML
        with Html_MGraph__To__D3(mgraph=self.html_mgraph_complex.mgraph) as _:
            result = _.export()

            assert len(result['nodes']) >= 3                                                  # div, h1, p at minimum
            assert len(result['links']) >= 2                                                  # At least parent-child links

    def test__export__with_config_filters(self):                                              # Test export respects config filters
        config = Html_MGraph__Render__Config()
        config.show_tag_nodes = False

        with Html_MGraph__To__D3(mgraph = self.html_mgraph_simple.mgraph,
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
