# Test: Routes__Graph__Native_Exports
#
# Unit tests for the native graph export routes (VisJs, D3, Cytoscape, Mermaid).
# Updated to work with the new Html_Graph__Export__Service v1.4.0

from unittest                                                                             import TestCase
from mgraph_ai_service_html_graph.fast_api.routes.Routes__Graph                           import Routes__Graph, TAG__ROUTES_GRAPH, ROUTES_PATHS__GRAPH

from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Html__Request        import Schema__Graph__From_Html__Request

from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Schemas import Schema__Graph__D3__Response, Schema__Graph__Mermaid__Response, Schema__Graph__VisJs__Response, \
    Schema__Graph__Cytoscape__Response
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service  import Html_Graph__Export__Service
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict import Type_Safe__Dict
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List import Type_Safe__List


class test_Routes__Graph__Native_Exports(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.routes_graph = Routes__Graph()
        cls.simple_html  = '<html><body><div><p>Hello World</p></div></body></html>'
        cls.complex_html = '<html><body><div class="main" id="content"><h1>Title</h1><p>Paragraph</p></div></body></html>'

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

        assert type(result)        is Schema__Graph__VisJs__Response
        assert type(result.nodes)  is Type_Safe__List
        assert type(result.edges)  is Type_Safe__List
        #assert result.format       == 'visjs'

    def test__from_html_to_visjs__nodes_format(self):                                         # Test vis.js nodes have correct format
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_visjs(request)

        assert len(result.nodes) > 0
        node = result.nodes[0]
        assert 'id'    in node
        assert 'label' in node

    def test__from_html_to_visjs__edges_format(self):                                         # Test vis.js edges have correct format
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_visjs(request)

        if len(result.edges) > 0:
            edge = result.edges[0]
            assert 'from' in edge
            assert 'to'   in edge

    def test__from_html_to_visjs__with_transformation__structure_only(self):                  # Test vis.js with structure_only transformation
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_visjs(request, transformation='structure_only')

        assert type(result)           is Schema__Graph__VisJs__Response
        assert result.transformation  == 'structure_only'

    def test__from_html_to_visjs__with_transformation__clean(self):                           # Test vis.js with clean transformation
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_visjs(request, transformation='clean')

        assert type(result)          is Schema__Graph__VisJs__Response
        assert result.transformation == 'clean'

    def test__from_html_to_visjs__with_transformation__semantic(self):                        # Test vis.js with semantic transformation
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_visjs(request, transformation='semantic')

        assert type(result)          is Schema__Graph__VisJs__Response
        assert result.transformation == 'semantic'

    def test__from_html_to_visjs__with_transformation__body_only(self):                       # Test vis.js with body_only transformation
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_visjs(request, transformation='body_only')

        assert type(result)          is Schema__Graph__VisJs__Response
        assert result.transformation == 'body_only'

    def test__from_html_to_visjs__with_transformation__head_only(self):                       # Test vis.js with head_only transformation
        request = Schema__Graph__From_Html__Request(html='<html><head><title>Test</title></head><body></body></html>')
        result  = self.to_visjs(request, transformation='head_only')

        assert type(result)          is Schema__Graph__VisJs__Response
        assert result.transformation == 'head_only'

    # ═══════════════════════════════════════════════════════════════════════════════
    # from_html_to_transformation (d3) Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__from_html_to_d3__simple(self):                                                  # Test basic D3 conversion
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_d3(request)

        assert type(result)        is Schema__Graph__D3__Response
        assert type(result.nodes)  is Type_Safe__List
        assert type(result.links)  is Type_Safe__List                                                    # D3 uses 'links'
        #assert result.format       == 'd3'

    def test__from_html_to_d3__nodes_format(self):                                            # Test D3 nodes have correct format
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_d3(request)

        assert len(result.nodes) > 0
        node = result.nodes[0]
        assert 'id'    in node
        assert 'label' in node

    def test__from_html_to_d3__links_format(self):                                            # Test D3 links have correct format
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_d3(request)

        if len(result.links) > 0:
            link = result.links[0]
            assert 'source' in link
            assert 'target' in link

    def test__from_html_to_d3__with_transformation__body_only(self):                          # Test D3 with body_only transformation
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_d3(request, transformation='body_only')

        assert type(result)          is Schema__Graph__D3__Response
        assert result.transformation == 'body_only'

    def test__from_html_to_d3__with_transformation__structure_only(self):                     # Test D3 with structure_only (ideal for D3)
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_d3(request, transformation='structure_only')

        assert type(result)          is Schema__Graph__D3__Response
        assert result.transformation == 'structure_only'

    def test__from_html_to_d3__with_transformation__clean(self):                              # Test D3 with clean transformation
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_d3(request, transformation='clean')

        assert type(result)          is Schema__Graph__D3__Response
        assert result.transformation == 'clean'

    # ═══════════════════════════════════════════════════════════════════════════════
    # from_html_to_transformation (cytoscape) Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__from_html_to_cytoscape__simple(self):                                           # Test basic Cytoscape conversion
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_cytoscape(request)

        assert type(result)           is Schema__Graph__Cytoscape__Response
        assert type(result.elements)  is Type_Safe__Dict
        assert 'nodes'                in result.elements
        assert 'edges'                in result.elements
        #assert result.format          == 'cytoscape'

    def test__from_html_to_cytoscape__nodes_format(self):                                     # Test Cytoscape nodes have correct format
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_cytoscape(request)

        assert len(result.elements['nodes']) > 0
        node = result.elements['nodes'][0]
        assert 'data' in node
        assert 'id'   in node['data']

    def test__from_html_to_cytoscape__edges_format(self):                                     # Test Cytoscape edges have correct format
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_cytoscape(request)

        if len(result.elements['edges']) > 0:
            edge = result.elements['edges'][0]
            assert 'data'   in edge
            assert 'source' in edge['data']
            assert 'target' in edge['data']

    def test__from_html_to_cytoscape__with_transformation__clean(self):                       # Test Cytoscape with clean transformation
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_cytoscape(request, transformation='clean')

        assert type(result)          is Schema__Graph__Cytoscape__Response
        assert result.transformation == 'clean'

    def test__from_html_to_cytoscape__with_transformation__semantic(self):                    # Test Cytoscape with semantic transformation
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_cytoscape(request, transformation='semantic')

        assert type(result)          is Schema__Graph__Cytoscape__Response
        assert result.transformation == 'semantic'

    def test__from_html_to_cytoscape__with_transformation__attributes_view(self):             # Test Cytoscape with attributes_view transformation
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.to_cytoscape(request, transformation='attributes_view')

        assert type(result)          is Schema__Graph__Cytoscape__Response
        assert result.transformation == 'attributes_view'

    # ═══════════════════════════════════════════════════════════════════════════════
    # from_html_to_transformation (mermaid) Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__from_html_to_mermaid__simple(self):                                             # Test basic Mermaid conversion
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_mermaid(request)

        assert type(result)              is Schema__Graph__Mermaid__Response
        assert type(result.mermaid)      is str
        assert type(result.mermaid_size) is int
        #assert result.format             == 'mermaid'

    def test__from_html_to_mermaid__is_valid_mermaid(self):                                   # Test Mermaid output is valid
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_mermaid(request)

        assert type(result.mermaid) is str
        assert 'flowchart' in result.mermaid                                                  # Starts with flowchart

    def test__from_html_to_mermaid__size_is_accurate(self):                                   # Test mermaid_size is accurate
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_mermaid(request)

        assert result.mermaid_size == len(result.mermaid)

    def test__from_html_to_mermaid__with_transformation__structure_only(self):                # Test Mermaid with structure_only transformation
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_mermaid(request, transformation='structure_only')

        assert type(result)          is Schema__Graph__Mermaid__Response
        assert result.transformation == 'structure_only'

    def test__from_html_to_mermaid__with_transformation__clean(self):                         # Test Mermaid with clean transformation
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_mermaid(request, transformation='clean')

        assert type(result)          is Schema__Graph__Mermaid__Response
        assert result.transformation == 'clean'

    def test__from_html_to_mermaid__with_transformation__body_only(self):                     # Test Mermaid with body_only transformation
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_mermaid(request, transformation='body_only')

        assert type(result)          is Schema__Graph__Mermaid__Response
        assert result.transformation == 'body_only'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Transformations List Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__transformations__returns_list(self):                                            # Test transformations endpoint
        result = self.routes_graph.transformations()

        assert type(result) is list
        assert len(result)  >= 1                                                              # At least 'default'

    def test__transformations__has_required_fields(self):                                     # Test transformation metadata
        result = self.routes_graph.transformations()

        for transformation in result:
            assert 'name'        in transformation
            assert 'description' in transformation

    def test__transformations__includes_default(self):                                        # Test default transformation exists
        result = self.routes_graph.transformations()
        names  = [t['name'] for t in result]

        assert 'default' in names

    def test__transformations__includes_builtin_transforms(self):                             # Test built-in transformations exist
        result = self.routes_graph.transformations()
        names  = [t['name'] for t in result]

        assert 'body_only'       in names
        assert 'attributes_view' in names or 'attributes' in names

    # ═══════════════════════════════════════════════════════════════════════════════
    # Duration Tests (common to all formats)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__native_exports__have_duration(self):                                            # Test all native exports include duration
        request = Schema__Graph__From_Html__Request(html=self.simple_html)

        visjs_result     = self.to_visjs(request)
        d3_result        = self.to_d3(request)
        cytoscape_result = self.to_cytoscape(request)
        mermaid_result   = self.to_mermaid(request)

        assert type(visjs_result    ) is Schema__Graph__VisJs__Response
        assert type(d3_result       ) is Schema__Graph__D3__Response
        assert type(cytoscape_result) is Schema__Graph__Cytoscape__Response
        assert type(mermaid_result  ) is Schema__Graph__Mermaid__Response

        assert type(visjs_result    .duration) is float
        assert type(d3_result       .duration) is float
        assert type(cytoscape_result.duration) is float
        assert type(mermaid_result  .duration) is float

    def test__native_exports__have_transformation(self):                                      # Test all native exports include transformation
        request = Schema__Graph__From_Html__Request(html=self.simple_html)

        visjs_result     = self.to_visjs(request)
        d3_result        = self.to_d3(request)
        cytoscape_result = self.to_cytoscape(request)
        mermaid_result   = self.to_mermaid(request)

        assert type(visjs_result    .transformation) is str
        assert type(d3_result       .transformation) is str
        assert type(cytoscape_result.transformation) is str
        assert type(mermaid_result  .transformation) is str

    # ═══════════════════════════════════════════════════════════════════════════════
    # Complex HTML Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__from_html_to_visjs__complex_html(self):                                         # Test vis.js with complex HTML
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.to_visjs(request)

        assert type(result)       is Schema__Graph__VisJs__Response
        assert len(result.nodes)  >= 1

    def test__from_html_to_d3__complex_html(self):                                            # Test D3 with complex HTML
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.to_d3(request)

        assert type(result)       is Schema__Graph__D3__Response
        assert len(result.nodes)  >= 1

    def test__from_html_to_cytoscape__complex_html(self):                                     # Test Cytoscape with complex HTML
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.to_cytoscape(request)

        assert type(result)                       is Schema__Graph__Cytoscape__Response
        assert len(result.elements['nodes'])      >= 1

    def test__from_html_to_mermaid__complex_html(self):                                       # Test Mermaid with complex HTML
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.to_mermaid(request)

        assert type(result)        is Schema__Graph__Mermaid__Response
        assert result.mermaid_size > 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # All Transformations with All Engines Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__all_transformations__visjs(self):                                               # Test all transformations work with vis.js
        request         = Schema__Graph__From_Html__Request(html=self.simple_html)
        transformations = ['default', 'body_only', 'attributes_view', 'clean', 'semantic']

        for transformation in transformations:
            result = self.to_visjs(request, transformation=transformation)
            assert type(result)          is Schema__Graph__VisJs__Response
            assert result.transformation == transformation
            assert type(result.nodes)    is Type_Safe__List

    def test__all_transformations__d3(self):                                                  # Test all transformations work with D3
        request         = Schema__Graph__From_Html__Request(html=self.simple_html)
        transformations = ['default', 'body_only', 'attributes_view', 'clean', 'semantic']

        for transformation in transformations:
            result = self.to_d3(request, transformation=transformation)
            assert type(result)          is Schema__Graph__D3__Response
            assert result.transformation == transformation
            assert type(result.nodes)    is Type_Safe__List

    def test__all_transformations__cytoscape(self):                                           # Test all transformations work with Cytoscape
        request         = Schema__Graph__From_Html__Request(html=self.simple_html)
        transformations = ['default', 'body_only', 'attributes_view', 'clean', 'semantic']

        for transformation in transformations:
            result = self.to_cytoscape(request, transformation=transformation)
            assert type(result)           is Schema__Graph__Cytoscape__Response
            assert result.transformation  == transformation
            assert type(result.elements)  is Type_Safe__Dict

    def test__all_transformations__mermaid(self):                                             # Test all transformations work with Mermaid
        request         = Schema__Graph__From_Html__Request(html=self.simple_html)
        transformations = ['default', 'body_only', 'attributes_view', 'clean', 'semantic']

        for transformation in transformations:
            result = self.to_mermaid(request, transformation=transformation)
            assert type(result)          is Schema__Graph__Mermaid__Response
            assert result.transformation == transformation
            assert type(result.mermaid)  is str

    # ═══════════════════════════════════════════════════════════════════════════════
    # setup_routes Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__setup_routes(self):                                                             # Test setup_routes returns self
        routes = Routes__Graph()
        result = routes.setup_routes()

        assert result is routes