from unittest                                                                             import TestCase
from mgraph_ai_service_html_graph.fast_api.routes.Routes__Graph                           import Routes__Graph, TAG__ROUTES_GRAPH, ROUTES_PATHS__GRAPH
from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Html__Request        import Schema__Graph__From_Html__Request
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service  import Html_Graph__Export__Service
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config         import Enum__Html_Render__Preset


class test_Routes__Graph__Native_Exports(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.routes_graph = Routes__Graph()
        cls.simple_html  = '<div><p>Hello World</p></div>'
        cls.complex_html = '<div class="main" id="content"><h1>Title</h1><p>Paragraph</p></div>'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def to_visjs(self, request, transformation='default'):
        return self.routes_graph.from_html_to_transformation(engine='visjs', transformation=transformation, request=request)

    def to_d3(self, request, transformation='default'):
        return self.routes_graph.from_html_to_transformation(engine='d3', transformation=transformation, request=request)

    def to_cytoscape(self, request, transformation='default'):
        return self.routes_graph.from_html_to_transformation(engine='cytoscape', transformation=transformation, request=request)

    def to_mermaid(self, request, transformation='default'):
        return self.routes_graph.from_html_to_transformation(engine='mermaid', transformation=transformation, request=request)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                   # Test auto-initialization
        with Routes__Graph() as _:
            assert type(_)                is Routes__Graph
            assert _.tag                  == TAG__ROUTES_GRAPH
            assert type(_.graph_service)  is Html_Graph__Export__Service

    def test__routes_paths__includes_transformation_pattern(self):                            # Test route paths include transformation pattern
        assert f'/{TAG__ROUTES_GRAPH}/transformations'                            in ROUTES_PATHS__GRAPH
        assert f'/{TAG__ROUTES_GRAPH}/from/html/to/{{engine}}/{{transformation}}' in ROUTES_PATHS__GRAPH
        assert f'/{TAG__ROUTES_GRAPH}/from/url/to/{{engine}}/{{transformation}}'  in ROUTES_PATHS__GRAPH

    # ═══════════════════════════════════════════════════════════════════════════════
    # from_html_to_transformation (visjs) Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__from_html_to_visjs__simple(self):                                               # Test basic vis.js conversion
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_visjs(request)

        assert type(result) is dict
        assert 'nodes' in result
        assert 'edges' in result
        assert 'stats' in result
        assert result['format'] == 'visjs'

    def test__from_html_to_visjs__nodes_format(self):                                         # Test vis.js nodes have correct format
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_visjs(request)

        assert len(result['nodes']) > 0
        node = result['nodes'][0]
        assert 'id'       in node
        assert 'label'    in node
        assert 'color'    in node
        assert 'nodeType' in node

    def test__from_html_to_visjs__edges_format(self):                                         # Test vis.js edges have correct format
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_visjs(request)

        assert len(result['edges']) > 0
        edge = result['edges'][0]
        assert 'from'      in edge
        assert 'to'        in edge
        assert 'predicate' in edge

    def test__from_html_to_visjs__with_preset(self):                                          # Test vis.js with preset
        request = Schema__Graph__From_Html__Request(html   = self.simple_html                     ,
                                                    preset = Enum__Html_Render__Preset.FULL_DETAIL)
        result  = self.to_visjs(request)

        assert len(result['nodes']) > 0

    def test__from_html_to_visjs__hide_tag_nodes(self):                                       # Test hiding tag nodes
        request = Schema__Graph__From_Html__Request(html           = self.simple_html,
                                                    show_tag_nodes = False           )
        result  = self.to_visjs(request)

        tag_nodes = [n for n in result['nodes'] if n['nodeType'] == 'tag']
        assert len(tag_nodes) == 0

    def test__from_html_to_visjs__with_transformation(self):                                  # Test vis.js with transformation
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_visjs(request, transformation='elements_only')

        assert type(result) is dict
        assert 'transformation' in result
        assert result['transformation'] == 'elements_only'

    # ═══════════════════════════════════════════════════════════════════════════════
    # from_html_to_transformation (d3) Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__from_html_to_d3__simple(self):                                                  # Test basic D3 conversion
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_d3(request)

        assert type(result) is dict
        assert 'nodes' in result
        assert 'links' in result                                                              # D3 uses 'links'
        assert 'stats' in result
        assert result['format'] == 'd3'

    def test__from_html_to_d3__nodes_format(self):                                            # Test D3 nodes have correct format
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_d3(request)

        assert len(result['nodes']) > 0
        node = result['nodes'][0]
        assert 'id'       in node
        assert 'label'    in node
        assert 'color'    in node
        assert 'radius'   in node
        assert 'nodeType' in node

    def test__from_html_to_d3__links_format(self):                                            # Test D3 links have correct format
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_d3(request)

        assert len(result['links']) > 0
        link = result['links'][0]
        assert 'source'    in link
        assert 'target'    in link
        assert 'predicate' in link
        assert 'width'     in link

    def test__from_html_to_d3__hide_attr_nodes(self):                                         # Test hiding attr nodes
        request = Schema__Graph__From_Html__Request(html            = self.complex_html,
                                                    show_attr_nodes = False            )
        result  = self.to_d3(request)

        attr_nodes = [n for n in result['nodes'] if n['nodeType'] == 'attr']
        assert len(attr_nodes) == 0

    def test__from_html_to_d3__with_transformation(self):                                     # Test D3 with transformation
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_d3(request, transformation='body_only')

        assert type(result) is dict
        assert 'transformation' in result
        assert result['transformation'] == 'body_only'

    # ═══════════════════════════════════════════════════════════════════════════════
    # from_html_to_transformation (cytoscape) Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__from_html_to_cytoscape__simple(self):                                           # Test basic Cytoscape conversion
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_cytoscape(request)

        assert type(result) is dict
        assert 'elements' in result
        assert 'nodes' in result['elements']
        assert 'edges' in result['elements']
        assert 'stats' in result
        assert result['format'] == 'cytoscape'

    def test__from_html_to_cytoscape__nodes_format(self):                                     # Test Cytoscape nodes have correct format
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_cytoscape(request)

        assert len(result['elements']['nodes']) > 0
        node = result['elements']['nodes'][0]
        assert 'data'  in node
        assert 'group' in node
        assert node['group'] == 'nodes'
        assert 'id'       in node['data']
        assert 'nodeType' in node['data']

    def test__from_html_to_cytoscape__edges_format(self):                                     # Test Cytoscape edges have correct format
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_cytoscape(request)

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
        result  = self.to_cytoscape(request)

        text_nodes = [n for n in result['elements']['nodes']
                     if n['data']['nodeType'] == 'text']
        assert len(text_nodes) == 0

    def test__from_html_to_cytoscape__with_transformation(self):                              # Test Cytoscape with transformation
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_cytoscape(request, transformation='collapse_text')

        assert type(result) is dict
        assert 'transformation' in result
        assert result['transformation'] == 'collapse_text'

    # ═══════════════════════════════════════════════════════════════════════════════
    # from_html_to_transformation (mermaid) Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__from_html_to_mermaid__simple(self):                                             # Test basic Mermaid conversion
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_mermaid(request)

        assert type(result) is dict
        assert 'mermaid' in result
        assert 'mermaid_size' in result
        assert 'stats' in result
        assert result['format'] == 'mermaid'

    def test__from_html_to_mermaid__is_valid_mermaid(self):                                   # Test Mermaid output is valid
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_mermaid(request)

        mermaid = result['mermaid']
        assert type(mermaid) is str
        assert mermaid.startswith('flowchart TB')
        assert '-->' in mermaid or '-.->' in mermaid

    def test__from_html_to_mermaid__size_is_accurate(self):                                   # Test mermaid_size is accurate
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_mermaid(request)

        assert result['mermaid_size'] == len(result['mermaid'])

    def test__from_html_to_mermaid__with_preset(self):                                        # Test Mermaid with preset
        request = Schema__Graph__From_Html__Request(html   = self.simple_html                        ,
                                                    preset = Enum__Html_Render__Preset.STRUCTURE_ONLY)
        result  = self.to_mermaid(request)

        assert 'flowchart TB' in result['mermaid']

    def test__from_html_to_mermaid__with_transformation(self):                                # Test Mermaid with transformation
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_mermaid(request, transformation='elements_only')

        assert type(result) is dict
        assert 'transformation' in result
        assert result['transformation'] == 'elements_only'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Transformations List Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__transformations__returns_list(self):                                            # Test transformations endpoint
        result = self.routes_graph.transformations()

        assert type(result) is list
        assert len(result) >= 1                                                               # At least 'default'

    def test__transformations__has_required_fields(self):                                     # Test transformation metadata
        result = self.routes_graph.transformations()

        for transformation in result:
            assert 'name'        in transformation
            assert 'label'       in transformation
            assert 'description' in transformation

    def test__transformations__includes_default(self):                                        # Test default transformation exists
        result = self.routes_graph.transformations()
        names  = [t['name'] for t in result]

        assert 'default' in names

    def test__transformations__includes_builtin_transforms(self):                             # Test built-in transformations exist
        result = self.routes_graph.transformations()
        names  = [t['name'] for t in result]

        assert 'elements_only' in names
        assert 'body_only'     in names
        assert 'collapse_text' in names

    # ═══════════════════════════════════════════════════════════════════════════════
    # Stats Tests (common to all formats)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__native_exports__have_stats(self):                                               # Test all native exports include stats
        request = Schema__Graph__From_Html__Request(html=self.simple_html)

        visjs_result     = self.to_visjs(request)
        d3_result        = self.to_d3(request)
        cytoscape_result = self.to_cytoscape(request)
        mermaid_result   = self.to_mermaid(request)

        assert 'stats' in visjs_result
        assert 'stats' in d3_result
        assert 'stats' in cytoscape_result
        assert 'stats' in mermaid_result

    def test__native_exports__have_duration(self):                                            # Test all native exports include duration
        request = Schema__Graph__From_Html__Request(html=self.simple_html)

        visjs_result     = self.to_visjs(request)
        d3_result        = self.to_d3(request)
        cytoscape_result = self.to_cytoscape(request)
        mermaid_result   = self.to_mermaid(request)

        assert 'duration' in visjs_result
        assert 'duration' in d3_result
        assert 'duration' in cytoscape_result
        assert 'duration' in mermaid_result

    def test__native_exports__have_transformation(self):                                      # Test all native exports include transformation
        request = Schema__Graph__From_Html__Request(html=self.simple_html)

        visjs_result     = self.to_visjs(request)
        d3_result        = self.to_d3(request)
        cytoscape_result = self.to_cytoscape(request)
        mermaid_result   = self.to_mermaid(request)

        assert 'transformation' in visjs_result
        assert 'transformation' in d3_result
        assert 'transformation' in cytoscape_result
        assert 'transformation' in mermaid_result

    # ═══════════════════════════════════════════════════════════════════════════════
    # Complex HTML Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__from_html_to_visjs__complex_html(self):                                         # Test vis.js with complex HTML
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.to_visjs(request)

        assert len(result['nodes']) >= 3                                                      # div, h1, p

    def test__from_html_to_d3__complex_html(self):                                            # Test D3 with complex HTML
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.to_d3(request)

        assert len(result['nodes']) >= 3

    def test__from_html_to_cytoscape__complex_html(self):                                     # Test Cytoscape with complex HTML
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.to_cytoscape(request)

        assert len(result['elements']['nodes']) >= 3

    def test__from_html_to_mermaid__complex_html(self):                                       # Test Mermaid with complex HTML
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.to_mermaid(request)

        # Complex HTML should produce larger Mermaid output
        assert result['mermaid_size'] > 100

    # ═══════════════════════════════════════════════════════════════════════════════
    # setup_routes Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__setup_routes(self):                                                             # Test setup_routes returns self
        routes = Routes__Graph()
        result = routes.setup_routes()

        assert result is routes