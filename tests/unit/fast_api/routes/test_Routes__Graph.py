# Test: Routes__Graph
#
# Unit tests for the graph routes handler.
# Updated to work with the new Html_Graph__Export__Service v1.4.0

from unittest                                                                            import TestCase
from mgraph_ai_service_html_graph.fast_api.routes.Routes__Graph                          import Routes__Graph, TAG__ROUTES_GRAPH, ROUTES_PATHS__GRAPH
#from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Dot__Response             import Schema__Graph__Dot__Response
from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Html__Request       import Schema__Graph__From_Html__Request
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Schemas import Schema__Graph__Tree__Response, Schema__Graph__Dot__Response
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service import Html_Graph__Export__Service
from mgraph_db.utils.testing.mgraph_test_ids import mgraph_test_ids
from osbot_utils.testing.__ import __, __SKIP__


class test_Routes__Graph(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.routes_graph = Routes__Graph()
        cls.simple_html  = '<html><body><div><p>Hello World</p></div></body></html>'
        cls.complex_html = '<html><body><div class="main" id="content"><h1>Title</h1><p>Paragraph</p></div></body></html>'

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

        assert type(result)     is Schema__Graph__Dot__Response
        assert type(result.dot) is str
        assert 'digraph'        in result.dot

    def test__from_html_to_dot__with_attributes(self):
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.to_dot(request)

        assert type(result.dot) is str

    def test__from_html_to_dot__has_duration(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_dot(request)

        assert hasattr(result, 'duration')
        assert result.duration >= 0

    def test__from_html_to_dot__has_counts(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_dot(request)

        assert hasattr(result, 'node_count')
        assert hasattr(result, 'edge_count')
        assert result.node_count >= 0
        assert result.edge_count >= 0

    # ═══════════════════════════════════════════════════════════════════════════════════
    # from_html_to_transformation Tests (Tree engine)
    # ═══════════════════════════════════════════════════════════════════════════════════

    def test__from_html_to_tree__simple(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_tree(request)

        assert type(result)         is Schema__Graph__Tree__Response


    def test__from_html_to_tree__complex(self):
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.to_tree(request)

        assert type(result) is Schema__Graph__Tree__Response

    def test__from_html_to_tree__has_children(self):
        with mgraph_test_ids():
            request = Schema__Graph__From_Html__Request(html=self.simple_html)
            result  = self.to_tree(request)
            assert type(result) is Schema__Graph__Tree__Response
            assert result.obj() == __( tree='├── c0000003\n'
                                            '└── body\n'
                                            '    └── body.div\n'
                                            '        └── body.div.p\n'
                                            '            └── Hello World',
                                       output_format='text',
                                       duration=__SKIP__,
                                       transformation='default',
                                       engine='tree',
                                       node_count=5,
                                       edge_count=3)

    # ═══════════════════════════════════════════════════════════════════════════════════
    # from_html_to_transformation Tests (Tree Text engine)
    # ═══════════════════════════════════════════════════════════════════════════════════

    # def test__from_html_to_tree_text__simple(self):
    #     request = Schema__Graph__From_Html__Request(html=self.simple_html)
    #     result  = self.to_tree_text(request)
    #
    #     assert type(result)              is dict
    #     assert 'tree_text'               in result
    #     assert 'duration'                in result
    #     assert result['format']          == 'tree_text'
    #     assert type(result['tree_text']) is str
    #     assert len(result['tree_text'])  > 0
    #
    # def test__from_html_to_tree_text__complex(self):
    #     request = Schema__Graph__From_Html__Request(html=self.complex_html)
    #     result  = self.to_tree_text(request)
    #
    #     assert type(result)              is dict
    #     assert type(result['tree_text']) is str
    #
    # def test__from_html_to_tree_text__contains_structure(self):
    #     request   = Schema__Graph__From_Html__Request(html=self.simple_html)
    #     result    = self.to_tree_text(request)
    #     tree_text = result['tree_text']
    #
    #     assert '\n' in tree_text                                                 # Has multiple lines
    #
    # def test__from_html_to_tree_text__size_matches(self):
    #     request = Schema__Graph__From_Html__Request(html=self.simple_html)
    #     result  = self.to_tree_text(request)
    #
    #     if 'tree_text_size' in result:
    #         assert result['tree_text_size'] == len(result['tree_text'])

    # ═══════════════════════════════════════════════════════════════════════════════════
    # DOT Transformation Tests
    # ═══════════════════════════════════════════════════════════════════════════════════

    def test__transformation__default(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_dot(request, transformation='default')

        assert type(result.dot) is str
        assert 'digraph' in result.dot
        assert result.transformation == 'default'

    def test__transformation__structure_only(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_dot(request, transformation='structure_only')

        assert type(result.dot) is str
        assert result.transformation == 'structure_only'

    def test__transformation__body_only(self):
        request = Schema__Graph__From_Html__Request(html='<html><head></head><body><p>Test</p></body></html>')
        result  = self.to_dot(request, transformation='body_only')

        assert type(result.dot) is str
        assert result.transformation == 'body_only'

    def test__transformation__clean(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_dot(request, transformation='clean')

        assert type(result.dot) is str
        assert result.transformation == 'clean'

    def test__transformation__semantic(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_dot(request, transformation='semantic')

        assert type(result.dot) is str
        assert result.transformation == 'semantic'

    def test__transformation__attributes_view(self):
        request = Schema__Graph__From_Html__Request(html=self.complex_html)
        result  = self.to_dot(request, transformation='attributes_view')

        assert type(result.dot) is str
        assert result.transformation == 'attributes_view'

    def test__transformation__head_only(self):
        request = Schema__Graph__From_Html__Request(html='<html><head><title>Test</title></head><body></body></html>')
        result  = self.to_dot(request, transformation='head_only')

        assert type(result.dot) is str
        assert result.transformation == 'head_only'

    def test__transformation__full_document(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_dot(request, transformation='full_document')

        assert type(result.dot) is str
        assert result.transformation == 'full_document'

    # ═══════════════════════════════════════════════════════════════════════════════════
    # Tree Transformation Tests
    # ═══════════════════════════════════════════════════════════════════════════════════

    def test__tree__transformation__default(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_tree(request, transformation='default')

        assert result.transformation == 'default'

    def test__tree__transformation__structure_only(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_tree(request, transformation='structure_only')

        assert result.transformation == 'structure_only'

    def test__tree__transformation__body_only(self):
        request = Schema__Graph__From_Html__Request(html='<html><head></head><body><p>Test</p></body></html>')
        result  = self.to_tree(request, transformation='body_only')

        assert result.transformation == 'body_only'

    def test__tree__transformation__clean(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_tree(request, transformation='clean')
        assert result.transformation == 'clean'
        

    def test__tree__transformation__semantic(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)
        result  = self.to_tree(request, transformation='semantic')

        assert result.transformation == 'semantic'        

    def test__tree__transformation__attributes_view(self):
        with mgraph_test_ids():
            request = Schema__Graph__From_Html__Request(html=self.complex_html)
            result  = self.to_tree(request, transformation='attributes_view')

        assert result.transformation == 'attributes_view'
        assert result.obj() == __(tree='├── c0000003\n'
                                        '└── body\n'
                                        '    └── body.div\n'
                                        '        ├── body.div.h1\n'
                                        '        │   └── Title\n'
                                        '        └── body.div.p\n'
                                        '            └── Paragraph',
                                   output_format='text',
                                   duration=__SKIP__,
                                   transformation='attributes_view',
                                   engine='tree',
                                   node_count=7,
                                   edge_count=5)


    # ═══════════════════════════════════════════════════════════════════════════════════
    # Tree Text Transformation Tests
    # ═══════════════════════════════════════════════════════════════════════════════════
    # todo: add tree_text support
    # def test__tree_text__transformation__default(self):
    #     request = Schema__Graph__From_Html__Request(html=self.simple_html)
    #     result  = self.to_tree_text(request, transformation='default')
    #
    #     assert result.transformation  == 'default'
    #     assert type(result['tree_text']) is str
    #
    # def test__tree_text__transformation__structure_only(self):
    #     request = Schema__Graph__From_Html__Request(html=self.simple_html)
    #     result  = self.to_tree_text(request, transformation='structure_only')
    #
    #     assert result.transformation  == 'structure_only'
    #     assert type(result['tree_text']) is str
    #
    # def test__tree_text__transformation__body_only(self):
    #     request = Schema__Graph__From_Html__Request(html='<html><head></head><body><p>Test</p></body></html>')
    #     result  = self.to_tree_text(request, transformation='body_only')
    #
    #     assert result.transformation  == 'body_only'
    #     assert type(result['tree_text']) is str
    #
    # def test__tree_text__transformation__clean(self):
    #     request = Schema__Graph__From_Html__Request(html=self.simple_html)
    #     result  = self.to_tree_text(request, transformation='clean')
    #
    #     assert result.transformation  == 'clean'
    #     assert type(result['tree_text']) is str
    #
    # def test__tree_text__transformation__semantic(self):
    #     request = Schema__Graph__From_Html__Request(html=self.simple_html)
    #     result  = self.to_tree_text(request, transformation='semantic')
    #
    #     assert result.transformation  == 'semantic'
    #     assert type(result.tree_text) is str

    # ═══════════════════════════════════════════════════════════════════════════════════
    # Engine Type Tests
    # ═══════════════════════════════════════════════════════════════════════════════════

    def test__unknown_engine__raises_exception(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)

        with self.assertRaises(Exception) as context:
            self.routes_graph.from_html_to_transformation(engine='unknown_engine',
                                                          transformation='default',
                                                          request=request)

        assert 'Unknown' in str(context.exception) or 'unknown' in str(context.exception).lower()

    def test__all_engines__return_valid_format(self):
        request = Schema__Graph__From_Html__Request(html=self.simple_html)

        engines_and_formats = [
            ('dot'      , 'dot'      ),
            ('visjs'    , 'visjs'    ),
            ('d3'       , 'd3'       ),
            ('cytoscape', 'cytoscape'),
            ('mermaid'  , 'mermaid'  ),
            ('tree'     , 'tree'     ),
            #('tree_text', 'tree_text'),
        ]

        for engine, expected_format in engines_and_formats:
            result = self.routes_graph.from_html_to_transformation(engine=engine,
                                                                   transformation='default',
                                                                   request=request)
            if engine == 'dot':                                                  # DOT returns Schema object
                assert hasattr(result, 'dot')
            else:                                                                # Others return dict
                if hasattr(result, 'format'):
                    assert result.format == expected_format, f"Engine {engine} returned wrong format"

    # ═══════════════════════════════════════════════════════════════════════════════════
    # setup_routes Tests
    # ═══════════════════════════════════════════════════════════════════════════════════

    def test__setup_routes(self):
        routes = Routes__Graph()
        result = routes.setup_routes()

        assert result is routes