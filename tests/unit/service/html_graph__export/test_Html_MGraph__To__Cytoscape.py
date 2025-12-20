from unittest                                                                             import TestCase
from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from osbot_utils.utils.Objects                                                            import base_classes
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph                          import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__Cytoscape   import Html_MGraph__To__Cytoscape
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config         import Html_MGraph__Render__Config


class test_Html_MGraph__To__Cytoscape(TestCase):

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
        with Html_MGraph__To__Cytoscape(mgraph=self.html_mgraph_simple.mgraph) as _:
            assert type(_)         is Html_MGraph__To__Cytoscape
            assert base_classes(_) == [Type_Safe, object]
            assert _.mgraph        is self.html_mgraph_simple.mgraph
            assert _.config        is None

    def test__init__with_config(self):                                                        # Test initialization with config
        config = Html_MGraph__Render__Config()
        with Html_MGraph__To__Cytoscape(mgraph = self.html_mgraph_simple.mgraph,
                                        config = config                        ) as _:
            assert _.config is config

    # ═══════════════════════════════════════════════════════════════════════════════
    # export Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__returns_dict(self):                                                     # Test export returns dict
        with Html_MGraph__To__Cytoscape(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()

            assert type(result) is dict
            assert 'elements' in result
            assert 'rootId'   in result

    def test__export__elements_has_nodes_and_edges(self):                                     # Test elements contains nodes and edges
        with Html_MGraph__To__Cytoscape(mgraph=self.html_mgraph_simple.mgraph) as _:
            result   = _.export()
            elements = result['elements']

            assert 'nodes' in elements
            assert 'edges' in elements

    def test__export__nodes_is_list(self):                                                    # Test nodes is a list
        with Html_MGraph__To__Cytoscape(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()

            assert type(result['elements']['nodes']) is list
            assert len(result['elements']['nodes']) > 0

    def test__export__edges_is_list(self):                                                    # Test edges is a list
        with Html_MGraph__To__Cytoscape(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()

            assert type(result['elements']['edges']) is list
            assert len(result['elements']['edges']) > 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Format Tests (Cytoscape uses {data: {...}, group: 'nodes'} wrapper)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__node_has_cytoscape_structure(self):                                     # Test node has Cytoscape wrapper structure
        with Html_MGraph__To__Cytoscape(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()
            node   = result['elements']['nodes'][0]

            assert 'data'  in node
            assert 'group' in node
            assert node['group'] == 'nodes'

    def test__export__node_data_has_required_fields(self):                                    # Test node data has required fields
        with Html_MGraph__To__Cytoscape(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()
            data   = result['elements']['nodes'][0]['data']

            assert 'id'          in data
            assert 'label'       in data
            assert 'color'       in data
            assert 'fontColor'   in data
            assert 'borderColor' in data

    def test__export__node_data_has_semantic_metadata(self):                                  # Test node data has semantic metadata
        with Html_MGraph__To__Cytoscape(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()
            data   = result['elements']['nodes'][0]['data']

            assert 'nodeType' in data
            assert 'domPath'  in data
            assert 'category' in data
            assert 'depth'    in data

    def test__export__node_types_correct(self):                                               # Test node types are valid
        with Html_MGraph__To__Cytoscape(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()

            valid_types = {'element', 'tag', 'attr', 'text'}
            for node in result['elements']['nodes']:
                assert node['data']['nodeType'] in valid_types

    # ═══════════════════════════════════════════════════════════════════════════════
    # Edge Format Tests (Cytoscape uses {data: {...}, group: 'edges'} wrapper)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__edge_has_cytoscape_structure(self):                                     # Test edge has Cytoscape wrapper structure
        with Html_MGraph__To__Cytoscape(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()
            edge   = result['elements']['edges'][0]

            assert 'data'  in edge
            assert 'group' in edge
            assert edge['group'] == 'edges'

    def test__export__edge_data_has_required_fields(self):                                    # Test edge data has required fields
        with Html_MGraph__To__Cytoscape(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()
            data   = result['elements']['edges'][0]['data']

            assert 'id'     in data
            assert 'source' in data
            assert 'target' in data
            assert 'color'  in data
            assert 'dashed' in data

    def test__export__edge_data_has_predicate(self):                                          # Test edge data has predicate
        with Html_MGraph__To__Cytoscape(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()
            data   = result['elements']['edges'][0]['data']

            assert 'predicate' in data

    def test__export__edge_references_valid_nodes(self):                                      # Test edge references valid node IDs
        with Html_MGraph__To__Cytoscape(mgraph=self.html_mgraph_simple.mgraph) as _:
            result   = _.export()
            node_ids = {n['data']['id'] for n in result['elements']['nodes']}

            for edge in result['elements']['edges']:
                assert edge['data']['source'] in node_ids
                assert edge['data']['target'] in node_ids

    # ═══════════════════════════════════════════════════════════════════════════════
    # Complex Graph Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__complex_html(self):                                                     # Test export with complex HTML
        with Html_MGraph__To__Cytoscape(mgraph=self.html_mgraph_complex.mgraph) as _:
            result = _.export()

            assert len(result['elements']['nodes']) >= 3                                      # div, h1, p at minimum
            assert len(result['elements']['edges']) >= 2                                      # At least parent-child edges

    def test__export__with_config_filters(self):                                              # Test export respects config filters
        config = Html_MGraph__Render__Config()
        config.show_tag_nodes = False

        with Html_MGraph__To__Cytoscape(mgraph = self.html_mgraph_simple.mgraph,
                                        config = config                        ) as _:
            result = _.export()

            tag_nodes = [n for n in result['elements']['nodes']
                        if n['data']['nodeType'] == 'tag']
            assert len(tag_nodes) == 0                                                        # Tag nodes filtered out

    def test__export__all_nodes_have_group(self):                                             # Test all nodes have correct group
        with Html_MGraph__To__Cytoscape(mgraph=self.html_mgraph_complex.mgraph) as _:
            result = _.export()

            for node in result['elements']['nodes']:
                assert node['group'] == 'nodes'

    def test__export__all_edges_have_group(self):                                             # Test all edges have correct group
        with Html_MGraph__To__Cytoscape(mgraph=self.html_mgraph_complex.mgraph) as _:
            result = _.export()

            for edge in result['elements']['edges']:
                assert edge['group'] == 'edges'


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
