# ═══════════════════════════════════════════════════════════════════════════════
# Test: MGraph__Engine__Dot
#
# Tests the DOT/Graphviz rendering engine for MGraph export.
# Validates DOT syntax generation, node/edge formatting, and config options.
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                   import TestCase
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Dot   import MGraph__Engine__Config__Dot
from mgraph_db.utils.testing.mgraph_test_ids                                                    import mgraph_test_ids
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.utils.Objects                                                                  import base_classes
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                               import Html_MGraph
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Base                  import MGraph__Engine__Base
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Dot                   import MGraph__Engine__Dot



class test_MGraph__Engine__Dot(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simple_html = '<html><body><div><p>Hello</p><span>World</span></div></body></html>'
        cls.complex_html = '''
            <html>
                <body>
                    <div class="container">
                        <h1>Title</h1>
                        <p>First paragraph</p>
                        <p>Second paragraph</p>
                    </div>
                </body>
            </html>
        '''
        with mgraph_test_ids():
            cls.html_mgraph_simple  = Html_MGraph.from_html(cls.simple_html)
            cls.mgraph_simple       = cls.html_mgraph_simple.body_graph.mgraph

            cls.html_mgraph_complex = Html_MGraph.from_html(cls.complex_html)
            cls.mgraph_complex      = cls.html_mgraph_complex.body_graph.mgraph

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test engine initialization
        with MGraph__Engine__Dot() as _:
            assert type(_) is MGraph__Engine__Dot
            assert isinstance(_, MGraph__Engine__Base)
            assert isinstance(_, Type_Safe)

    def test__init__creates_default_config(self):                                # Test auto-creates config
        with MGraph__Engine__Dot() as _:
            assert _.config is not None
            assert type(_.config) is MGraph__Engine__Config__Dot

    def test__init__with_mgraph(self):                                           # Test initialization with MGraph
        with MGraph__Engine__Dot(mgraph=self.mgraph_simple) as _:
            assert _.mgraph is self.mgraph_simple

    def test__init__with_custom_config(self):                                    # Test initialization with config
        config = MGraph__Engine__Config__Dot(rankdir='LR')
        with MGraph__Engine__Dot(config=config) as _:
            assert _.config is config
            assert _.config.rankdir == 'LR'

    def test__inheritance(self):                                                 # Test inheritance chain
        engine = MGraph__Engine__Dot()
        assert base_classes(engine) == [MGraph__Engine__Base, Type_Safe, object]

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Basic Structure
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__returns_string(self):                                      # Test export returns string
        with MGraph__Engine__Dot(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert type(result) is str

    def test__export__starts_with_digraph(self):                                 # Test DOT starts correctly
        with MGraph__Engine__Dot(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert result.startswith('digraph G {')

    def test__export__ends_with_closing_brace(self):                             # Test DOT ends correctly
        with MGraph__Engine__Dot(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert result.strip().endswith('}')

    def test__export__contains_graph_attributes(self):                           # Test graph attributes present
        with MGraph__Engine__Dot(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert 'graph [' in result
            assert 'rankdir=' in result
            assert 'splines=' in result

    def test__export__contains_node_defaults(self):                              # Test node defaults present
        with MGraph__Engine__Dot(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert 'node [' in result
            assert 'shape=' in result
            assert 'style=' in result

    def test__export__contains_edge_defaults(self):                              # Test edge defaults present
        with MGraph__Engine__Dot(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert 'edge [' in result
            assert 'color=' in result
            assert 'arrowsize=' in result

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Node Formatting
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__contains_node_definitions(self):                           # Test nodes in output
        with MGraph__Engine__Dot(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert 'label=' in result                                            # Nodes have labels

    def test__export__node_has_label(self):                                      # Test node has label attribute
        with MGraph__Engine__Dot(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert 'label=' in result

    def test__export__node_uses_text_content(self):                              # Test text content in labels
        with MGraph__Engine__Dot(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert 'Hello' in result or 'World' in result                        # Text nodes visible

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Edge Formatting
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__contains_edge_definitions(self):                           # Test edges in output
        with MGraph__Engine__Dot(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert '->' in result                                                # DOT edge syntax

    def test__export__edge_connects_nodes(self):                                 # Test edges connect right nodes
        with MGraph__Engine__Dot(mgraph=self.mgraph_simple) as _:
            result = _.export()
            lines  = result.split('\n')
            edges  = [l for l in lines if '->' in l]
            assert len(edges) > 0                                                # Has edge definitions

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Config Options
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__respects_rankdir_config(self):                             # Test rankdir in output
        config = MGraph__Engine__Config__Dot(rankdir='LR')
        with MGraph__Engine__Dot(mgraph=self.mgraph_simple, config=config) as _:
            result = _.export()
            assert 'rankdir=LR' in result

    def test__export__respects_splines_config(self):                             # Test splines in output
        config = MGraph__Engine__Config__Dot(splines='ortho')
        with MGraph__Engine__Dot(mgraph=self.mgraph_simple, config=config) as _:
            result = _.export()
            assert 'splines=ortho' in result

    def test__export__respects_bgcolor_config(self):                             # Test bgcolor in output
        config = MGraph__Engine__Config__Dot(bgcolor='#ffffff')
        with MGraph__Engine__Dot(mgraph=self.mgraph_simple, config=config) as _:
            result = _.export()
            assert 'bgcolor="#ffffff"' in result

    def test__export__respects_concentrate_config(self):                         # Test concentrate in output
        config = MGraph__Engine__Config__Dot(concentrate=True)
        with MGraph__Engine__Dot(mgraph=self.mgraph_simple, config=config) as _:
            result = _.export()
            assert 'concentrate=true' in result

    def test__export__respects_node_shape_config(self):                          # Test node shape in defaults
        config = MGraph__Engine__Config__Dot(node_shape='ellipse')
        with MGraph__Engine__Dot(mgraph=self.mgraph_simple, config=config) as _:
            result = _.export()
            assert 'shape=ellipse' in result

    def test__export__respects_font_config(self):                                # Test font in output
        config = MGraph__Engine__Config__Dot(font_name='Helvetica', font_size=14)
        with MGraph__Engine__Dot(mgraph=self.mgraph_simple, config=config) as _:
            result = _.export()
            assert 'fontname="Helvetica"' in result
            assert 'fontsize=14' in result

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Complex Graph
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__complex_graph_structure(self):                             # Test complex HTML export
        with MGraph__Engine__Dot(mgraph=self.mgraph_complex) as _:
            result = _.export()
            assert result.startswith('digraph G {')
            assert '->' in result
            lines = result.split('\n')
            assert len(lines) > 5                                                # Has substantial content

    def test__export__complex_graph_has_many_nodes(self):                        # Test complex graph nodes
        with MGraph__Engine__Dot(mgraph=self.mgraph_complex) as _:
            result = _.export()
            lines  = result.split('\n')
            node_lines = [l for l in lines if 'label=' in l and '->' not in l]
            assert len(node_lines) >= 3                                          # Multiple nodes

    def test__export__complex_graph_has_many_edges(self):                        # Test complex graph edges
        with MGraph__Engine__Dot(mgraph=self.mgraph_complex) as _:
            result = _.export()
            lines  = result.split('\n')
            edge_lines = [l for l in lines if '->' in l]
            assert len(edge_lines) >= 3                                          # Multiple edges

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Empty Graph
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__empty_html(self):                                          # Test minimal HTML
        html = '<div></div>'
        with mgraph_test_ids():
            html_mgraph = Html_MGraph.from_html(html)
            mgraph      = html_mgraph.body_graph.mgraph

        with MGraph__Engine__Dot(mgraph=mgraph) as _:
            result = _.export()
            assert result.startswith('digraph G {')
            assert result.strip().endswith('}')

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Label Truncation
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__truncates_long_labels(self):                               # Test label truncation
        long_text = 'A' * 100
        html = f'<html><body><div>{long_text}</div></body></html>'
        with mgraph_test_ids():
            html_mgraph = Html_MGraph.from_html(html)
            mgraph      = html_mgraph.body_graph.mgraph

        config = MGraph__Engine__Config__Dot(max_label_len=20)
        with MGraph__Engine__Dot(mgraph=mgraph, config=config) as _:
            result = _.export()
            assert long_text not in result                                       # Full text not present
            assert '...' in result                                               # Truncation indicator

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Special Characters
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__escapes_quotes_in_labels(self):                            # Test quote escaping
        html = '<html><body><div>Say "Hello"</div></body></html>'
        with mgraph_test_ids():
            html_mgraph = Html_MGraph.from_html(html)
            mgraph      = html_mgraph.body_graph.mgraph

        with MGraph__Engine__Dot(mgraph=mgraph) as _:
            result = _.export()
            assert result == """\
digraph G {
  graph [rankdir=TB; splines=true; nodesep=0.25; ranksep=0.5; bgcolor="transparent"];
  node [shape=box; style="rounded,filled"; fillcolor="#e8f4f8"; fontcolor="#333333"; fontname="Arial"; fontsize=10];
  edge [color="#666666"; arrowsize=0.7; fontname="Arial"; fontsize=8];
  "c0000003" [label="c0000003", ];
  "c0000016" [label="body", ];
  "c0000018" [label="body.div", ];
  "c0000020" [label="Say \\"Hello\\"", ];
  "c0000016" -> "c0000018" [label="child"];
  "c0000018" -> "c0000020" [label="text"];
}"""
            assert '\\"Hello\\"' in result or 'Say' in result                    # Escaped or present

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Predictable IDs
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__uses_predictable_ids(self):                                # Test mgraph_test_ids works
        html = '<div><p>Test</p></div>'
        with mgraph_test_ids():
            html_mgraph = Html_MGraph.from_html(html)
            mgraph      = html_mgraph.body_graph.mgraph

        with MGraph__Engine__Dot(mgraph=mgraph) as _:
            result = _.export()
            # With mgraph_test_ids, IDs should be predictable patterns
            assert 'digraph G {' in result