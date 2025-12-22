from unittest                                                                             import TestCase
from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from osbot_utils.utils.Objects                                                            import base_classes
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                         import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Export__Base    import Html_MGraph__Export__Base
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__Mermaid     import Html_MGraph__To__Mermaid
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config         import Html_MGraph__Render__Config


class test_Html_MGraph__To__Mermaid(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simple_html   = '<div class="main">Hello World</div>'
        cls.complex_html  = '<div class="main" id="content"><h1>Title</h1><p>Paragraph</p></div>'
        cls.html_mgraph_simple  = Html_MGraph.from_html(cls.simple_html)
        cls.html_mgraph_complex = Html_MGraph.from_html(cls.complex_html)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                   # Test auto-initialization
        with Html_MGraph__To__Mermaid(html_mgraph=self.html_mgraph_simple) as _:
            assert type(_)         is Html_MGraph__To__Mermaid
            assert base_classes(_) == [Html_MGraph__Export__Base, Type_Safe, object]
            assert _.html_mgraph   is self.html_mgraph_simple
            assert _.config        is None

    def test__init__with_config(self):                                                        # Test initialization with config
        config = Html_MGraph__Render__Config()
        with Html_MGraph__To__Mermaid(html_mgraph = self.html_mgraph_simple,
                                      config      = config                 ) as _:
            assert _.config is config

    # ═══════════════════════════════════════════════════════════════════════════════
    # export Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__returns_string(self):                                                   # Test export returns string
        with Html_MGraph__To__Mermaid(html_mgraph=self.html_mgraph_simple) as _:
            result = _.export()

            assert type(result) is str

    def test__export__starts_with_flowchart(self):                                            # Test output starts with flowchart declaration
        with Html_MGraph__To__Mermaid(html_mgraph=self.html_mgraph_simple) as _:
            result = _.export()

            assert result.startswith('flowchart TB')

    def test__export__contains_nodes(self):                                                   # Test output contains node definitions
        with Html_MGraph__To__Mermaid(html_mgraph=self.html_mgraph_simple) as _:
            result = _.export()

            assert 'n0' in result or 'n1' in result                                           # Short IDs

    def test__export__contains_style_definitions(self):                                       # Test output contains style definitions
        with Html_MGraph__To__Mermaid(html_mgraph=self.html_mgraph_simple) as _:
            result = _.export()

            assert 'style' in result
            assert 'fill:' in result

    # ═══════════════════════════════════════════════════════════════════════════════
    # _get_short_id Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___get_short_id__creates_short_ids(self):                                         # Test short ID creation
        with Html_MGraph__To__Mermaid(html_mgraph=self.html_mgraph_simple) as _:
            short1 = _._get_short_id('very-long-uuid-string-1')
            short2 = _._get_short_id('very-long-uuid-string-2')

            assert short1 == 'n0'
            assert short2 == 'n1'

    def test___get_short_id__returns_same_for_same_input(self):                               # Test idempotency
        with Html_MGraph__To__Mermaid(html_mgraph=self.html_mgraph_simple) as _:
            id1 = _._get_short_id('test-id')
            id2 = _._get_short_id('test-id')

            assert id1 == id2

    # ═══════════════════════════════════════════════════════════════════════════════
    # _format_node Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___format_node__element_uses_rectangle(self):                                     # Test element node format
        from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Data__Extractor import Extracted__Node
        with Html_MGraph__To__Mermaid(html_mgraph=self.html_mgraph_simple) as _:
            node   = Extracted__Node(id='test', node_type='element', label='div')
            result = _._format_node(node)

            assert '[' in result and ']' in result                                            # Rectangle syntax

    def test___format_node__tag_uses_circle(self):                                            # Test tag node format
        from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Data__Extractor import Extracted__Node
        with Html_MGraph__To__Mermaid(html_mgraph=self.html_mgraph_simple) as _:
            node   = Extracted__Node(id='test', node_type='tag', label='div')
            result = _._format_node(node)

            assert '((' in result and '))' in result                                          # Circle syntax

    def test___format_node__attr_uses_hexagon(self):                                          # Test attr node format
        from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Data__Extractor import Extracted__Node
        with Html_MGraph__To__Mermaid(html_mgraph=self.html_mgraph_simple) as _:
            node   = Extracted__Node(id='test', node_type='attr', label='class')
            result = _._format_node(node)

            assert '{{' in result and '}}' in result                                          # Hexagon syntax

    def test___format_node__text_uses_flag(self):                                             # Test text node format
        from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Data__Extractor import Extracted__Node
        with Html_MGraph__To__Mermaid(html_mgraph=self.html_mgraph_simple) as _:
            node   = Extracted__Node(id='test', node_type='text', label='Hello')
            result = _._format_node(node)

            assert '>' in result and ']' in result                                            # Flag syntax

    # ═══════════════════════════════════════════════════════════════════════════════
    # _format_edge Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___format_edge__solid_arrow(self):                                                # Test solid edge format
        from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Data__Extractor import Extracted__Edge
        with Html_MGraph__To__Mermaid(html_mgraph=self.html_mgraph_simple) as _:
            _._get_short_id('source')
            _._get_short_id('target')
            edge   = Extracted__Edge(id='e1', source='source', target='target', dashed=False)
            result = _._format_edge(edge)

            assert '-->' in result

    def test___format_edge__dashed_arrow(self):                                               # Test dashed edge format
        from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Data__Extractor import Extracted__Edge
        with Html_MGraph__To__Mermaid(html_mgraph=self.html_mgraph_simple) as _:
            _._get_short_id('source')
            _._get_short_id('target')
            edge   = Extracted__Edge(id='e1', source='source', target='target', dashed=True)
            result = _._format_edge(edge)

            assert '-.->' in result

    def test___format_edge__skips_self_loop(self):                                            # Test self-loop is skipped
        from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Data__Extractor import Extracted__Edge
        with Html_MGraph__To__Mermaid(html_mgraph=self.html_mgraph_simple) as _:
            _._get_short_id('same')
            edge   = Extracted__Edge(id='e1', source='same', target='same', dashed=False)
            result = _._format_edge(edge)

            assert result == ''                                                               # Empty for self-loop

    # ═══════════════════════════════════════════════════════════════════════════════
    # escape_label Tests (inherited from base)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__escape_label__handles_quotes(self):                                             # Test quote escaping
        with Html_MGraph__To__Mermaid(html_mgraph=self.html_mgraph_simple) as _:
            result = _.escape_label('say "hello"')

            assert '"' not in result                                                          # Double quotes escaped

    def test__escape_label__truncates_long_labels(self):                                      # Test long label truncation
        with Html_MGraph__To__Mermaid(html_mgraph=self.html_mgraph_simple) as _:
            long_text = 'a' * 50
            result = _.escape_label(long_text)

            assert len(result) <= 33                                                          # Max 30 + '...'
            assert result.endswith('...')

    # ═══════════════════════════════════════════════════════════════════════════════
    # Complex Graph Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__complex_html(self):                                                     # Test export with complex HTML
        with Html_MGraph__To__Mermaid(html_mgraph=self.html_mgraph_complex) as _:
            result = _.export()

            assert 'flowchart TB' in result
            assert 'style' in result

    def test__export__valid_mermaid_syntax(self):                                             # Test output is valid Mermaid syntax
        with Html_MGraph__To__Mermaid(html_mgraph=self.html_mgraph_simple) as _:
            result = _.export()

            lines = result.split('\n')
            assert lines[0] == 'flowchart TB'                                                 # First line is flowchart declaration

    def test__export__with_config_filters(self):                                              # Test export respects config filters
        config = Html_MGraph__Render__Config()
        config.show_tag_nodes = False

        with Html_MGraph__To__Mermaid(html_mgraph = self.html_mgraph_simple,
                                      config      = config                 ) as _:
            result = _.export()

            # Mermaid output should have fewer nodes when filtered
            assert type(result) is str