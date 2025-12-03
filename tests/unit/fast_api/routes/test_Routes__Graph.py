from unittest                                                                        import TestCase
from mgraph_ai_service_html_graph.fast_api.routes.Routes__Graph                      import Routes__Graph, TAG__ROUTES_GRAPH, ROUTES_PATHS__GRAPH
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Dot__Response         import Schema__Graph__Dot__Response
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Stats                 import Schema__Graph__Stats
from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Html__Request   import Schema__Graph__From_Html__Request
from mgraph_ai_service_html_graph.service.html_graph__export                         import Html_Graph__Export__Service
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config    import Enum__Html_Render__Preset
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors    import Enum__Html_Render__Color_Scheme


class test_Routes__Graph(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.routes_graph = Routes__Graph()
        cls.simple_html  = '<div><p>Hello World</p></div>'
        cls.complex_html = '<div class="main" id="content"><h1>Title</h1><p>Paragraph</p></div>'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                       # Test auto-initialization
        with Routes__Graph() as _:
            assert type(_)                is Routes__Graph
            assert _.tag                  == TAG__ROUTES_GRAPH
            assert type(_.graph_service)  is Html_Graph__Export__Service

    def test__routes_paths(self):                                                                 # Test route paths constant
        assert '/graph/from/html/to/dot' in ROUTES_PATHS__GRAPH
        assert len(ROUTES_PATHS__GRAPH)  == 5                                                     # All planned routes

    # ═══════════════════════════════════════════════════════════════════════════════
    # from__html__to__dot Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__from_html_to_dot__simple(self):                                                     # Test basic DOT conversion
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.routes_graph.from__html__to__dot(request)

        assert type(result)       is Schema__Graph__Dot__Response
        assert type(result.dot)   is str
        assert type(result.stats) is Schema__Graph__Stats
        assert 'digraph' in result.dot                                                            # DOT format marker
        assert result.stats.element_nodes >= 2                                                    # At least div and p

    def test__from_html_to_dot__with_attributes(self):                                            # Test HTML with attributes
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.routes_graph.from__html__to__dot(request)

        assert result.stats.attr_nodes >= 2                                                       # class and id attributes

    def test__from_html_to_dot__preset_full_detail(self):                                         # Test full detail preset
        request = Schema__Graph__From_Html__Request(html            = self.simple_html                    ,
                                                    preset          = Enum__Html_Render__Preset.FULL_DETAIL)
        result  = self.routes_graph.from__html__to__dot(request)

        assert result.stats.tag_nodes >= 1                                                        # Tag nodes should be visible

    def test__from_html_to_dot__preset_structure_only(self):                                      # Test structure only preset
        request = Schema__Graph__From_Html__Request(html   = self.simple_html                        ,
                                                    preset = Enum__Html_Render__Preset.STRUCTURE_ONLY)
        result  = self.routes_graph.from__html__to__dot(request)

        assert type(result.dot)   is str
        assert 'digraph' in result.dot

    def test__from_html_to_dot__hide_tag_nodes(self):                                             # Test hiding tag nodes
        request = Schema__Graph__From_Html__Request(html           = self.simple_html ,
                                                    show_tag_nodes = False            )
        result  = self.routes_graph.from__html__to__dot(request)

        assert type(result.dot) is str                                                            # Should still generate valid DOT

    def test__from_html_to_dot__hide_attr_nodes(self):                                            # Test hiding attribute nodes
        request = Schema__Graph__From_Html__Request(html            = self.complex_html ,
                                                    show_attr_nodes = False             )
        result  = self.routes_graph.from__html__to__dot(request)

        assert type(result.dot) is str

    def test__from_html_to_dot__hide_text_nodes(self):                                            # Test hiding text nodes
        request = Schema__Graph__From_Html__Request(html            = self.simple_html ,
                                                    show_text_nodes = False            )
        result  = self.routes_graph.from__html__to__dot(request)

        assert type(result.dot) is str

    def test__from_html_to_dot__color_scheme_default(self):                                       # Test default color scheme
        request = Schema__Graph__From_Html__Request(html         = self.simple_html                       ,
                                                    color_scheme = Enum__Html_Render__Color_Scheme.DEFAULT)
        result  = self.routes_graph.from__html__to__dot(request)

        assert type(result.dot) is str

    def test__from_html_to_dot__color_scheme_monochrome(self):                                    # Test monochrome color scheme
        request = Schema__Graph__From_Html__Request(html         = self.simple_html                          ,
                                                    color_scheme = Enum__Html_Render__Color_Scheme.MONOCHROME)
        result  = self.routes_graph.from__html__to__dot(request)

        assert type(result.dot) is str

    def test__from_html_to_dot__color_scheme_high_contrast(self):                                 # Test high contrast color scheme
        request = Schema__Graph__From_Html__Request(html         = self.simple_html                             ,
                                                    color_scheme = Enum__Html_Render__Color_Scheme.HIGH_CONTRAST)
        result  = self.routes_graph.from__html__to__dot(request)

        assert type(result.dot) is str

    # ═══════════════════════════════════════════════════════════════════════════════
    # Stats Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__stats__simple_html(self):                                                           # Test statistics for simple HTML
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.routes_graph.from__html__to__dot(request)
        stats   = result.stats

        assert stats.total_nodes   > 0
        assert stats.total_edges   > 0
        assert stats.element_nodes > 0
        assert stats.value_nodes   >= 0
        assert stats.tag_nodes     >= 0
        assert stats.text_nodes    >= 0
        assert stats.attr_nodes    >= 0

    def test__stats__complex_html(self):                                                          # Test statistics for complex HTML
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.routes_graph.from__html__to__dot(request)
        stats   = result.stats

        assert stats.element_nodes >= 3                                                           # div, h1, p
        assert stats.attr_nodes    >= 2                                                           # class, id

    # ═══════════════════════════════════════════════════════════════════════════════
    # setup_routes Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__setup_routes(self):                                                                 # Test setup_routes returns self
        routes = Routes__Graph()
        result = routes.setup_routes()

        assert result is routes


