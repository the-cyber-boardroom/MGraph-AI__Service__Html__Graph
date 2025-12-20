from unittest                                                                             import TestCase
from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from osbot_utils.utils.Objects                                                            import base_classes
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Stats                      import Schema__Graph__Stats
from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Html__Request        import Schema__Graph__From_Html__Request
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service  import Html_Graph__Export__Service
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph                          import Html_MGraph
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config         import Html_MGraph__Render__Config, Enum__Html_Render__Preset
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors         import Enum__Html_Render__Color_Scheme


class test_Html_Graph__Export__Service__Native_Exports(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service      = Html_Graph__Export__Service()
        cls.simple_html  = '<div><p>Hello World</p></div>'
        cls.complex_html = '<div class="main" id="content"><h1>Title</h1><p>Paragraph</p></div>'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                   # Test auto-initialization
        with Html_Graph__Export__Service() as _:
            assert type(_)         is Html_Graph__Export__Service
            assert base_classes(_) == [Type_Safe, object]

    # ═══════════════════════════════════════════════════════════════════════════════
    # html_to_mgraph Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__html_to_mgraph(self):                                                           # Test HTML to MGraph conversion
        html_mgraph = self.service.html_to_mgraph(self.simple_html)

        assert type(html_mgraph) is Html_MGraph
        assert html_mgraph.mgraph is not None

    def test__html_to_mgraph__complex(self):                                                  # Test complex HTML conversion
        html_mgraph = self.service.html_to_mgraph(self.complex_html)

        stats = html_mgraph.stats()
        assert stats['element_nodes'] >= 3                                                    # div, h1, p

    # ═══════════════════════════════════════════════════════════════════════════════
    # create_config Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__create_config__defaults(self):                                                  # Test config creation with defaults
        request = Schema__Graph__From_Html__Request(html='<div></div>')
        config  = self.service.create_config(request)

        assert type(config) is Html_MGraph__Render__Config
        assert config.show_tag_nodes  == True
        assert config.show_attr_nodes == True
        assert config.show_text_nodes == True

    def test__create_config__custom(self):                                                    # Test config creation with custom values
        request = Schema__Graph__From_Html__Request(html            = '<div></div>'                        ,
                                                    preset          = Enum__Html_Render__Preset.MINIMAL    ,
                                                    show_tag_nodes  = False                                ,
                                                    show_attr_nodes = False                                ,
                                                    color_scheme    = Enum__Html_Render__Color_Scheme.MONOCHROME)
        config = self.service.create_config(request)

        assert config.show_tag_nodes  == False
        assert config.show_attr_nodes == False

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_stats Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_stats(self):                                                                # Test stats generation
        html_mgraph = self.service.html_to_mgraph(self.simple_html)
        stats       = self.service.get_stats(html_mgraph)

        assert type(stats) is Schema__Graph__Stats
        assert stats.total_nodes > 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # to_visjs Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__to_visjs__returns_dict(self):                                                   # Test to_visjs returns dict
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.service.to_visjs(request)

        assert type(result) is dict
        assert 'nodes'    in result
        assert 'edges'    in result
        assert 'stats'    in result
        assert 'duration' in result
        assert 'format'   in result

    def test__to_visjs__format_identifier(self):                                              # Test format identifier
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.service.to_visjs(request)

        assert result['format'] == 'visjs'

    def test__to_visjs__nodes_structure(self):                                                # Test nodes have vis.js structure
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.service.to_visjs(request)

        assert len(result['nodes']) > 0
        node = result['nodes'][0]
        assert 'id'       in node
        assert 'label'    in node
        assert 'color'    in node
        assert 'nodeType' in node

    def test__to_visjs__edges_structure(self):                                                # Test edges have vis.js structure
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.service.to_visjs(request)

        assert len(result['edges']) > 0
        edge = result['edges'][0]
        assert 'from'      in edge
        assert 'to'        in edge
        assert 'predicate' in edge

    # ═══════════════════════════════════════════════════════════════════════════════
    # to_d3 Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__to_d3__returns_dict(self):                                                      # Test to_d3 returns dict
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.service.to_d3(request)

        assert type(result) is dict
        assert 'nodes'    in result
        assert 'links'    in result                                                           # D3 uses 'links'
        assert 'stats'    in result
        assert 'duration' in result

    def test__to_d3__format_identifier(self):                                                 # Test format identifier
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.service.to_d3(request)

        assert result['format'] == 'd3'

    def test__to_d3__nodes_structure(self):                                                   # Test nodes have D3 structure
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.service.to_d3(request)

        assert len(result['nodes']) > 0
        node = result['nodes'][0]
        assert 'id'       in node
        assert 'label'    in node
        assert 'radius'   in node
        assert 'nodeType' in node

    def test__to_d3__links_structure(self):                                                   # Test links have D3 structure
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.service.to_d3(request)

        assert len(result['links']) > 0
        link = result['links'][0]
        assert 'source'    in link
        assert 'target'    in link
        assert 'width'     in link
        assert 'predicate' in link

    # ═══════════════════════════════════════════════════════════════════════════════
    # to_cytoscape Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__to_cytoscape__returns_dict(self):                                               # Test to_cytoscape returns dict
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.service.to_cytoscape(request)

        assert type(result) is dict
        assert 'elements' in result
        assert 'stats'    in result
        assert 'duration' in result

    def test__to_cytoscape__format_identifier(self):                                          # Test format identifier
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.service.to_cytoscape(request)

        assert result['format'] == 'cytoscape'

    def test__to_cytoscape__elements_structure(self):                                         # Test elements has nodes and edges
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.service.to_cytoscape(request)

        assert 'nodes' in result['elements']
        assert 'edges' in result['elements']

    def test__to_cytoscape__node_wrapper_structure(self):                                     # Test node has Cytoscape wrapper
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.service.to_cytoscape(request)

        node = result['elements']['nodes'][0]
        assert 'data'  in node
        assert 'group' in node
        assert node['group'] == 'nodes'

    def test__to_cytoscape__edge_wrapper_structure(self):                                     # Test edge has Cytoscape wrapper
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.service.to_cytoscape(request)

        edge = result['elements']['edges'][0]
        assert 'data'  in edge
        assert 'group' in edge
        assert edge['group'] == 'edges'

    # ═══════════════════════════════════════════════════════════════════════════════
    # to_mermaid Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__to_mermaid__returns_dict(self):                                                 # Test to_mermaid returns dict
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.service.to_mermaid(request)

        assert type(result) is dict
        assert 'mermaid'      in result
        assert 'mermaid_size' in result
        assert 'stats'        in result
        assert 'duration'     in result

    def test__to_mermaid__format_identifier(self):                                            # Test format identifier
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.service.to_mermaid(request)

        assert result['format'] == 'mermaid'

    def test__to_mermaid__is_string(self):                                                    # Test mermaid output is string
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.service.to_mermaid(request)

        assert type(result['mermaid']) is str

    def test__to_mermaid__starts_with_flowchart(self):                                        # Test starts with flowchart
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.service.to_mermaid(request)

        assert result['mermaid'].startswith('flowchart TB')

    def test__to_mermaid__size_is_accurate(self):                                             # Test size matches string length
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.service.to_mermaid(request)

        assert result['mermaid_size'] == len(result['mermaid'])

    # ═══════════════════════════════════════════════════════════════════════════════
    # Config Filter Tests (all formats)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__to_visjs__respects_hide_tag_nodes(self):                                        # Test vis.js respects config
        request = Schema__Graph__From_Html__Request(html           = self.simple_html,
                                                    show_tag_nodes = False           )
        result  = self.service.to_visjs(request)

        tag_nodes = [n for n in result['nodes'] if n['nodeType'] == 'tag']
        assert len(tag_nodes) == 0

    def test__to_d3__respects_hide_attr_nodes(self):                                          # Test D3 respects config
        request = Schema__Graph__From_Html__Request(html            = self.complex_html,
                                                    show_attr_nodes = False            )
        result  = self.service.to_d3(request)

        attr_nodes = [n for n in result['nodes'] if n['nodeType'] == 'attr']
        assert len(attr_nodes) == 0

    def test__to_cytoscape__respects_hide_text_nodes(self):                                   # Test Cytoscape respects config
        request = Schema__Graph__From_Html__Request(html            = self.simple_html,
                                                    show_text_nodes = False           )
        result  = self.service.to_cytoscape(request)

        text_nodes = [n for n in result['elements']['nodes']
                     if n['data']['nodeType'] == 'text']
        assert len(text_nodes) == 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # Duration Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__all_formats__have_duration(self):                                               # Test all formats include duration
        request = Schema__Graph__From_Html__Request(html=self.simple_html)

        visjs_result     = self.service.to_visjs(request)
        d3_result        = self.service.to_d3(request)
        cytoscape_result = self.service.to_cytoscape(request)
        mermaid_result   = self.service.to_mermaid(request)

        assert visjs_result['duration']     >= 0
        assert d3_result['duration']        >= 0
        assert cytoscape_result['duration'] >= 0
        assert mermaid_result['duration']   >= 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # Complex HTML Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__all_formats__handle_complex_html(self):                                         # Test all formats handle complex HTML
        request = Schema__Graph__From_Html__Request(html=self.complex_html)

        visjs_result     = self.service.to_visjs(request)
        d3_result        = self.service.to_d3(request)
        cytoscape_result = self.service.to_cytoscape(request)
        mermaid_result   = self.service.to_mermaid(request)

        assert len(visjs_result['nodes'])               >= 3
        assert len(d3_result['nodes'])                  >= 3
        assert len(cytoscape_result['elements']['nodes']) >= 3
        assert len(mermaid_result['mermaid'])           > 100
