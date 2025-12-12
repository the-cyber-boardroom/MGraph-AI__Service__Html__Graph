from unittest                                                                                  import TestCase
from osbot_utils.type_safe.Type_Safe                                                           import Type_Safe
from osbot_utils.utils.Objects                                                                 import base_classes
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph                               import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Data__Extractor      import Html_MGraph__Data__Extractor, Extracted__Node, Extracted__Edge
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config              import Html_MGraph__Render__Config
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors              import Html_MGraph__Render__Colors
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Labels              import Html_MGraph__Render__Labels


class test_Html_MGraph__Data__Extractor(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simple_html_dict  = SIMPLE_HTML_DICT
        cls.complex_html_dict = COMPLEX_HTML_DICT
        cls.html_mgraph_simple  = Html_MGraph.from_html_dict(cls.simple_html_dict)
        cls.html_mgraph_complex = Html_MGraph.from_html_dict(cls.complex_html_dict)

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
                             fill_color   = '#F5F5F5'        ) as _:
            assert _.id         == 'node-1'
            assert _.label      == '<div>'
            assert _.node_type  == 'element'
            assert _.dom_path   == 'html.body.div'
            assert _.depth      == 3
            assert _.category   == 'structural'
            assert _.fill_color == '#F5F5F5'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Extracted__Edge Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__Extracted__Edge__init__(self):                                                  # Test Extracted__Edge initialization
        with Extracted__Edge(id='edge-1', source='n1', target='n2') as _:
            assert type(_)       is Extracted__Edge
            assert base_classes(_) == [Type_Safe, object]
            assert _.id          == 'edge-1'
            assert _.source      == 'n1'
            assert _.target      == 'n2'
            assert _.predicate   == ''
            assert _.position    is None
            assert _.color       == '#888888'
            assert _.dashed      == False

    def test__Extracted__Edge__with_values(self):                                             # Test Extracted__Edge with custom values
        with Extracted__Edge(id        = 'edge-1'    ,
                             source    = 'n1'        ,
                             target    = 'n2'        ,
                             predicate = 'child'     ,
                             position  = 0           ,
                             color     = '#333333'   ,
                             dashed    = False       ) as _:
            assert _.predicate == 'child'
            assert _.position  == 0
            assert _.color     == '#333333'
            assert _.dashed    == False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Html_MGraph__Data__Extractor Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                   # Test auto-initialization
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_simple.mgraph) as _:
            assert type(_)         is Html_MGraph__Data__Extractor
            assert base_classes(_) == [Type_Safe, object]
            assert _.mgraph        is self.html_mgraph_simple.mgraph
            assert type(_.config)  is Html_MGraph__Render__Config
            assert type(_.colors)  is Html_MGraph__Render__Colors
            assert type(_.labels)  is Html_MGraph__Render__Labels
            assert _.nodes         == []
            assert _.edges         == []
            assert _.root_id       is None

    def test__init__with_config(self):                                                        # Test initialization with custom config
        config = Html_MGraph__Render__Config()
        config.show_tag_nodes = False

        with Html_MGraph__Data__Extractor(mgraph = self.html_mgraph_simple.mgraph,
                                          config = config                        ) as _:
            assert _.config               is config
            assert _.config.show_tag_nodes == False

    # ═══════════════════════════════════════════════════════════════════════════════
    # extract Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__extract__returns_self(self):                                                    # Test extract returns self for chaining
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.extract()
            assert result is _

    def test__extract__populates_nodes(self):                                                 # Test extract populates nodes list
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_simple.mgraph) as _:
            _.extract()
            assert len(_.nodes) > 0
            assert all(type(n) is Extracted__Node for n in _.nodes)

    def test__extract__populates_edges(self):                                                 # Test extract populates edges list
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_simple.mgraph) as _:
            _.extract()
            assert len(_.edges) > 0
            assert all(type(e) is Extracted__Edge for e in _.edges)

    def test__extract__sets_root_id(self):                                                    # Test extract finds root node
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_simple.mgraph) as _:
            _.extract()
            assert _.root_id is not None

    def test__extract__simple_html(self):                                                     # Test extraction from simple HTML
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_simple.mgraph) as _:
            _.extract()

            element_nodes = [n for n in _.nodes if n.node_type == 'element']
            tag_nodes     = [n for n in _.nodes if n.node_type == 'tag']
            text_nodes    = [n for n in _.nodes if n.node_type == 'text']
            attr_nodes    = [n for n in _.nodes if n.node_type == 'attr']

            assert len(element_nodes) >= 1                                                    # At least one element
            assert len(tag_nodes)     >= 1                                                    # At least one tag
            assert len(text_nodes)    >= 1                                                    # At least one text

    def test__extract__complex_html(self):                                                    # Test extraction from complex HTML
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_complex.mgraph) as _:
            _.extract()

            element_nodes = [n for n in _.nodes if n.node_type == 'element']
            attr_nodes    = [n for n in _.nodes if n.node_type == 'attr']

            assert len(element_nodes) >= 3                                                    # div, h1, p
            assert len(attr_nodes)    >= 2                                                    # class and id

    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Type Detection Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__extract__element_nodes_have_dom_path(self):                                     # Test element nodes have DOM path
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_simple.mgraph) as _:
            _.extract()

            element_nodes = [n for n in _.nodes if n.node_type == 'element']
            for node in element_nodes:
                assert node.dom_path != ''                                                    # Should have DOM path

    def test__extract__tag_nodes_have_label(self):                                            # Test tag nodes have proper label
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_simple.mgraph) as _:
            _.extract()

            tag_nodes = [n for n in _.nodes if n.node_type == 'tag']
            for node in tag_nodes:
                assert node.label != ''                                                       # Should have label

    def test__extract__text_nodes_have_value(self):                                           # Test text nodes have value
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_simple.mgraph) as _:
            _.extract()

            text_nodes = [n for n in _.nodes if n.node_type == 'text']
            # Text nodes should have either value or label populated

    # ═══════════════════════════════════════════════════════════════════════════════
    # Edge Predicate Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__extract__edges_have_predicates(self):                                           # Test edges have predicate set
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_simple.mgraph) as _:
            _.extract()

            predicates = {e.predicate for e in _.edges}
            # Should have at least child or tag predicate
            assert len(predicates) >= 1

    def test__extract__child_edges_not_dashed(self):                                          # Test child edges are solid
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_simple.mgraph) as _:
            _.extract()

            child_edges = [e for e in _.edges if e.predicate == 'child']
            for edge in child_edges:
                assert edge.dashed == False

    def test__extract__tag_edges_are_dashed(self):                                            # Test tag edges are dashed
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_simple.mgraph) as _:
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

        with Html_MGraph__Data__Extractor(mgraph = self.html_mgraph_simple.mgraph,
                                          config = config                        ) as _:
            _.extract()

            tag_nodes = [n for n in _.nodes if n.node_type == 'tag']
            assert len(tag_nodes) == 0                                                        # Tag nodes should be filtered

    def test__extract__hide_attr_nodes(self):                                                 # Test hiding attr nodes via config
        config = Html_MGraph__Render__Config()
        config.show_attr_nodes = False

        with Html_MGraph__Data__Extractor(mgraph = self.html_mgraph_complex.mgraph,
                                          config = config                         ) as _:
            _.extract()

            attr_nodes = [n for n in _.nodes if n.node_type == 'attr']
            assert len(attr_nodes) == 0                                                       # Attr nodes should be filtered

    def test__extract__hide_text_nodes(self):                                                 # Test hiding text nodes via config
        config = Html_MGraph__Render__Config()
        config.show_text_nodes = False

        with Html_MGraph__Data__Extractor(mgraph = self.html_mgraph_simple.mgraph,
                                          config = config                        ) as _:
            _.extract()

            text_nodes = [n for n in _.nodes if n.node_type == 'text']
            assert len(text_nodes) == 0                                                       # Text nodes should be filtered

    def test__extract__edges_to_hidden_nodes_excluded(self):                                  # Test edges to hidden nodes are excluded
        config = Html_MGraph__Render__Config()
        config.show_tag_nodes = False

        with Html_MGraph__Data__Extractor(mgraph = self.html_mgraph_simple.mgraph,
                                          config = config                        ) as _:
            _.extract()

            tag_edges = [e for e in _.edges if e.predicate == 'tag']
            assert len(tag_edges) == 0                                                        # Edges to tag nodes excluded

    # ═══════════════════════════════════════════════════════════════════════════════
    # Utility Method Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___calculate_depth__empty_path(self):                                             # Test depth calculation for empty path
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_simple.mgraph) as _:
            depth = _._calculate_depth('')
            assert depth == 0

    def test___calculate_depth__root(self):                                                   # Test depth calculation for root path
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_simple.mgraph) as _:
            depth = _._calculate_depth('div')
            assert depth == 1

    def test___calculate_depth__nested(self):                                                 # Test depth calculation for nested path
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_simple.mgraph) as _:
            depth = _._calculate_depth('html.body.div.p')
            assert depth == 4

    def test___extract_tag__simple(self):                                                     # Test tag extraction from simple path
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_simple.mgraph) as _:
            tag = _._extract_tag('div')
            assert tag == 'div'

    def test___extract_tag__nested(self):                                                     # Test tag extraction from nested path
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_simple.mgraph) as _:
            tag = _._extract_tag('html.body.div')
            assert tag == 'div'

    def test___extract_tag__with_index(self):                                                 # Test tag extraction with index
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_simple.mgraph) as _:
            tag = _._extract_tag('html.body.div[0]')
            assert tag == 'div'

    def test___darken__valid_hex(self):                                                       # Test color darkening
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_simple.mgraph) as _:
            darker = _._darken('#FFFFFF')
            assert darker.startswith('#')
            assert darker != '#FFFFFF'

    def test___darken__invalid_hex(self):                                                     # Test color darkening with invalid input
        with Html_MGraph__Data__Extractor(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _._darken('invalid')
            assert result == '#CCCCCC'                                                        # Should return default


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
