from unittest                                                                       import TestCase

from mgraph_ai_service_html_graph.schemas.html.Schema__Html_MGraph import Schema__Html_MGraph__Stats__Document
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                   import Html_MGraph
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document  import Html_MGraph__Document
from mgraph_db.utils.testing.mgraph_test_ids                                        import mgraph_test_ids
from osbot_utils.testing.__ import __
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.utils.Objects                                                      import base_classes


class test_Html_MGraph(TestCase):                                               # Test Html_MGraph facade class

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                     # Test default initialization
        with Html_MGraph() as _:
            assert type(_)         is Html_MGraph
            assert base_classes(_) == [Type_Safe, object]
            assert _.document      is None

    # ═══════════════════════════════════════════════════════════════════════════
    # Factory Method Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_from_html__minimal(self):                                          # Test creating from minimal HTML
        html = '<html><head></head><body></body></html>'

        mgraph = Html_MGraph.from_html(html)

        assert type(mgraph)          is Html_MGraph
        assert type(mgraph.document) is Html_MGraph__Document
        assert mgraph.document.root_id is not None

    def test_from_html__with_content(self):                                     # Test creating from HTML with content
        html = '''<html lang="en">
            <head><title>Test</title></head>
            <body><div class="main">Hello</div></body>
        </html>'''

        mgraph = Html_MGraph.from_html(html)

        assert mgraph.document.root_id is not None
        assert mgraph.get_tag(mgraph.document.root_id) == 'html'

    def test_from_html_dict(self):                                              # Test creating from Html_Dict
        html_dict = {
            'tag'  : 'html',
            'attrs': {'lang': 'en'},
            'nodes': [
                {'tag': 'head', 'attrs': {}, 'nodes': []},
                {'tag': 'body', 'attrs': {}, 'nodes': []}
            ]
        }

        mgraph = Html_MGraph.from_html_dict(html_dict)

        assert type(mgraph) is Html_MGraph
        assert mgraph.document is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # Export Method Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_to_html(self):                                                     # Test HTML export
        original = '<html><head></head><body><p>Hello</p></body></html>'
        mgraph   = Html_MGraph.from_html(original)

        result = mgraph.to_html()

        assert '<!DOCTYPE html>' in result
        assert '<html>'          in result
        assert '<head>'          in result
        assert '<body>'          in result
        assert '<p>'             in result
        assert 'Hello'           in result

    def test_to_html_dict(self):                                                # Test Html_Dict export
        html   = '<html lang="en"><head></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        result = mgraph.to_html_dict()

        assert result['tag']          == 'html'
        assert result['attrs']['lang'] == 'en'
        assert 'nodes' in result

    def test_to_json(self):                                                     # Test JSON export
        html   = '<html><head></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        result = mgraph.to_json()

        assert type(result) is dict
        assert 'head'  in result
        assert 'body'  in result
        assert 'attributes' in result

    def test_to_dot__all(self):                                                 # Test DOT export - all graphs
        html   = '<html><head></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        result = mgraph.to_dot()

        assert 'digraph Html_MGraph' in result
        assert 'cluster_head'        in result
        assert 'cluster_body'        in result

    def test_to_dot__head_only(self):                                           # Test DOT export - head only
        html   = '<html><head><title>Test</title></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        result = mgraph.to_dot(graph='head')

        assert 'digraph Head' in result
        assert 'cluster_body' not in result

    def test_to_dot__body_only(self):                                           # Test DOT export - body only
        html   = '<html><head></head><body><div>Test</div></body></html>'
        mgraph = Html_MGraph.from_html(html)

        result = mgraph.to_dot(graph='body')

        assert 'digraph Body' in result
        assert 'cluster_head' not in result

    # ═══════════════════════════════════════════════════════════════════════════
    # Query Method Tests - Element Access
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_tag(self):                                                     # Test getting element tag
        html   = '<html><head></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        assert mgraph.get_tag(mgraph.root_id())      == 'html'
        assert mgraph.get_tag(mgraph.head_root_id()) == 'head'
        assert mgraph.get_tag(mgraph.body_root_id()) == 'body'

    def test_get_attributes(self):                                              # Test getting element attributes
        html   = '<html lang="en" dir="ltr"><head></head><body class="main"></body></html>'
        mgraph = Html_MGraph.from_html(html)

        html_attrs = mgraph.get_attributes(mgraph.root_id())
        body_attrs = mgraph.get_attributes(mgraph.body_root_id())

        assert html_attrs['lang']  == 'en'
        assert html_attrs['dir']   == 'ltr'
        assert body_attrs['class'] == 'main'

    def test_get_attribute(self):                                               # Test getting specific attribute
        html   = '<html lang="en"><head></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        assert mgraph.get_attribute(mgraph.root_id(), 'lang')    == 'en'
        assert mgraph.get_attribute(mgraph.root_id(), 'missing') is None

    # ═══════════════════════════════════════════════════════════════════════════
    # Query Method Tests - Structure Navigation
    # ═══════════════════════════════════════════════════════════════════════════

    def test_root_id(self):                                                     # Test root node access
        html   = '<html><head></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        assert mgraph.root_id() is not None
        assert mgraph.root_id() == mgraph.document.root_id

    def test_head_root_id(self):                                                # Test head root access
        html   = '<html><head></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        assert mgraph.head_root_id() is not None
        assert mgraph.get_tag(mgraph.head_root_id()) == 'head'

    def test_body_root_id(self):                                                # Test body root access
        html   = '<html><head></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        assert mgraph.body_root_id() is not None
        assert mgraph.get_tag(mgraph.body_root_id()) == 'body'

    def test_get_head_children(self):                                           # Test getting head children
        html   = '<html><head><title>Test</title><meta charset="utf-8"></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        children = mgraph.get_head_children()

        assert len(children) == 2

    def test_get_body_children(self):                                           # Test getting body children
        html   = '<html><head></head><body><div></div><p></p><span></span></body></html>'
        mgraph = Html_MGraph.from_html(html)

        children = mgraph.get_body_children()

        assert len(children) == 3

    # ═══════════════════════════════════════════════════════════════════════════
    # Query Method Tests - Content Access
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_script_content(self):                                          # Test getting script content
        html   = "<html><head></head><body><script>console.log('test');</script></body></html>"
        mgraph = Html_MGraph.from_html(html)

        children   = mgraph.get_body_children()
        script_id  = children[0]
        content    = mgraph.get_script_content(script_id)

        assert content == "console.log('test');"

    def test_get_style_content(self):                                           # Test getting style content
        html   = '<html><head><style>body { margin: 0; }</style></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        children  = mgraph.get_head_children()
        style_id  = children[0]
        content   = mgraph.get_style_content(style_id)

        assert content == 'body { margin: 0; }'

    def test_get_text_content(self):                                            # Test getting text content
        html   = '<html><head><title>My Title</title></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        children  = mgraph.get_head_children()
        title_id  = children[0]
        text      = mgraph.get_text_content(title_id)

        assert text == 'My Title'

    # ═══════════════════════════════════════════════════════════════════════════
    # Graph Access Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_head_graph_property(self):                                         # Test direct head graph access
        html   = '<html><head></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        assert mgraph.head_graph is mgraph.document.head_graph

    def test_body_graph_property(self):                                         # Test direct body graph access
        html   = '<html><head></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        assert mgraph.body_graph is mgraph.document.body_graph

    def test_attrs_graph_property(self):                                        # Test direct attrs graph access
        html   = '<html><head></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        assert mgraph.attrs_graph is mgraph.document.attrs_graph

    def test_scripts_graph_property(self):                                      # Test direct scripts graph access
        html   = '<html><head></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        assert mgraph.scripts_graph is mgraph.document.scripts_graph

    def test_styles_graph_property(self):                                       # Test direct styles graph access
        html   = '<html><head></head><body></body></html>'
        mgraph = Html_MGraph.from_html(html)

        assert mgraph.styles_graph is mgraph.document.styles_graph

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_stats(self):                                                       # Test statistics
        html   = '<html><head><title>Test</title></head><body><div>Content</div></body></html>'
        with mgraph_test_ids():
            mgraph = Html_MGraph.from_html(html)

            stats = mgraph.stats()
            assert type(stats) is Schema__Html_MGraph__Stats__Document
            assert stats.obj() == __(document=__(total_nodes=6,
                                                 total_edges=5,
                                                 root_id='c0000001'),
                                     head=__(element_nodes=2,
                                             text_nodes=1,
                                             total_nodes=4,
                                             total_edges=2,
                                             root_id='c0000016'),
                                     body=__(element_nodes=2,
                                             text_nodes=1,
                                             total_nodes=4,
                                             total_edges=2,
                                             root_id='c0000021'),
                                     attributes=__(registered_elements=5,
                                                   total_attributes=0,
                                                   unique_tags=5,
                                                   total_nodes=12,
                                                   total_edges=10,
                                                   root_id='c0000005'),
                                     scripts=__(total_scripts=0,
                                                inline_scripts=0,
                                                external_scripts=0,
                                                total_nodes=2,
                                                total_edges=0,
                                                root_id='c0000007'),
                                     styles=__(total_styles=0,
                                               inline_styles=0,
                                               external_styles=0,
                                               total_nodes=2,
                                               total_edges=0,
                                               root_id='c0000009'))


    # ═══════════════════════════════════════════════════════════════════════════
    # Element Info Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_element_info(self):                                                # Test comprehensive element info
        html   = '<html><head></head><body><div class="main" id="app">Hello</div></body></html>'
        with  mgraph_test_ids():
            mgraph = Html_MGraph.from_html(html)

        children = mgraph.get_body_children()
        div_id   = children[0]
        info     = mgraph.element_info(div_id)
        assert info == {'attributes': {'class': 'main', 'id': 'app'},
                         'node_id': 'c0000020',
                         'tag': 'div'}
        assert info['tag']             == 'div'
        assert info['attributes']['class']  == 'main'
        assert info['attributes']['id']     == 'app'

    # ═══════════════════════════════════════════════════════════════════════════
    # Round-Trip Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_roundtrip__simple(self):                                           # Test simple round-trip
        original = '<html><head></head><body><p>Hello</p></body></html>'

        mgraph = Html_MGraph.from_html(original)
        result = mgraph.to_html()

        assert '<html>'  in result
        assert '<head>'  in result
        assert '<body>'  in result
        assert '<p>'     in result
        assert 'Hello'   in result

    def test_roundtrip__complex(self):                                          # Test complex round-trip
        original = '''<html lang="en">
            <head>
                <meta charset="utf-8">
                <title>Test Page</title>
                <style>.main { color: red; }</style>
            </head>
            <body class="page">
                <header id="top">Header</header>
                <main>
                    <article>
                        <h1>Title</h1>
                        <p>Content</p>
                    </article>
                </main>
                <script>console.log('loaded');</script>
            </body>
        </html>'''

        mgraph = Html_MGraph.from_html(original)
        result = mgraph.to_html()

        # Verify all content preserved
        assert 'lang="en"'           in result
        assert 'charset="utf-8"'     in result
        assert 'Test Page'           in result
        assert '.main { color: red; }' in result
        assert 'class="page"'        in result
        assert 'id="top"'            in result
        assert 'Header'              in result
        assert '<article>'           in result
        assert '<h1>'                in result
        assert 'Title'               in result
        assert 'Content'             in result
        assert "console.log('loaded');" in result

    def test_roundtrip__to_dict_and_back(self):                                 # Test round-trip through dict
        original = '<html lang="en"><head><title>Test</title></head><body><div>Hi</div></body></html>'

        mgraph1   = Html_MGraph.from_html(original)
        html_dict = mgraph1.to_html_dict()
        mgraph2   = Html_MGraph.from_html_dict(html_dict)
        result    = mgraph2.to_html()

        assert 'lang="en"' in result
        assert 'Test'      in result
        assert 'Hi'        in result