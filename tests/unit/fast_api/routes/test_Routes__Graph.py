from unittest                                                                            import TestCase
from mgraph_ai_service_html_graph.fast_api.routes.Routes__Graph                          import Routes__Graph, TAG__ROUTES_GRAPH, ROUTES_PATHS__GRAPH
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Dot__Response             import Schema__Graph__Dot__Response
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Stats                     import Schema__Graph__Stats
from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Html__Request       import Schema__Graph__From_Html__Request
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service import Html_Graph__Export__Service
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config        import Enum__Html_Render__Preset
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors        import Enum__Html_Render__Color_Scheme


class test_Routes__Graph(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.routes_graph = Routes__Graph()
        cls.simple_html  = '<div><p>Hello World</p></div>'
        cls.complex_html = '<div class="main" id="content"><h1>Title</h1><p>Paragraph</p></div>'

    # ═══════════════════════════════════════════════════════════════════════════════════
    # Helper methods
    # ═══════════════════════════════════════════════════════════════════════════════════

    def to_dot(self, request, transformation='default'):
        return self.routes_graph.from_html_to_transformation(engine='dot', transformation=transformation, request=request)

    def to_tree(self, request, transformation='default'):
        return self.routes_graph.from_html_to_transformation(engine='tree', transformation=transformation, request=request)

    def to_tree_text(self, request, transformation='default'):
        return self.routes_graph.from_html_to_transformation(engine='tree_text', transformation=transformation, request=request)

    # ═══════════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with Routes__Graph() as _:
            assert type(_)                is Routes__Graph
            assert _.tag                  == TAG__ROUTES_GRAPH
            assert type(_.graph_service)  is Html_Graph__Export__Service

    # ═══════════════════════════════════════════════════════════════════════════════════
    # from_html_to_transformation Tests (DOT engine)
    # ═══════════════════════════════════════════════════════════════════════════════════

    def test__from_html_to_dot__simple(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_dot(request)

        assert type(result)       is Schema__Graph__Dot__Response
        assert type(result.dot)   is str
        assert type(result.stats) is Schema__Graph__Stats
        assert 'digraph' in result.dot
        assert result.stats.element_nodes >= 2

    def test__from_html_to_dot__with_attributes(self):
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.to_dot(request)

        assert result.stats.attr_nodes >= 2

    def test__from_html_to_dot__preset_full_detail(self):
        request = Schema__Graph__From_Html__Request(html   = self.simple_html,
                                                    preset = Enum__Html_Render__Preset.FULL_DETAIL)
        result  = self.to_dot(request)

        assert result.stats.unique_tags >= 1

    def test__from_html_to_dot__preset_structure_only(self):
        request = Schema__Graph__From_Html__Request(html   = self.simple_html,
                                                    preset = Enum__Html_Render__Preset.STRUCTURE_ONLY)
        result  = self.to_dot(request)

        assert type(result.dot) is str
        assert 'digraph' in result.dot

    def test__from_html_to_dot__hide_tag_nodes(self):
        request = Schema__Graph__From_Html__Request(html           = self.simple_html,
                                                    show_tag_nodes = False)
        result  = self.to_dot(request)

        assert type(result.dot) is str

    def test__from_html_to_dot__hide_attr_nodes(self):
        request = Schema__Graph__From_Html__Request(html            = self.complex_html,
                                                    show_attr_nodes = False)
        result  = self.to_dot(request)

        assert type(result.dot) is str

    def test__from_html_to_dot__hide_text_nodes(self):
        request = Schema__Graph__From_Html__Request(html            = self.simple_html,
                                                    show_text_nodes = False)
        result  = self.to_dot(request)

        assert type(result.dot) is str

    def test__from_html_to_dot__color_scheme_default(self):
        request = Schema__Graph__From_Html__Request(html         = self.simple_html,
                                                    color_scheme = Enum__Html_Render__Color_Scheme.DEFAULT)
        result  = self.to_dot(request)

        assert type(result.dot) is str

    def test__from_html_to_dot__color_scheme_monochrome(self):
        request = Schema__Graph__From_Html__Request(html         = self.simple_html,
                                                    color_scheme = Enum__Html_Render__Color_Scheme.MONOCHROME)
        result  = self.to_dot(request)

        assert type(result.dot) is str

    def test__from_html_to_dot__color_scheme_high_contrast(self):
        request = Schema__Graph__From_Html__Request(html         = self.simple_html,
                                                    color_scheme = Enum__Html_Render__Color_Scheme.HIGH_CONTRAST)
        result  = self.to_dot(request)

        assert type(result.dot) is str

    # ═══════════════════════════════════════════════════════════════════════════════════
    # from_html_to_transformation Tests (Tree engine)
    # ═══════════════════════════════════════════════════════════════════════════════════

    def test__from_html_to_tree__simple(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_tree(request)

        assert type(result)         is dict
        assert 'tree'               in result
        assert 'rootId'             in result
        assert 'stats'              in result
        assert 'duration'           in result
        assert result['format']     == 'tree'
        assert type(result['tree']) is dict

    def test__from_html_to_tree__complex(self):
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.to_tree(request)

        assert type(result)         is dict
        assert type(result['tree']) is dict
        assert result['rootId']     is not None

    def test__from_html_to_tree__has_children(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_tree(request)
        tree    = result['tree']

        assert 'children' in tree
        assert 'id'       in tree

    def test__from_html_to_tree__preset_full_detail(self):
        request = Schema__Graph__From_Html__Request(html   = self.simple_html,
                                                    preset = Enum__Html_Render__Preset.FULL_DETAIL)
        result  = self.to_tree(request)

        assert type(result['tree']) is dict

    def test__from_html_to_tree__preset_structure_only(self):
        request = Schema__Graph__From_Html__Request(html   = self.simple_html,
                                                    preset = Enum__Html_Render__Preset.STRUCTURE_ONLY)
        result  = self.to_tree(request)

        assert type(result['tree']) is dict

    # ═══════════════════════════════════════════════════════════════════════════════════
    # from_html_to_transformation Tests (Tree Text engine)
    # ═══════════════════════════════════════════════════════════════════════════════════

    def test__from_html_to_tree_text__simple(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_tree_text(request)

        assert type(result)              is dict
        assert 'tree_text'               in result
        assert 'tree_text_size'          in result
        assert 'rootId'                  in result
        assert 'stats'                   in result
        assert 'duration'                in result
        assert result['format']          == 'tree_text'
        assert type(result['tree_text']) is str
        assert len(result['tree_text'])  > 0

    def test__from_html_to_tree_text__complex(self):
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.to_tree_text(request)

        assert type(result)              is dict
        assert type(result['tree_text']) is str
        assert result['rootId']          is not None

    def test__from_html_to_tree_text__contains_structure(self):
        request   = Schema__Graph__From_Html__Request(html=self.simple_html)
        result    = self.to_tree_text(request)
        tree_text = result['tree_text']

        assert '\n' in tree_text                                                    # Has multiple lines
        assert '    ' in tree_text or '\t' in tree_text                             # Has indentation

    def test__from_html_to_tree_text__size_matches(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_tree_text(request)

        assert result['tree_text_size'] == len(result['tree_text'])

    def test__from_html_to_tree_text__preset_full_detail(self):
        request = Schema__Graph__From_Html__Request(html   = self.simple_html,
                                                    preset = Enum__Html_Render__Preset.FULL_DETAIL)
        result  = self.to_tree_text(request)

        assert type(result['tree_text']) is str

    def test__from_html_to_tree_text__preset_structure_only(self):
        request = Schema__Graph__From_Html__Request(html   = self.simple_html,
                                                    preset = Enum__Html_Render__Preset.STRUCTURE_ONLY)
        result  = self.to_tree_text(request)

        assert type(result['tree_text']) is str

    # ═══════════════════════════════════════════════════════════════════════════════════
    # DOT Transformation Tests
    # ═══════════════════════════════════════════════════════════════════════════════════

    def test__transformation__default(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_dot(request, transformation='default')

        assert type(result.dot) is str
        assert 'digraph' in result.dot

    def test__transformation__elements_only(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_dot(request, transformation='elements_only')

        assert type(result.dot) is str

    def test__transformation__body_only(self):
        request = Schema__Graph__From_Html__Request(html='<html><head></head><body><p>Test</p></body></html>')
        result  = self.to_dot(request, transformation='body_only')

        assert type(result.dot) is str

    def test__transformation__collapse_text(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_dot(request, transformation='collapse_text')

        assert type(result.dot) is str

    # ═══════════════════════════════════════════════════════════════════════════════════
    # Tree Transformation Tests
    # ═══════════════════════════════════════════════════════════════════════════════════

    def test__tree__transformation__default(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_tree(request, transformation='default')

        assert result['transformation'] == 'default'
        assert type(result['tree'])     is dict

    def test__tree__transformation__elements_only(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_tree(request, transformation='elements_only')

        assert result['transformation'] == 'elements_only'
        assert type(result['tree'])     is dict

    def test__tree__transformation__body_only(self):
        request = Schema__Graph__From_Html__Request(html='<html><head></head><body><p>Test</p></body></html>')
        result  = self.to_tree(request, transformation='body_only')

        assert result['transformation'] == 'body_only'
        assert type(result['tree'])     is dict

    def test__tree__transformation__collapse_text(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_tree(request, transformation='collapse_text')

        assert result['transformation'] == 'collapse_text'
        assert type(result['tree'])     is dict

    # ═══════════════════════════════════════════════════════════════════════════════════
    # Tree Text Transformation Tests
    # ═══════════════════════════════════════════════════════════════════════════════════

    def test__tree_text__transformation__default(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_tree_text(request, transformation='default')

        assert result['transformation']  == 'default'
        assert type(result['tree_text']) is str

    def test__tree_text__transformation__elements_only(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_tree_text(request, transformation='elements_only')

        assert result['transformation']  == 'elements_only'
        assert type(result['tree_text']) is str

    def test__tree_text__transformation__body_only(self):
        request = Schema__Graph__From_Html__Request(html='<html><head></head><body><p>Test</p></body></html>')
        result  = self.to_tree_text(request, transformation='body_only')

        assert result['transformation']  == 'body_only'
        assert type(result['tree_text']) is str

    def test__tree_text__transformation__collapse_text(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_tree_text(request, transformation='collapse_text')

        assert result['transformation']  == 'collapse_text'
        assert type(result['tree_text']) is str

    # ═══════════════════════════════════════════════════════════════════════════════════
    # DOT Stats Tests
    # ═══════════════════════════════════════════════════════════════════════════════════

    def test__stats__simple_html(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_dot(request)
        stats   = result.stats

        assert stats.total_nodes   > 0
        assert stats.total_edges   > 0
        assert stats.element_nodes > 0
        assert stats.value_nodes   >= 0
        assert stats.unique_tags     >= 0
        assert stats.text_nodes    >= 0
        assert stats.attr_nodes    >= 0

    def test__stats__complex_html(self):
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.to_dot(request)
        stats   = result.stats

        assert stats.element_nodes >= 3
        assert stats.attr_nodes    >= 2

    # ═══════════════════════════════════════════════════════════════════════════════════
    # Tree Stats Tests
    # ═══════════════════════════════════════════════════════════════════════════════════

    def test__tree__stats__simple_html(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_tree(request)
        stats   = result['stats']

        assert stats['total_nodes']   > 0
        assert stats['total_edges']   > 0
        assert stats['element_nodes'] > 0

    def test__tree__stats__complex_html(self):
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.to_tree(request)
        stats   = result['stats']

        assert stats['element_nodes'] >= 3
        assert stats['attr_nodes']    >= 2

    def test__tree_text__stats__simple_html(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_tree_text(request)
        stats   = result['stats']

        assert stats['total_nodes']   > 0
        assert stats['total_edges']   > 0
        assert stats['element_nodes'] > 0

    def test__tree_text__stats__complex_html(self):
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.to_tree_text(request)
        stats   = result['stats']

        assert stats['element_nodes'] >= 3
        assert stats['attr_nodes']    >= 2

    # ═══════════════════════════════════════════════════════════════════════════════════
    # Engine Type Tests
    # ═══════════════════════════════════════════════════════════════════════════════════

    def test__unknown_engine__raises_exception(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)

        with self.assertRaises(Exception) as context:
            self.routes_graph.from_html_to_transformation(engine='unknown_engine',
                                                          transformation='default',
                                                          request=request)

        assert 'Unknown graph engine' in str(context.exception)

    def test__all_engines__return_valid_format(self):
        """Test that all supported engines return their expected format."""
        request = Schema__Graph__From_Html__Request(html=self.simple_html)

        engines_and_formats = [
            ('dot'      , 'dot'      ),
            ('visjs'    , 'visjs'    ),
            ('d3'       , 'd3'       ),
            ('cytoscape', 'cytoscape'),
            ('mermaid'  , 'mermaid'  ),
            ('tree'     , 'tree'     ),
            ('tree_text', 'tree_text'),
        ]

        for engine, expected_format in engines_and_formats:
            result = self.routes_graph.from_html_to_transformation(engine=engine,
                                                                   transformation='default',
                                                                   request=request)
            if hasattr(result, 'json'):                                             # Schema object
                result_dict = result.json()
            else:                                                                   # Already a dict
                result_dict = result

            # DOT returns Schema object, others return dict
            if engine == 'dot':
                assert hasattr(result, 'dot')
            else:
                assert result_dict.get('format') == expected_format, f"Engine {engine} returned wrong format"

    # ═══════════════════════════════════════════════════════════════════════════════════
    # setup_routes Tests
    # ═══════════════════════════════════════════════════════════════════════════════════

    def test__setup_routes(self):
        routes = Routes__Graph()
        result = routes.setup_routes()

        assert result is routes