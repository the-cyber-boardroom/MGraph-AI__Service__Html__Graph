from unittest                                                                       import TestCase
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                   import Html_MGraph
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__To__Dot import Html_MGraph__To__Dot
from mgraph_db.utils.testing.mgraph_test_ids import mgraph_test_ids
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.utils.Objects                                                      import base_classes


class test_Html_MGraph__To__Dot(TestCase):                                          # Test Html_MGraph to DOT conversion

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                         # Test default initialization
        with Html_MGraph__To__Dot() as _:
            assert type(_)         is Html_MGraph__To__Dot
            assert base_classes(_) == [Type_Safe, object]
            assert _.show_head     is True
            assert _.show_body     is True
            assert _.show_attrs    is True
            assert _.show_scripts  is True
            assert _.show_styles   is True
            assert _.use_clusters  is True
            assert _.show_legend   is False

    def test__init__custom_config(self):                                            # Test custom configuration
        with Html_MGraph__To__Dot(show_scripts=False, show_styles=False) as _:
            assert _.show_scripts is False
            assert _.show_styles  is False
            assert _.show_head    is True

    def test_colors_defined(self):                                                  # Test color schemes defined
        with Html_MGraph__To__Dot() as _:
            assert 'head'    in _.COLORS
            assert 'body'    in _.COLORS
            assert 'attrs'   in _.COLORS
            assert 'scripts' in _.COLORS
            assert 'styles'  in _.COLORS
            assert 'text'    in _.COLORS
            assert 'edge'    in _.COLORS

    # ═══════════════════════════════════════════════════════════════════════════
    # Convert - Full Graph Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert__minimal(self):                                                # Test minimal HTML conversion
        html   = '<html><head></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        with Html_MGraph__To__Dot() as converter:
            dot = converter.convert(mgraph)

            assert 'digraph Html_MGraph'   in dot
            assert 'rankdir=TB'            in dot
            assert 'subgraph cluster_head' in dot
            assert 'subgraph cluster_body' in dot
            assert '}'                     in dot


    def test_convert__with_content(self):                                           # Test HTML with content
        html = '''<html lang="en">
            <head><title>Test</title></head>
            <body><div class="main">Hello</div></body>
        </html>'''
        mgraph = Html_MGraph.from_html(html)

        with Html_MGraph__To__Dot() as converter:
            dot = converter.convert(mgraph)

            assert 'cluster_head'   in dot
            assert 'cluster_body'   in dot
            assert 'cluster_attrs'  in dot

    def test_convert__no_clusters(self):                                            # Test without cluster grouping
        html   = '<html><head></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        with Html_MGraph__To__Dot(use_clusters=False) as converter:
            dot = converter.convert(mgraph)

            assert 'digraph Html_MGraph' in dot
            assert 'subgraph cluster_'   not in dot

    def test_convert__with_legend(self):                                            # Test with legend enabled
        html   = '<html><head></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        with Html_MGraph__To__Dot(show_legend=True) as converter:
            dot = converter.convert(mgraph)

            assert 'cluster_legend' in dot
            assert 'Legend'         in dot

    def test_convert__selective_graphs(self):                                       # Test showing only specific graphs
        html   = '<html><head></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        with Html_MGraph__To__Dot(show_head=True, show_body=True,
                                   show_attrs=False, show_scripts=False, show_styles=False) as converter:
            dot = converter.convert(mgraph)

            assert 'cluster_head'    in dot
            assert 'cluster_body'    in dot
            assert 'cluster_attrs'   not in dot
            assert 'cluster_scripts' not in dot
            assert 'cluster_styles'  not in dot

    # ═══════════════════════════════════════════════════════════════════════════
    # Convert Single - Individual Graph Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_head_only(self):                                                       # Test head graph only
        html   = '<html><head><title>Test</title></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        with Html_MGraph__To__Dot() as converter:
            dot = converter.head_only(mgraph)

            assert 'digraph Head' in dot
            assert 'cluster_'     not in dot                                        # No clusters in single graph

    def test_body_only(self):                                                       # Test body graph only
        html   = '<html><head></head><body><div>Content</div></body></html>'
        mgraph = Html_MGraph.from_html(html)

        with Html_MGraph__To__Dot() as converter:
            dot = converter.body_only(mgraph)

            assert 'digraph Body' in dot

    def test_attrs_only(self):                                                      # Test attributes graph only
        html   = '<html lang="en"><head></head><body class="main"></body></html>'
        with mgraph_test_ids():
            mgraph = Html_MGraph.from_html(html)

        with Html_MGraph__To__Dot() as converter:
            dot = converter.attrs_only(mgraph)

            assert 'digraph Attrs' in dot

    def test_scripts_only(self):                                                    # Test scripts graph only
        html   = "<html><head></head><body><script>var x=1;</script></body></html>"
        mgraph = Html_MGraph.from_html(html)

        with Html_MGraph__To__Dot() as converter:
            dot = converter.scripts_only(mgraph)

            assert 'digraph Scripts' in dot

    def test_styles_only(self):                                                     # Test styles graph only
        html   = '<html><head><style>body{}</style></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        with Html_MGraph__To__Dot() as converter:
            dot = converter.styles_only(mgraph)

            assert 'digraph Styles' in dot

    # ═══════════════════════════════════════════════════════════════════════════
    # Node and Edge Rendering Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_nodes_have_labels(self):                                               # Test nodes have labels
        html   = '<html><head></head><body><p>Hello</p></body></html>'
        mgraph = Html_MGraph.from_html(html)

        with Html_MGraph__To__Dot() as converter:
            dot = converter.convert(mgraph)

            assert 'label=' in dot
            assert 'fillcolor=' in dot

    def test_edges_have_labels(self):                                               # Test edges have labels
        html   = '<html><head></head><body><div><p>Text</p></div></body></html>'
        mgraph = Html_MGraph.from_html(html)

        with Html_MGraph__To__Dot() as converter:
            dot = converter.convert(mgraph)

            assert '->' in dot                                                      # Edge arrows

    def test_cross_references_rendered(self):                                       # Test cross-references between graphs
        html   = '<html><head></head><body><div class="main"></div></body></html>'
        mgraph = Html_MGraph.from_html(html)

        with Html_MGraph__To__Dot() as converter:
            dot = converter.convert(mgraph)

            assert 'Cross-references' in dot
            assert 'style=dashed'     in dot

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Method Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__escape_label(self):                                                   # Test label escaping
        with Html_MGraph__To__Dot() as converter:
            assert converter._escape_label('hello')       == 'hello'
            assert converter._escape_label('say "hi"')    == 'say \\"hi\\"'
            assert converter._escape_label('line1\nline2') == 'line1\\nline2'
            assert converter._escape_label('back\\slash') == 'back\\\\slash'

    def test__safe_node_id(self):                                                   # Test safe node ID generation
        from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id import Node_Id
        from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id  import Obj_Id

        with Html_MGraph__To__Dot() as converter:
            node_id = Node_Id(Obj_Id())
            safe_id = converter._safe_node_id(node_id, 'body')

            assert safe_id.startswith('body_')
            assert str(node_id) in safe_id

    # ═══════════════════════════════════════════════════════════════════════════
    # Complex Document Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert__complex_document(self):                                       # Test complex HTML document
        html = '''<html lang="en">
            <head>
                <meta charset="utf-8">
                <title>Complex Page</title>
                <style>.main { color: red; }</style>
                <script>var config = {};</script>
            </head>
            <body class="page">
                <header id="top">
                    <nav>Menu</nav>
                </header>
                <main>
                    <article>
                        <h1>Title</h1>
                        <p>First paragraph</p>
                        <p>Second paragraph</p>
                    </article>
                </main>
                <script src="app.js"></script>
            </body>
        </html>'''

        mgraph = Html_MGraph.from_html(html)

        with Html_MGraph__To__Dot() as converter:
            dot = converter.convert(mgraph)

            # Verify structure
            assert 'digraph Html_MGraph' in dot
            assert 'cluster_head'        in dot
            assert 'cluster_body'        in dot
            assert 'cluster_attrs'       in dot
            assert 'cluster_scripts'     in dot
            assert 'cluster_styles'      in dot

            # Verify it's valid DOT (basic check)
            assert dot.count('{') == dot.count('}')
            assert dot.endswith('}')


    def test_convert__generates_valid_dot_structure(self):                          # Test DOT structure validity
        html   = '<html><head></head><body><div><p>Test</p></div></body></html>'
        mgraph = Html_MGraph.from_html(html)

        with Html_MGraph__To__Dot() as converter:
            dot = converter.convert(mgraph)

            # Basic DOT structure checks
            assert dot.startswith('digraph')
            assert dot.endswith('}')
            assert dot.count('{') == dot.count('}')

            # Should have nodes and edges
            lines = dot.split('\n')
            has_nodes = any('[label=' in line for line in lines)
            has_edges = any('->' in line for line in lines)

            assert has_nodes
            assert has_edges