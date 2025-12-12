from unittest                                                                             import TestCase
from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from osbot_utils.utils.Objects                                                            import base_classes
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph                          import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__Mermaid     import Html_MGraph__To__Mermaid
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Data__Extractor import Extracted__Node, Extracted__Edge
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config         import Html_MGraph__Render__Config


class test_Html_MGraph__To__Mermaid(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simple_html_dict  = SIMPLE_HTML_DICT
        cls.complex_html_dict = COMPLEX_HTML_DICT
        cls.html_mgraph_simple  = Html_MGraph.from_html_dict(cls.simple_html_dict)
        cls.html_mgraph_complex = Html_MGraph.from_html_dict(cls.complex_html_dict)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                   # Test auto-initialization
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            assert type(_)         is Html_MGraph__To__Mermaid
            assert base_classes(_) == [Type_Safe, object]
            assert _.mgraph        is self.html_mgraph_simple.mgraph
            assert _.config        is None
            assert _._id_map       == {}
            assert _._id_counter   == 0

    def test__init__with_config(self):                                                        # Test initialization with config
        config = Html_MGraph__Render__Config()
        with Html_MGraph__To__Mermaid(mgraph = self.html_mgraph_simple.mgraph,
                                      config = config                        ) as _:
            assert _.config is config

    # ═══════════════════════════════════════════════════════════════════════════════
    # export Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__returns_string(self):                                                   # Test export returns string
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()

            assert type(result) is str
            assert len(result) > 0

    def test__export__starts_with_flowchart(self):                                            # Test output starts with flowchart declaration
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()

            assert result.startswith('flowchart TB')

    def test__export__contains_nodes(self):                                                   # Test output contains node definitions
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()

            # Should contain at least one node definition (nX[...])
            assert 'n0' in result

    def test__export__contains_edges(self):                                                   # Test output contains edge definitions
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()

            # Should contain arrow syntax
            assert '-->' in result or '-.->' in result

    def test__export__contains_styles(self):                                                  # Test output contains style definitions
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()

            assert 'style' in result

    # ═══════════════════════════════════════════════════════════════════════════════
    # _get_short_id Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___get_short_id__creates_new_id(self):                                            # Test short ID creation
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            short_id = _._get_short_id('some-long-uuid-string')
            assert short_id == 'n0'

    def test___get_short_id__returns_same_id_for_same_input(self):                            # Test ID consistency
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            id1 = _._get_short_id('test-id')
            id2 = _._get_short_id('test-id')
            assert id1 == id2

    def test___get_short_id__increments_counter(self):                                        # Test counter increments for different IDs
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            id1 = _._get_short_id('first')
            id2 = _._get_short_id('second')
            id3 = _._get_short_id('third')

            assert id1 == 'n0'
            assert id2 == 'n1'
            assert id3 == 'n2'

    # ═══════════════════════════════════════════════════════════════════════════════
    # _format_node Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___format_node__element(self):                                                    # Test element node formatting (rectangle)
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            node   = Extracted__Node(id='n1', node_type='element', label='div')
            result = _._format_node(node)

            assert '[' in result and ']' in result                                            # Rectangle syntax

    def test___format_node__tag(self):                                                        # Test tag node formatting (circle)
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            node   = Extracted__Node(id='n1', node_type='tag', label='div')
            result = _._format_node(node)

            assert '((' in result and '))' in result                                          # Circle syntax

    def test___format_node__attr(self):                                                       # Test attr node formatting (hexagon)
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            node   = Extracted__Node(id='n1', node_type='attr', label='class=main')
            result = _._format_node(node)

            assert '{{' in result and '}}' in result                                          # Hexagon syntax

    def test___format_node__text(self):                                                       # Test text node formatting (flag)
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            node   = Extracted__Node(id='n1', node_type='text', label='Hello')
            result = _._format_node(node)

            assert '>' in result and ']' in result                                            # Flag syntax

    # ═══════════════════════════════════════════════════════════════════════════════
    # _format_edge Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___format_edge__solid(self):                                                      # Test solid edge formatting
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            _._get_short_id('source')                                                         # Register IDs first
            _._get_short_id('target')
            edge   = Extracted__Edge(id='e1', source='source', target='target', dashed=False)
            result = _._format_edge(edge)

            assert '-->' in result

    def test___format_edge__dashed(self):                                                     # Test dashed edge formatting
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            _._get_short_id('source')
            _._get_short_id('target')
            edge   = Extracted__Edge(id='e1', source='source', target='target', dashed=True)
            result = _._format_edge(edge)

            assert '-.->' in result

    def test___format_edge__self_loop_returns_empty(self):                                    # Test self-loop returns empty
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            _._get_short_id('same')
            edge   = Extracted__Edge(id='e1', source='same', target='same', dashed=False)
            result = _._format_edge(edge)

            assert result == ''

    # ═══════════════════════════════════════════════════════════════════════════════
    # _escape_label Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___escape_label__empty(self):                                                     # Test escaping empty string
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _._escape_label('')
            assert result == ''

    def test___escape_label__removes_special_chars(self):                                     # Test special characters removed
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _._escape_label('<div>[test]{hello}(world)')
            assert '<' not in result
            assert '>' not in result
            assert '[' not in result
            assert ']' not in result
            assert '{' not in result
            assert '}' not in result
            assert '(' not in result
            assert ')' not in result

    def test___escape_label__replaces_quotes(self):                                           # Test double quotes replaced
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _._escape_label('class="main"')
            assert '"' not in result

    def test___escape_label__truncates_long_labels(self):                                     # Test long labels are truncated
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            long_label = 'a' * 50
            result     = _._escape_label(long_label)

            assert len(result) <= 33                                                          # 30 + '...'
            assert result.endswith('...')

    def test___escape_label__removes_newlines(self):                                          # Test newlines replaced
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _._escape_label('line1\nline2')
            assert '\n' not in result

    # ═══════════════════════════════════════════════════════════════════════════════
    # Complex Graph Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__complex_html(self):                                                     # Test export with complex HTML
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_complex.mgraph) as _:
            result = _.export()

            assert 'flowchart TB' in result
            assert 'style' in result
            lines = result.split('\n')
            assert len(lines) > 5                                                             # Should have multiple lines

    def test__export__with_config_filters(self):                                              # Test export respects config filters
        config = Html_MGraph__Render__Config()
        config.show_tag_nodes = False

        with Html_MGraph__To__Mermaid(mgraph = self.html_mgraph_simple.mgraph,
                                      config = config                        ) as _:
            result = _.export()

            # Should still be valid Mermaid
            assert 'flowchart TB' in result

    def test__export__valid_mermaid_syntax(self):                                             # Test output is valid Mermaid
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.export()

            # Basic validation - no unclosed brackets
            assert result.count('[') == result.count(']') or '((' in result
            # Arrows are properly formatted
            assert '-.->' in result or '-->' in result

    def test__export__resets_id_map(self):                                                    # Test ID map resets on each export
        with Html_MGraph__To__Mermaid(mgraph=self.html_mgraph_simple.mgraph) as _:
            result1 = _.export()
            result2 = _.export()

            # Both should start IDs from n0
            assert 'n0' in result1
            assert 'n0' in result2


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
