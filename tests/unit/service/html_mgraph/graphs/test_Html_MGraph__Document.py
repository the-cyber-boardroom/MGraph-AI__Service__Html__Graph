from unittest                                                                                       import TestCase
from mgraph_ai_service_html_graph.schemas.html.Schema__Html_MGraph                                  import Schema__Html_MGraph__Stats__Document
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document    import Html__To__Html_MGraph__Document
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document    import SCRIPT_TAGS, STYLE_TAGS
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document                  import Html_MGraph__Document
from mgraph_db.utils.testing.mgraph_test_ids                                                        import mgraph_test_ids
from osbot_utils.testing.__                                                                         import __
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.utils.Objects                                                                      import base_classes


class test_Html__To__Html_MGraph__Document(TestCase):                           # Test HTML to multi-graph conversion

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                     # Test default initialization
        with Html__To__Html_MGraph__Document() as _:
            assert type(_)         is Html__To__Html_MGraph__Document
            assert base_classes(_) == [Type_Safe, object]

    def test_constants(self):                                                   # Test module constants
        assert SCRIPT_TAGS == {'script'}
        assert STYLE_TAGS  == {'style', 'link'}

    # ═══════════════════════════════════════════════════════════════════════════
    # Convert Tests - Basic HTML
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert_minimal_html(self):                                        # Test minimal HTML conversion
        html = "<html><head></head><body></body></html>"

        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            assert type(doc)  is Html_MGraph__Document
            assert doc.root_id is not None

    def test_convert_simple_html(self):                                         # Test simple HTML conversion
        html = """
        <html lang="en">
            <head>
                <title>Test Page</title>
            </head>
            <body class="container">
                <div id="main">Hello World</div>
            </body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            assert doc.root_id is not None                                      # Document has root
            assert doc.head_graph.root_id is not None                           # Head graph populated
            assert doc.body_graph.root_id is not None                           # Body graph populated

    def test_convert_html_with_lang_attribute(self):                            # Test <html> attributes are captured
        html = '<html lang="en" dir="ltr"><head></head><body></body></html>'

        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            attrs = doc.get_attributes(doc.root_id)
            assert attrs.get('lang') == 'en'
            assert attrs.get('dir')  == 'ltr'

    # ═══════════════════════════════════════════════════════════════════════════
    # Convert Tests - Head Section
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert_head_with_meta(self):                                      # Test <head> with meta tags
        html = """
        <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width">
            </head>
            <body></body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            metas = doc.get_elements_by_tag('meta')
            assert len(metas) == 2

            charset_found = False
            for meta_id in metas:
                if doc.get_attribute(meta_id, 'charset') == 'utf-8':
                    charset_found = True
            assert charset_found

    def test_convert_head_with_title(self):                                     # Test <head> with title and text
        html = """
        <html>
            <head>
                <title>My Page Title</title>
            </head>
            <body></body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            titles = doc.get_elements_by_tag('title')
            assert len(titles) == 1

            title_id = titles[0]
            content  = doc.get_text_content(title_id, in_head=True)
            assert content == 'My Page Title'

    def test_convert_head_with_style(self):                                     # Test <head> with inline style
        html = """
        <html>
            <head>
                <style>.container { display: flex; }</style>
            </head>
            <body></body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            styles = doc.styles_graph.get_all_styles()
            assert len(styles) == 1

            style_id = styles[0]
            content  = doc.get_style_content(style_id)
            assert 'display: flex' in content

    def test_convert_head_with_link(self):                                      # Test <head> with external stylesheet link
        html = """
        <html>
            <head>
                <link rel="stylesheet" href="styles.css">
            </head>
            <body></body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            links = doc.get_elements_by_tag('link')
            assert len(links) == 1

            link_id = links[0]
            assert doc.get_attribute(link_id, 'rel')  == 'stylesheet'
            assert doc.get_attribute(link_id, 'href') == 'styles.css'

            assert doc.styles_graph.is_external_style(link_id) is True          # Registered in styles graph

    def test_convert_head_with_script(self):                                    # Test <head> with inline script
        html = """
        <html>
            <head>
                <script>console.log('head script');</script>
            </head>
            <body></body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            scripts = doc.scripts_graph.get_all_scripts()
            assert len(scripts) == 1

            script_id = scripts[0]
            content   = doc.get_script_content(script_id)
            assert "console.log('head script')" in content

    def test_convert_head_attributes(self):                                     # Test <head> element attributes
        html = """
        <html>
            <head data-theme="dark">
                <title>Test</title>
            </head>
            <body></body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            head_id = doc.head_graph.root_id
            attrs   = doc.get_attributes(head_id)
            assert attrs.get('data-theme') == 'dark'

    # ═══════════════════════════════════════════════════════════════════════════
    # Convert Tests - Body Section
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert_body_with_div(self):                                       # Test <body> with div elements
        html = """
        <html>
            <head></head>
            <body>
                <div id="container" class="main">
                    <div id="nested">Content</div>
                </div>
            </body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            divs = doc.get_elements_by_tag('div')
            assert len(divs) == 2

            container_found = False
            nested_found    = False
            for div_id in divs:
                if doc.get_attribute(div_id, 'id') == 'container':
                    container_found = True
                    assert doc.get_attribute(div_id, 'class') == 'main'
                if doc.get_attribute(div_id, 'id') == 'nested':
                    nested_found = True
            assert container_found
            assert nested_found

    def test_convert_body_with_text(self):                                      # Test <body> with text content
        html = """
        <html>
            <head></head>
            <body>
                <p>Hello World</p>
            </body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            ps = doc.get_elements_by_tag('p')
            assert len(ps) == 1

            p_id    = ps[0]
            content = doc.get_text_content(p_id)
            assert content == 'Hello World'

    def test_convert_body_with_script(self):                                    # Test <body> with inline script
        html = """
        <html>
            <head></head>
            <body>
                <script>console.log('test');</script>
            </body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            scripts = doc.scripts_graph.get_all_scripts()
            assert len(scripts) == 1

            script_id = scripts[0]
            content   = doc.get_script_content(script_id)
            assert 'console.log' in content

    def test_convert_body_attributes(self):                                     # Test <body> element attributes
        html = """
        <html>
            <head></head>
            <body class="container" data-page="home">
                <div>Content</div>
            </body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            body_id = doc.body_graph.root_id
            assert doc.get_tag(body_id) == 'body'

            attrs = doc.get_attributes(body_id)
            assert attrs.get('class')     == 'container'
            assert attrs.get('data-page') == 'home'

    def test_convert_body_with_multiple_same_tags(self):                        # Test multiple same tags get indexed paths
        html = """
        <html>
            <head></head>
            <body>
                <div>First</div>
                <div>Second</div>
                <div>Third</div>
            </body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            divs = doc.get_elements_by_tag('div')
            assert len(divs) == 3

    def test_convert_body_nested_structure(self):                               # Test deeply nested body structure
        html = """
        <html>
            <head></head>
            <body>
                <div class="level1">
                    <div class="level2">
                        <p class="level3">Deep content</p>
                    </div>
                </div>
            </body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            divs = doc.get_elements_by_tag('div')
            assert len(divs) == 2

            ps = doc.get_elements_by_tag('p')
            assert len(ps) == 1

            p_id    = ps[0]
            content = doc.get_text_content(p_id)
            assert content == 'Deep content'

    # ═══════════════════════════════════════════════════════════════════════════
    # Convert Tests - Scripts and Styles
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert_with_script(self):                                         # Test script content extraction
        html = """
        <html>
            <head></head>
            <body>
                <script>console.log('test');</script>
            </body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            scripts = doc.scripts_graph.get_all_scripts()
            assert len(scripts) == 1

            script_id = scripts[0]
            content   = doc.get_script_content(script_id)
            assert 'console.log' in content

    def test_convert_with_external_script(self):                                # Test external script (no content)
        html = """
        <html>
            <head></head>
            <body>
                <script src="app.js"></script>
            </body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            scripts = doc.scripts_graph.get_all_scripts()
            assert len(scripts) == 1

            script_id = scripts[0]
            assert doc.get_attribute(script_id, 'src') == 'app.js'
            assert doc.scripts_graph.is_external_script(script_id) is True

    def test_convert_with_style(self):                                          # Test style content extraction
        html = """
        <html>
            <head>
                <style>.container { display: flex; }</style>
            </head>
            <body></body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            styles = doc.styles_graph.get_all_styles()
            assert len(styles) == 1

            style_id = styles[0]
            content  = doc.get_style_content(style_id)
            assert 'display: flex' in content

    def test_convert_with_multiple_scripts(self):                               # Test multiple scripts
        html = """
        <html>
            <head>
                <script>var a = 1;</script>
            </head>
            <body>
                <script>var b = 2;</script>
                <script src="external.js"></script>
            </body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            scripts = doc.scripts_graph.get_all_scripts()
            assert len(scripts) == 3

            inline_scripts = doc.scripts_graph.get_inline_scripts()
            assert len(inline_scripts) == 2

            external_scripts = doc.scripts_graph.get_external_scripts()
            assert len(external_scripts) == 1

    def test_convert_with_multiple_styles(self):                                # Test multiple styles
        html = """
        <html>
            <head>
                <style>/* style 1 */</style>
                <link rel="stylesheet" href="main.css">
                <style>/* style 2 */</style>
            </head>
            <body></body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            styles = doc.styles_graph.get_all_styles()
            assert len(styles) == 3

            inline_styles = doc.styles_graph.get_inline_styles()
            assert len(inline_styles) == 2

            external_styles = doc.styles_graph.get_external_styles()
            assert len(external_styles) == 1

    # ═══════════════════════════════════════════════════════════════════════════
    # Convert From Dict Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert_from_dict(self):                                           # Test conversion from dict directly
        html_dict = {
            'tag'  : 'html',
            'attrs': {'lang': 'en'},
            'nodes': [
                {'tag': 'head', 'attrs': {}, 'nodes': []},
                {'tag': 'body', 'attrs': {'class': 'main'}, 'nodes': [
                    {'tag': 'div', 'attrs': {'id': 'content'}, 'nodes': [
                        {'type': 'TEXT', 'data': 'Hello'}
                    ]}
                ]}
            ]
        }
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert_from_dict(html_dict)

            assert doc.root_id is not None
            assert doc.get_attribute(doc.root_id, 'lang') == 'en'

            divs = doc.get_elements_by_tag('div')
            assert len(divs) == 1

    def test_convert_from_dict__empty_head_body(self):                          # Test dict with empty head/body
        html_dict = {
            'tag'  : 'html',
            'attrs': {},
            'nodes': [
                {'tag': 'head', 'attrs': {}, 'nodes': []},
                {'tag': 'body', 'attrs': {}, 'nodes': []}
            ]
        }
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert_from_dict(html_dict)

            assert doc.root_id is not None
            assert doc.head_graph.root_id is not None
            assert doc.body_graph.root_id is not None

    def test_convert_from_dict__no_head(self):                                  # Test dict without head section
        html_dict = {
            'tag'  : 'html',
            'attrs': {},
            'nodes': [
                {'tag': 'body', 'attrs': {}, 'nodes': []}
            ]
        }
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert_from_dict(html_dict)

            assert doc.root_id is not None

    def test_convert_from_dict__no_body(self):                                  # Test dict without body section
        html_dict = {
            'tag'  : 'html',
            'attrs': {},
            'nodes': [
                {'tag': 'head', 'attrs': {}, 'nodes': []}
            ]
        }
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert_from_dict(html_dict)

            assert doc.root_id is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # _extract_head_body Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__extract_head_body(self):                                          # Test head/body extraction
        html_dict = {
            'nodes': [
                {'tag': 'head', 'data': 'head_content'},
                {'tag': 'body', 'data': 'body_content'}
            ]
        }
        with Html__To__Html_MGraph__Document() as converter:
            head, body = converter._extract_head_body(html_dict)

            assert head is not None
            assert body is not None
            assert head.get('tag') == 'head'
            assert body.get('tag') == 'body'

    def test__extract_head_body__case_insensitive(self):                        # Test extraction is case insensitive
        html_dict = {
            'nodes': [
                {'tag': 'HEAD'},
                {'tag': 'BODY'}
            ]
        }
        with Html__To__Html_MGraph__Document() as converter:
            head, body = converter._extract_head_body(html_dict)

            assert head is not None
            assert body is not None

    def test__extract_head_body__empty_nodes(self):                             # Test extraction with empty nodes
        html_dict = {'nodes': []}

        with Html__To__Html_MGraph__Document() as converter:
            head, body = converter._extract_head_body(html_dict)

            assert head is None
            assert body is None

    def test__extract_head_body__no_nodes_key(self):                            # Test extraction without nodes key
        html_dict = {}

        with Html__To__Html_MGraph__Document() as converter:
            head, body = converter._extract_head_body(html_dict)

            assert head is None
            assert body is None

    def test__extract_head_body__non_dict_nodes(self):                          # Test extraction with non-dict nodes
        html_dict = {
            'nodes': [
                "text node",                                                    # Not a dict
                {'tag': 'body'}
            ]
        }
        with Html__To__Html_MGraph__Document() as converter:
            head, body = converter._extract_head_body(html_dict)

            assert head is None
            assert body is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Method Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__generate_node_id(self):                                           # Test node ID generation
        with Html__To__Html_MGraph__Document() as converter:
            id1 = converter._generate_node_id()
            id2 = converter._generate_node_id()

            assert id1 is not None
            assert id2 is not None
            assert id1 != id2                                                   # Each ID should be unique

    def test__is_text_node__type_text(self):                                    # Test text node detection with type=TEXT
        with Html__To__Html_MGraph__Document() as converter:
            node = {'type': 'TEXT', 'data': 'some text'}
            assert converter._is_text_node(node) is True

    def test__is_text_node__data_only(self):                                    # Test text node detection with data only
        with Html__To__Html_MGraph__Document() as converter:
            node = {'data': 'some text'}                                        # No tag, has data
            assert converter._is_text_node(node) is True

    def test__is_text_node__element(self):                                      # Test text node detection returns False for element
        with Html__To__Html_MGraph__Document() as converter:
            node = {'tag': 'div', 'data': 'some text'}                          # Has tag, so not text
            assert converter._is_text_node(node) is False

    def test__is_text_node__no_data(self):                                      # Test text node detection with no data
        with Html__To__Html_MGraph__Document() as converter:
            node = {'attrs': {}}                                                # No data, no tag
            assert converter._is_text_node(node) is False

    def test__extract_text_content(self):                                       # Test text content extraction
        with Html__To__Html_MGraph__Document() as converter:
            node = {
                'nodes': [
                    {'type': 'TEXT', 'data': 'Hello '},
                    {'type': 'TEXT', 'data': 'World'}
                ]
            }
            content = converter._extract_text_content(node)
            assert content == 'Hello World'

    def test__extract_text_content__empty(self):                                # Test text extraction with no text nodes
        with Html__To__Html_MGraph__Document() as converter:
            node = {'nodes': [{'tag': 'span'}]}
            content = converter._extract_text_content(node)
            assert content is None

    def test__extract_text_content__whitespace_only(self):                      # Test text extraction skips whitespace
        with Html__To__Html_MGraph__Document() as converter:
            node = {
                'nodes': [
                    {'type': 'TEXT', 'data': '   '},
                    {'type': 'TEXT', 'data': '\n\t'}
                ]
            }
            content = converter._extract_text_content(node)
            assert content is None

    def test__extract_text_content__mixed(self):                                # Test text extraction with mixed nodes
        with Html__To__Html_MGraph__Document() as converter:
            node = {
                'nodes': [
                    {'type': 'TEXT', 'data': 'Text1'},
                    {'tag': 'span'},                                            # Element node (ignored)
                    {'type': 'TEXT', 'data': 'Text2'}
                ]
            }
            content = converter._extract_text_content(node)
            assert content == 'Text1Text2'

    def test__count_tags(self):                                                 # Test tag counting
        with Html__To__Html_MGraph__Document() as converter:
            nodes = [
                {'tag': 'div'},
                {'tag': 'div'},
                {'tag': 'p'},
                {'tag': 'DIV'},                                                 # Case insensitive
                {'data': 'text'}                                                # Not a tag
            ]
            counts = converter._count_tags(nodes)

            assert counts.get('div') == 3
            assert counts.get('p')   == 1

    def test__count_tags__empty(self):                                          # Test tag counting with empty list
        with Html__To__Html_MGraph__Document() as converter:
            counts = converter._count_tags([])
            assert counts == {}

    def test__count_tags__no_tags(self):                                        # Test tag counting with no tag nodes
        with Html__To__Html_MGraph__Document() as converter:
            nodes = [
                {'data': 'text1'},
                {'data': 'text2'}
            ]
            counts = converter._count_tags(nodes)
            assert counts == {}

    # ═══════════════════════════════════════════════════════════════════════════
    # Shared Node IDs Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_shared_node_ids(self):                                             # Test that node IDs are shared across graphs
        html = """
        <html>
            <head></head>
            <body>
                <div class="main">Content</div>
            </body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            divs_in_attrs = doc.attrs_graph.get_elements_by_tag('div')          # Get div from attributes graph
            assert len(divs_in_attrs) == 1
            div_id = divs_in_attrs[0]

            tag = doc.get_tag(div_id)                                           # Cross-graph lookup
            assert tag == 'div'

            attrs = doc.get_attributes(div_id)
            assert attrs.get('class') == 'main'

    def test_shared_node_ids__script(self):                                     # Test script node ID shared between graphs
        html = """
        <html>
            <head></head>
            <body>
                <script type="module">export default {};</script>
            </body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            scripts = doc.scripts_graph.get_all_scripts()
            assert len(scripts) == 1
            script_id = scripts[0]

            tag = doc.get_tag(script_id)                                        # Tag from attrs_graph
            assert tag == 'script'

            attrs = doc.get_attributes(script_id)                               # Attrs from attrs_graph
            assert attrs.get('type') == 'module'

            content = doc.get_script_content(script_id)                         # Content from scripts_graph
            assert 'export default' in content

    def test_shared_node_ids__style(self):                                      # Test style node ID shared between graphs
        html = """
        <html>
            <head>
                <style type="text/css">body { margin: 0; }</style>
            </head>
            <body></body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            doc = converter.convert(html)

            styles = doc.styles_graph.get_all_styles()
            assert len(styles) == 1
            style_id = styles[0]

            tag = doc.get_tag(style_id)
            assert tag == 'style'

            attrs = doc.get_attributes(style_id)
            assert attrs.get('type') == 'text/css'

            content = doc.get_style_content(style_id)
            assert 'margin: 0' in content

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_full_html_document(self):                                          # Test complete HTML document
        html = """
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <title>Test Document</title>
                <link rel="stylesheet" href="styles.css">
                <style>.highlight { color: red; }</style>
                <script>window.APP_CONFIG = {};</script>
            </head>
            <body class="page" data-page="home">
                <header id="header">
                    <nav>Navigation</nav>
                </header>
                <main>
                    <article>
                        <h1>Title</h1>
                        <p>First paragraph</p>
                        <p>Second paragraph</p>
                    </article>
                </main>
                <footer>Footer content</footer>
                <script src="app.js"></script>
                <script>console.log('inline');</script>
            </body>
        </html>
        """
        with Html__To__Html_MGraph__Document() as converter:
            with mgraph_test_ids():
                doc = converter.convert(html)

            # Verify document structure
            assert doc.root_id is not None
            assert doc.get_tag(doc.root_id) == 'html'
            assert doc.get_attribute(doc.root_id, 'lang') == 'en'

            # Verify head elements
            titles = doc.get_elements_by_tag('title')
            assert len(titles) == 1
            assert doc.get_text_content(titles[0], in_head=True) == 'Test Document'

            metas = doc.get_elements_by_tag('meta')
            assert len(metas) >= 1

            # Verify body structure
            body_id = doc.body_graph.root_id
            assert doc.get_tag(body_id) == 'body'
            assert doc.get_attribute(body_id, 'class') == 'page'

            # Verify nested elements
            headers  = doc.get_elements_by_tag('header')
            articles = doc.get_elements_by_tag('article')
            ps       = doc.get_elements_by_tag('p')

            assert len(headers)  == 1
            assert len(articles) == 1
            assert len(ps)       == 2

            # Verify scripts
            scripts         = doc.scripts_graph.get_all_scripts()
            inline_scripts  = doc.scripts_graph.get_inline_scripts()
            external_scripts = doc.scripts_graph.get_external_scripts()

            assert len(scripts)          == 3                                   # 1 in head, 2 in body
            assert len(inline_scripts)   == 2
            assert len(external_scripts) == 1

            # Verify styles
            styles         = doc.styles_graph.get_all_styles()
            inline_styles  = doc.styles_graph.get_inline_styles()
            external_styles = doc.styles_graph.get_external_styles()

            assert len(styles)          == 2                                    # 1 link, 1 style
            assert len(inline_styles)   == 1
            assert len(external_styles) == 1

            # Verify stats work
            stats = doc.stats()
            assert type(stats) == Schema__Html_MGraph__Stats__Document
            assert stats.obj() == __(document=__(total_nodes=6,
                                                 total_edges=5,
                                                 root_id='c0000001'),
                                     head=__(element_nodes=6,
                                             text_nodes=1,
                                             total_nodes=8,
                                             total_edges=6,
                                             root_id='c0000017'),
                                     body=__(element_nodes=11,
                                             text_nodes=5,
                                             total_nodes=17,
                                             total_edges=15,
                                             root_id='c0000035'),
                                     attributes=__(registered_elements=18,
                                                   total_attributes=7,
                                                   unique_tags=15,
                                                   total_nodes=42,
                                                   total_edges=41,
                                                   root_id='c0000005'),
                                     scripts=__(total_scripts=3,
                                                inline_scripts=2,
                                                external_scripts=1,
                                                total_nodes=7,
                                                total_edges=5,
                                                root_id='c0000007'),
                                     styles=__(total_styles=2,
                                               inline_styles=1,
                                               external_styles=1,
                                               total_nodes=5,
                                               total_edges=3,
                                               root_id='c0000009'))
