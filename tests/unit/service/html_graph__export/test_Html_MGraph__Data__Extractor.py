from unittest                                                                                  import TestCase
from osbot_utils.type_safe.Type_Safe                                                           import Type_Safe
from osbot_utils.utils.Objects                                                                 import base_classes
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                              import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Data__Extractor      import Html_MGraph__Data__Extractor, Extracted__Node, Extracted__Edge
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config              import Html_MGraph__Render__Config
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors              import Html_MGraph__Render__Colors
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Labels              import Html_MGraph__Render__Labels


class test_Html_MGraph__Data__Extractor(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simple_html   = '<div class="main">Hello World</div>'
        cls.complex_html  = '<div class="main" id="content"><h1>Title</h1><p>Paragraph</p></div>'
        cls.html_mgraph_simple  = Html_MGraph.from_html(cls.simple_html)
        cls.html_mgraph_complex = Html_MGraph.from_html(cls.complex_html)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Extracted__Node Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__Extracted__Node__init__(self):                                                  # Test Extracted__Node initialization
        with Extracted__Node(id='test-id') as _:
            assert type(_)            is Extracted__Node
            assert base_classes(_)    == [Type_Safe, object]
            assert _.id               == 'test-id'
            assert _.label            == ''
            assert _.node_type        == 'element'
            assert _.dom_path         == ''
            assert _.value            is None
            assert _.depth            == 0
            assert _.category         == ''
            assert _.graph_source     == ''
            assert _.fill_color       == '#E8E8E8'
            assert _.font_color       == '#333333'
            assert _.border_color     == '#CCCCCC'
            assert _.shape            == 'box'

    def test__Extracted__Node__with_values(self):                                             # Test Extracted__Node with custom values
        with Extracted__Node(id           = 'node-1'         ,
                             label        = '<div>'          ,
                             node_type    = 'element'        ,
                             dom_path     = 'html.body.div'  ,
                             depth        = 3                ,
                             category     = 'structural'     ,
                             graph_source = 'body'           ,
                             fill_color   = '#F5F5F5'        ) as _:
            assert _.id           == 'node-1'
            assert _.label        == '<div>'
            assert _.node_type    == 'element'
            assert _.dom_path     == 'html.body.div'
            assert _.depth        == 3
            assert _.category     == 'structural'
            assert _.graph_source == 'body'
            assert _.fill_color   == '#F5F5F5'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Extracted__Edge Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__Extracted__Edge__init__(self):                                                  # Test Extracted__Edge initialization
        with Extracted__Edge(id='edge-1', source='n1', target='n2') as _:
            assert type(_)         is Extracted__Edge
            assert base_classes(_) == [Type_Safe, object]
            assert _.id            == 'edge-1'
            assert _.source        == 'n1'
            assert _.target        == 'n2'
            assert _.predicate     == ''
            assert _.position      is None
            assert _.graph_source  == ''
            assert _.color         == '#888888'
            assert _.dashed        == False

    def test__Extracted__Edge__with_values(self):                                             # Test Extracted__Edge with custom values
        with Extracted__Edge(id           = 'edge-1'    ,
                             source       = 'n1'        ,
                             target       = 'n2'        ,
                             predicate    = 'child'     ,
                             position     = 0           ,
                             graph_source = 'body'      ,
                             color        = '#333333'   ,
                             dashed       = False       ) as _:
            assert _.predicate    == 'child'
            assert _.position     == 0
            assert _.graph_source == 'body'
            assert _.color        == '#333333'
            assert _.dashed       == False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Html_MGraph__Data__Extractor Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                   # Test auto-initialization
        with Html_MGraph__Data__Extractor(html_mgraph=self.html_mgraph_simple) as _:
            assert type(_)         is Html_MGraph__Data__Extractor
            assert base_classes(_) == [Type_Safe, object]
            assert _.html_mgraph   is self.html_mgraph_simple
            assert type(_.config)  is Html_MGraph__Render__Config
            assert type(_.colors)  is Html_MGraph__Render__Colors
            assert type(_.labels)  is Html_MGraph__Render__Labels
            assert _.nodes         == []
            assert _.edges         == []
            assert _.root_id       is None

    def test__init__with_config(self):                                                        # Test initialization with custom config
        config = Html_MGraph__Render__Config()
        config.show_tag_nodes = False

        with Html_MGraph__Data__Extractor(html_mgraph = self.html_mgraph_simple,
                                          config      = config                 ) as _:
            assert _.config                is config
            assert _.config.show_tag_nodes == False

    # ═══════════════════════════════════════════════════════════════════════════════
    # extract Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__extract__returns_self(self):                                                    # Test extract returns self for chaining
        with Html_MGraph__Data__Extractor(html_mgraph=self.html_mgraph_simple) as _:
            result = _.extract()
            assert result is _

    def test__extract__populates_nodes(self):                                                 # Test extract populates nodes list
        with Html_MGraph__Data__Extractor(html_mgraph=self.html_mgraph_simple) as _:
            _.extract()
            assert len(_.nodes) > 0
            assert all(type(n) is Extracted__Node for n in _.nodes)

    def test__extract__populates_edges(self):                                                 # Test extract populates edges list
        with Html_MGraph__Data__Extractor(html_mgraph=self.html_mgraph_complex) as _:
            _.extract()
            assert len(_.edges) > 0
            assert all(type(e) is Extracted__Edge for e in _.edges)

    def test__extract__sets_root_id(self):                                                    # Test extract finds root node
        with Html_MGraph__Data__Extractor(html_mgraph=self.html_mgraph_simple) as _:
            _.extract()
            assert _.root_id is not None

    def test__extract__simple_html(self):                                                     # Test extraction from simple HTML
        with Html_MGraph__Data__Extractor(html_mgraph=self.html_mgraph_simple) as _:
            _.extract()

            node_types = {n.node_type for n in _.nodes}
            assert 'element' in node_types or 'tag' in node_types or 'text' in node_types

    def test__extract__complex_html(self):                                                    # Test extraction from complex HTML
        with Html_MGraph__Data__Extractor(html_mgraph=self.html_mgraph_complex) as _:
            _.extract()

            assert len(_.nodes) >= 3                                                          # At least div, h1, p elements

    def test__extract__nodes_have_graph_source(self):                                         # Test nodes have graph_source set
        with Html_MGraph__Data__Extractor(html_mgraph=self.html_mgraph_simple) as _:
            _.extract()

            for node in _.nodes:
                assert node.graph_source in ('body', 'head', 'attrs', 'scripts', 'styles', '')

    def test__extract__edge_predicates(self):                                                 # Test edges have predicate
        with Html_MGraph__Data__Extractor(html_mgraph=self.html_mgraph_complex) as _:
            _.extract()

            if _.edges:
                predicates = {e.predicate for e in _.edges}
                assert len(predicates) >= 1

    def test__extract__child_edges_not_dashed(self):                                          # Test child edges are solid
        with Html_MGraph__Data__Extractor(html_mgraph=self.html_mgraph_complex) as _:
            _.extract()

            child_edges = [e for e in _.edges if e.predicate == 'child']
            for edge in child_edges:
                assert edge.dashed == False

    def test__extract__tag_edges_are_dashed(self):                                            # Test tag edges are dashed
        with Html_MGraph__Data__Extractor(html_mgraph=self.html_mgraph_simple) as _:
            _.extract()

            tag_edges = [e for e in _.edges if e.predicate == 'tag']
            for edge in tag_edges:
                assert edge.dashed == True

    # ═══════════════════════════════════════════════════════════════════════════════
    # Config Filtering Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__extract__hide_tag_nodes(self):                                                  # Test hiding tag nodes via config
        config = Html_MGraph__Render__Config()
        config.show_tag_nodes = False

        with Html_MGraph__Data__Extractor(html_mgraph = self.html_mgraph_simple,
                                          config      = config                 ) as _:
            _.extract()

            tag_nodes = [n for n in _.nodes if n.node_type == 'tag']
            assert len(tag_nodes) == 0                                                        # Tag nodes should be filtered

    def test__extract__hide_attr_nodes(self):                                                 # Test hiding attr nodes via config
        config = Html_MGraph__Render__Config()
        config.show_attr_nodes = False

        with Html_MGraph__Data__Extractor(html_mgraph = self.html_mgraph_complex,
                                          config      = config                  ) as _:
            _.extract()

            attr_nodes = [n for n in _.nodes if n.node_type == 'attr']
            assert len(attr_nodes) == 0                                                       # Attr nodes should be filtered

    def test__extract__hide_text_nodes(self):                                                 # Test hiding text nodes via config
        config = Html_MGraph__Render__Config()
        config.show_text_nodes = False

        with Html_MGraph__Data__Extractor(html_mgraph = self.html_mgraph_simple,
                                          config      = config                 ) as _:
            _.extract()

            text_nodes = [n for n in _.nodes if n.node_type == 'text']
            assert len(text_nodes) == 0                                                       # Text nodes should be filtered

    # ═══════════════════════════════════════════════════════════════════════════════
    # Utility Method Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___calculate_depth__empty_path(self):                                             # Test depth calculation for empty path
        with Html_MGraph__Data__Extractor(html_mgraph=self.html_mgraph_simple) as _:
            depth = _._calculate_depth('')
            assert depth == 0

    def test___calculate_depth__root(self):                                                   # Test depth calculation for root path
        with Html_MGraph__Data__Extractor(html_mgraph=self.html_mgraph_simple) as _:
            depth = _._calculate_depth('div')
            assert depth == 1

    def test___calculate_depth__nested(self):                                                 # Test depth calculation for nested path
        with Html_MGraph__Data__Extractor(html_mgraph=self.html_mgraph_simple) as _:
            depth = _._calculate_depth('html.body.div.p')
            assert depth == 4

    def test___extract_tag__simple(self):                                                     # Test tag extraction from simple path
        with Html_MGraph__Data__Extractor(html_mgraph=self.html_mgraph_simple) as _:
            tag = _._extract_tag('div')
            assert tag == 'div'

    def test___extract_tag__nested(self):                                                     # Test tag extraction from nested path
        with Html_MGraph__Data__Extractor(html_mgraph=self.html_mgraph_simple) as _:
            tag = _._extract_tag('html.body.div')
            assert tag == 'div'

    def test___extract_tag__with_index(self):                                                 # Test tag extraction with index
        with Html_MGraph__Data__Extractor(html_mgraph=self.html_mgraph_simple) as _:
            tag = _._extract_tag('html.body.div[0]')
            assert tag == 'div'

    def test___darken__valid_hex(self):                                                       # Test color darkening
        with Html_MGraph__Data__Extractor(html_mgraph=self.html_mgraph_simple) as _:
            darker = _._darken('#FFFFFF')
            assert darker.startswith('#')
            assert darker != '#FFFFFF'

    def test___darken__invalid_hex(self):                                                     # Test color darkening with invalid input
        with Html_MGraph__Data__Extractor(html_mgraph=self.html_mgraph_simple) as _:
            result = _._darken('invalid')
            assert result == '#CCCCCC'                                                        # Should return default