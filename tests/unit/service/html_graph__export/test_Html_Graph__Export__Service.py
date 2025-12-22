from unittest                                                                            import TestCase
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Stats                     import Schema__Graph__Stats
from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Html__Request       import Schema__Graph__From_Html__Request
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service import Html_Graph__Export__Service
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                        import Html_MGraph
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config        import Enum__Html_Render__Preset
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors        import Enum__Html_Render__Color_Scheme


class test_Html_Graph__Export__Service(TestCase):                                         # Tests for the underlying service

    @classmethod
    def setUpClass(cls):
        cls.service = Html_Graph__Export__Service()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Core Conversion Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__html_to_mgraph(self):                                                       # Test HTML to MGraph conversion
        html        = '<div><p>Test</p></div>'
        html_mgraph = self.service.html_to_mgraph(html)

        assert html_mgraph is not None
        assert type(html_mgraph) is Html_MGraph
        assert html_mgraph.document is not None

    def test__html_to_mgraph__has_body_graph(self):                                       # Test body graph is populated
        html        = '<div><p>Test</p></div>'
        html_mgraph = self.service.html_to_mgraph(html)

        assert html_mgraph.body_graph is not None

    def test__html_to_mgraph__has_attrs_graph(self):                                      # Test attrs graph is populated
        html        = '<div class="main"><p>Test</p></div>'
        html_mgraph = self.service.html_to_mgraph(html)

        assert html_mgraph.attrs_graph is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Transformation Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__list_transformations(self):                                                 # Test list_transformations returns list
        transformations = self.service.list_transformations()

        assert type(transformations) is list

    def test__html_to_mgraph_with_transformation(self):                                   # Test transformation pipeline
        html        = '<div><p>Test</p></div>'
        html_mgraph = self.service.html_to_mgraph_with_transformation(html, 'default')

        assert html_mgraph is not None
        assert type(html_mgraph) is Html_MGraph

    # ═══════════════════════════════════════════════════════════════════════════════
    # Config Creation Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__create_config__defaults(self):                                              # Test config creation with defaults
        request = Schema__Graph__From_Html__Request(html='<div></div>')
        config  = self.service.create_config(request)

        assert config.show_tag_nodes  == True
        assert config.show_attr_nodes == True
        assert config.show_text_nodes == True

    def test__create_config__custom(self):                                                # Test config creation with custom values
        request = Schema__Graph__From_Html__Request(html            = '<div></div>'                        ,
                                                    preset          = Enum__Html_Render__Preset.MINIMAL    ,
                                                    show_tag_nodes  = False                                ,
                                                    show_attr_nodes = False                                ,
                                                    color_scheme    = Enum__Html_Render__Color_Scheme.MONOCHROME)
        config  = self.service.create_config(request)

        assert config.show_tag_nodes  == False
        assert config.show_attr_nodes == False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Stats Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_stats(self):                                                            # Test stats generation
        html_mgraph = self.service.html_to_mgraph('<div><p>Hello</p></div>')
        stats       = self.service.get_stats(html_mgraph)

        assert type(stats) is Schema__Graph__Stats
        assert stats.total_nodes > 0

    def test__get_stats__aggregates_from_all_graphs(self):                                # Test stats aggregates from multi-graph
        html_mgraph = self.service.html_to_mgraph('<div class="main"><p>Hello</p></div>')
        stats       = self.service.get_stats(html_mgraph)

        assert stats.total_nodes   >= 0
        assert stats.total_edges   >= 0
        assert stats.element_nodes >= 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # DOT Export Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__to_dot(self):                                                               # Test DOT export
        request = Schema__Graph__From_Html__Request(html='<div>Test</div>')
        result  = self.service.to_dot(request)

        assert result.dot is not None
        assert 'digraph' in result.dot
        assert result.dot_size > 0

    def test__to_dot__with_transformation(self):                                          # Test DOT export with transformation
        request = Schema__Graph__From_Html__Request(html='<div>Test</div>')
        result  = self.service.to_dot(request, transformation='default')

        assert result.dot is not None
        assert result.transformation == 'default'

    # ═══════════════════════════════════════════════════════════════════════════════
    # vis.js Export Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__to_visjs(self):                                                             # Test vis.js export
        request = Schema__Graph__From_Html__Request(html='<div>Test</div>')
        result  = self.service.to_visjs(request)

        assert type(result)   is dict
        assert 'nodes'        in result
        assert 'edges'        in result
        assert 'stats'        in result
        assert 'duration'     in result
        assert result['format'] == 'visjs'

    def test__to_visjs__nodes_format(self):                                               # Test vis.js nodes have correct format
        request = Schema__Graph__From_Html__Request(html='<div>Test</div>')
        result  = self.service.to_visjs(request)

        assert len(result['nodes']) > 0
        node = result['nodes'][0]
        assert 'id'    in node
        assert 'label' in node

    # ═══════════════════════════════════════════════════════════════════════════════
    # D3.js Export Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__to_d3(self):                                                                # Test D3.js export
        request = Schema__Graph__From_Html__Request(html='<div>Test</div>')
        result  = self.service.to_d3(request)

        assert type(result)   is dict
        assert 'nodes'        in result
        assert 'links'        in result                                                   # D3 uses 'links'
        assert 'stats'        in result
        assert 'duration'     in result
        assert result['format'] == 'd3'

    def test__to_d3__links_format(self):                                                  # Test D3 links have correct format
        request = Schema__Graph__From_Html__Request(html='<div><p>Test</p></div>')
        result  = self.service.to_d3(request)

        if result['links']:
            link = result['links'][0]
            assert 'source' in link
            assert 'target' in link

    # ═══════════════════════════════════════════════════════════════════════════════
    # Cytoscape.js Export Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__to_cytoscape(self):                                                         # Test Cytoscape.js export
        request = Schema__Graph__From_Html__Request(html='<div>Test</div>')
        result  = self.service.to_cytoscape(request)

        assert type(result)   is dict
        assert 'elements'     in result
        assert 'stats'        in result
        assert 'duration'     in result
        assert result['format'] == 'cytoscape'

    def test__to_cytoscape__elements_format(self):                                        # Test Cytoscape elements have correct format
        request = Schema__Graph__From_Html__Request(html='<div>Test</div>')
        result  = self.service.to_cytoscape(request)

        elements = result['elements']
        assert 'nodes' in elements
        assert 'edges' in elements

    # ═══════════════════════════════════════════════════════════════════════════════
    # Mermaid Export Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__to_mermaid(self):                                                           # Test Mermaid export
        request = Schema__Graph__From_Html__Request(html='<div>Test</div>')
        result  = self.service.to_mermaid(request)

        assert type(result)     is dict
        assert 'mermaid'        in result
        assert 'mermaid_size'   in result
        assert 'stats'          in result
        assert 'duration'       in result
        assert result['format'] == 'mermaid'

    def test__to_mermaid__valid_syntax(self):                                             # Test Mermaid output is valid syntax
        request = Schema__Graph__From_Html__Request(html='<div>Test</div>')
        result  = self.service.to_mermaid(request)

        assert result['mermaid'].startswith('flowchart TB')

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tree Export Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__to_tree(self):                                                              # Test tree export
        request = Schema__Graph__From_Html__Request(html='<div>Test</div>')
        result  = self.service.to_tree(request)

        assert type(result)   is dict
        assert 'tree'         in result
        assert 'rootId'       in result
        assert 'stats'        in result
        assert 'duration'     in result
        assert result['format'] == 'tree'

    def test__to_tree__has_structure(self):                                               # Test tree has hierarchical structure
        request = Schema__Graph__From_Html__Request(html='<div><p>Test</p></div>')
        result  = self.service.to_tree(request)

        tree = result['tree']
        assert 'id'       in tree
        assert 'value'    in tree
        assert 'children' in tree

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tree Text Export Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__to_tree_text(self):                                                         # Test tree text export
        request = Schema__Graph__From_Html__Request(html='<div>Test</div>')
        result  = self.service.to_tree_text(request)

        assert type(result)     is dict
        assert 'tree_text'      in result
        assert 'tree_text_size' in result
        assert 'rootId'         in result
        assert 'stats'          in result
        assert 'duration'       in result
        assert result['format'] == 'tree_text'

    def test__to_tree_text__is_string(self):                                              # Test tree text is formatted string
        request = Schema__Graph__From_Html__Request(html='<div>Test</div>')
        result  = self.service.to_tree_text(request)

        assert type(result['tree_text']) is str
        assert result['tree_text_size'] == len(result['tree_text'])