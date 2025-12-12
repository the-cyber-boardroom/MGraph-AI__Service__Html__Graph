from unittest                                                                             import TestCase
from mgraph_ai_service_html_graph.fast_api.routes.Routes__Graph                           import Routes__Graph, TAG__ROUTES_GRAPH, ROUTES_PATHS__GRAPH
from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Html__Request        import Schema__Graph__From_Html__Request
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service  import Html_Graph__Export__Service
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config         import Enum__Html_Render__Preset
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors         import Enum__Html_Render__Color_Scheme


class test_Routes__Graph__Native_Exports(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.routes_graph = Routes__Graph()
        cls.simple_html  = '<div><p>Hello World</p></div>'
        cls.complex_html = '<div class="main" id="content"><h1>Title</h1><p>Paragraph</p></div>'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                   # Test auto-initialization
        with Routes__Graph() as _:
            assert type(_)                is Routes__Graph
            assert _.tag                  == TAG__ROUTES_GRAPH
            assert type(_.graph_service)  is Html_Graph__Export__Service

    def test__routes_paths__includes_native_formats(self):                                    # Test route paths include native formats
        assert '/graph/from/html/to/visjs'     in ROUTES_PATHS__GRAPH
        assert '/graph/from/html/to/d3'        in ROUTES_PATHS__GRAPH
        assert '/graph/from/html/to/cytoscape' in ROUTES_PATHS__GRAPH
        assert '/graph/from/html/to/mermaid'   in ROUTES_PATHS__GRAPH

    def test__routes_paths__includes_url_variants(self):                                      # Test URL variants are included
        assert '/graph/from/url/to/visjs'     in ROUTES_PATHS__GRAPH
        assert '/graph/from/url/to/d3'        in ROUTES_PATHS__GRAPH
        assert '/graph/from/url/to/cytoscape' in ROUTES_PATHS__GRAPH
        assert '/graph/from/url/to/mermaid'   in ROUTES_PATHS__GRAPH

    # ═══════════════════════════════════════════════════════════════════════════════
    # from__html__to__visjs Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__from_html_to_visjs__simple(self):                                               # Test basic vis.js conversion
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.routes_graph.from__html__to__visjs(request)

        assert type(result) is dict
        assert 'nodes' in result
        assert 'edges' in result
        assert 'stats' in result
        assert result['format'] == 'visjs'

    def test__from_html_to_visjs__nodes_format(self):                                         # Test vis.js nodes have correct format
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.routes_graph.from__html__to__visjs(request)

        assert len(result['nodes']) > 0
        node = result['nodes'][0]
        assert 'id'       in node
        assert 'label'    in node
        assert 'color'    in node
        assert 'nodeType' in node

    def test__from_html_to_visjs__edges_format(self):                                         # Test vis.js edges have correct format
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.routes_graph.from__html__to__visjs(request)

        assert len(result['edges']) > 0
        edge = result['edges'][0]
        assert 'from'      in edge
        assert 'to'        in edge
        assert 'predicate' in edge

    def test__from_html_to_visjs__with_preset(self):                                          # Test vis.js with preset
        request = Schema__Graph__From_Html__Request(html   = self.simple_html                     ,
                                                    preset = Enum__Html_Render__Preset.FULL_DETAIL)
        result  = self.routes_graph.from__html__to__visjs(request)

        assert len(result['nodes']) > 0

    def test__from_html_to_visjs__hide_tag_nodes(self):                                       # Test hiding tag nodes
        request = Schema__Graph__From_Html__Request(html           = self.simple_html,
                                                    show_tag_nodes = False           )
        result  = self.routes_graph.from__html__to__visjs(request)

        tag_nodes = [n for n in result['nodes'] if n['nodeType'] == 'tag']
        assert len(tag_nodes) == 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # from__html__to__d3 Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__from_html_to_d3__simple(self):                                                  # Test basic D3 conversion
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.routes_graph.from__html__to__d3(request)

        assert type(result) is dict
        assert 'nodes' in result
        assert 'links' in result                                                              # D3 uses 'links'
        assert 'stats' in result
        assert result['format'] == 'd3'

    def test__from_html_to_d3__nodes_format(self):                                            # Test D3 nodes have correct format
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.routes_graph.from__html__to__d3(request)

        assert len(result['nodes']) > 0
        node = result['nodes'][0]
        assert 'id'       in node
        assert 'label'    in node
        assert 'color'    in node
        assert 'radius'   in node
        assert 'nodeType' in node

    def test__from_html_to_d3__links_format(self):                                            # Test D3 links have correct format
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.routes_graph.from__html__to__d3(request)

        assert len(result['links']) > 0
        link = result['links'][0]
        assert 'source'    in link
        assert 'target'    in link
        assert 'predicate' in link
        assert 'width'     in link

    def test__from_html_to_d3__hide_attr_nodes(self):                                         # Test hiding attr nodes
        request = Schema__Graph__From_Html__Request(html            = self.complex_html,
                                                    show_attr_nodes = False            )
        result  = self.routes_graph.from__html__to__d3(request)

        attr_nodes = [n for n in result['nodes'] if n['nodeType'] == 'attr']
        assert len(attr_nodes) == 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # from__html__to__cytoscape Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__from_html_to_cytoscape__simple(self):                                           # Test basic Cytoscape conversion
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.routes_graph.from__html__to__cytoscape(request)

        assert type(result) is dict
        assert 'elements' in result
        assert 'nodes' in result['elements']
        assert 'edges' in result['elements']
        assert 'stats' in result
        assert result['format'] == 'cytoscape'

    def test__from_html_to_cytoscape__nodes_format(self):                                     # Test Cytoscape nodes have correct format
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.routes_graph.from__html__to__cytoscape(request)

        assert len(result['elements']['nodes']) > 0
        node = result['elements']['nodes'][0]
        assert 'data'  in node
        assert 'group' in node
        assert node['group'] == 'nodes'
        assert 'id'       in node['data']
        assert 'nodeType' in node['data']

    def test__from_html_to_cytoscape__edges_format(self):                                     # Test Cytoscape edges have correct format
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.routes_graph.from__html__to__cytoscape(request)

        assert len(result['elements']['edges']) > 0
        edge = result['elements']['edges'][0]
        assert 'data'  in edge
        assert 'group' in edge
        assert edge['group'] == 'edges'
        assert 'source'    in edge['data']
        assert 'target'    in edge['data']
        assert 'predicate' in edge['data']

    def test__from_html_to_cytoscape__hide_text_nodes(self):                                  # Test hiding text nodes
        request = Schema__Graph__From_Html__Request(html            = self.simple_html,
                                                    show_text_nodes = False           )
        result  = self.routes_graph.from__html__to__cytoscape(request)

        text_nodes = [n for n in result['elements']['nodes']
                     if n['data']['nodeType'] == 'text']
        assert len(text_nodes) == 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # from__html__to__mermaid Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__from_html_to_mermaid__simple(self):                                             # Test basic Mermaid conversion
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.routes_graph.from__html__to__mermaid(request)

        assert type(result) is dict
        assert 'mermaid' in result
        assert 'mermaid_size' in result
        assert 'stats' in result
        assert result['format'] == 'mermaid'

    def test__from_html_to_mermaid__is_valid_mermaid(self):                                   # Test Mermaid output is valid
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.routes_graph.from__html__to__mermaid(request)

        mermaid = result['mermaid']
        assert type(mermaid) is str
        assert mermaid.startswith('flowchart TB')
        assert '-->' in mermaid or '-.->' in mermaid

    def test__from_html_to_mermaid__size_is_accurate(self):                                   # Test mermaid_size is accurate
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.routes_graph.from__html__to__mermaid(request)

        assert result['mermaid_size'] == len(result['mermaid'])

    def test__from_html_to_mermaid__with_preset(self):                                        # Test Mermaid with preset
        request = Schema__Graph__From_Html__Request(html   = self.simple_html                        ,
                                                    preset = Enum__Html_Render__Preset.STRUCTURE_ONLY)
        result  = self.routes_graph.from__html__to__mermaid(request)

        assert 'flowchart TB' in result['mermaid']

    # ═══════════════════════════════════════════════════════════════════════════════
    # Stats Tests (common to all formats)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__native_exports__have_stats(self):                                               # Test all native exports include stats
        request = Schema__Graph__From_Html__Request(html=self.simple_html)

        visjs_result     = self.routes_graph.from__html__to__visjs(request)
        d3_result        = self.routes_graph.from__html__to__d3(request)
        cytoscape_result = self.routes_graph.from__html__to__cytoscape(request)
        mermaid_result   = self.routes_graph.from__html__to__mermaid(request)

        assert 'stats' in visjs_result
        assert 'stats' in d3_result
        assert 'stats' in cytoscape_result
        assert 'stats' in mermaid_result

    def test__native_exports__have_duration(self):                                            # Test all native exports include duration
        request = Schema__Graph__From_Html__Request(html=self.simple_html)

        visjs_result     = self.routes_graph.from__html__to__visjs(request)
        d3_result        = self.routes_graph.from__html__to__d3(request)
        cytoscape_result = self.routes_graph.from__html__to__cytoscape(request)
        mermaid_result   = self.routes_graph.from__html__to__mermaid(request)

        assert 'duration' in visjs_result
        assert 'duration' in d3_result
        assert 'duration' in cytoscape_result
        assert 'duration' in mermaid_result

    # ═══════════════════════════════════════════════════════════════════════════════
    # Complex HTML Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__from_html_to_visjs__complex_html(self):                                         # Test vis.js with complex HTML
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.routes_graph.from__html__to__visjs(request)

        assert len(result['nodes']) >= 3                                                      # div, h1, p

    def test__from_html_to_d3__complex_html(self):                                            # Test D3 with complex HTML
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.routes_graph.from__html__to__d3(request)

        assert len(result['nodes']) >= 3

    def test__from_html_to_cytoscape__complex_html(self):                                     # Test Cytoscape with complex HTML
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.routes_graph.from__html__to__cytoscape(request)

        assert len(result['elements']['nodes']) >= 3

    def test__from_html_to_mermaid__complex_html(self):                                       # Test Mermaid with complex HTML
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.routes_graph.from__html__to__mermaid(request)

        # Complex HTML should produce larger Mermaid output
        assert result['mermaid_size'] > 100

    # ═══════════════════════════════════════════════════════════════════════════════
    # setup_routes Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__setup_routes(self):                                                             # Test setup_routes returns self
        routes = Routes__Graph()
        result = routes.setup_routes()

        assert result is routes
