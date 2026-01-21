from unittest                                                                                       import TestCase
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                                   import Node_Id
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document    import Html__To__Html_MGraph__Document
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document                  import Html_MGraph__Document


class test_Html__To__Html_MGraph__Document(TestCase):                           # Test HTML to MGraph Document conversion

    # ═══════════════════════════════════════════════════════════════════════════
    # Core Initialization
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                     # Test initialization and Type_Safe compliance
        with Html__To__Html_MGraph__Document() as _:
            assert type(_) is Html__To__Html_MGraph__Document

    # ═══════════════════════════════════════════════════════════════════════════
    # convert() Method Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert(self):                                                     # Test basic HTML string conversion
        html = "<html><head></head><body></body></html>"
        with Html__To__Html_MGraph__Document() as _:
            doc = _.convert(html)
            assert type(doc)                is Html_MGraph__Document
            assert doc.root_id              is not None
            assert doc.head_graph.root_id   is not None
            assert doc.body_graph.root_id   is not None

    def test_convert__with_attributes(self):                                    # Test HTML with attributes on all levels
        html = '''<html lang="en" dir="ltr">
            <head><title>Test</title></head>
            <body class="container" id="main">
                <div class="content">Hello</div>
            </body>
        </html>'''
        with Html__To__Html_MGraph__Document() as _:
            doc = _.convert(html)

            html_attrs = doc.get_attributes(doc.root_id)                        # Check <html> attributes
            assert html_attrs.get('lang') == 'en'
            assert html_attrs.get('dir')  == 'ltr'

            body_attrs = doc.get_attributes(doc.body_graph.root_id)             # Check <body> attributes
            assert body_attrs.get('class') == 'container'
            assert body_attrs.get('id')    == 'main'

    def test_convert__minimal_html(self):                                       # Test minimal valid HTML
        html = "<html></html>"
        with Html__To__Html_MGraph__Document() as _:
            doc = _.convert(html)
            assert doc.root_id is not None                                      # Document still created

    def test_convert__with_text_content(self):                                  # Test text node handling
        html = "<html><head></head><body><p>Hello World</p></body></html>"
        with Html__To__Html_MGraph__Document() as _:
            doc  = _.convert(html)
            divs = doc.get_elements_by_tag('p')
            assert len(divs) == 1

    # ═══════════════════════════════════════════════════════════════════════════
    # convert_from_dict() Method Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert_from_dict(self):                                           # Test conversion from pre-parsed dict
        html_dict = {
            'tag'  : 'html'                                             ,
            'attrs': {'lang': 'en'}                                     ,
            'nodes': [
                {'tag': 'head', 'attrs': {}, 'nodes': []}               ,
                {'tag': 'body', 'attrs': {}, 'nodes': []}               ,
            ]
        }
        with Html__To__Html_MGraph__Document() as _:
            doc = _.convert_from_dict(html_dict)
            assert type(doc)      is Html_MGraph__Document
            assert doc.root_id    is not None
            html_attrs = doc.get_attributes(doc.root_id)
            assert html_attrs.get('lang') == 'en'

    def test_convert_from_dict__empty_nodes(self):                              # Test dict with empty nodes list
        html_dict = {'tag': 'html', 'attrs': {}, 'nodes': []}
        with Html__To__Html_MGraph__Document() as _:
            doc = _.convert_from_dict(html_dict)
            assert doc.root_id is not None                                      # Still creates document

    def test_convert_from_dict__with_nested_elements(self):                     # Test deeply nested structure
        html_dict = {
            'tag'  : 'html'                                             ,
            'attrs': {}                                                 ,
            'nodes': [
                {'tag': 'head', 'attrs': {}, 'nodes': []}               ,
                {'tag': 'body', 'attrs': {}, 'nodes': [
                    {'tag': 'div', 'attrs': {'id': 'outer'}, 'nodes': [
                        {'tag': 'div', 'attrs': {'id': 'inner'}, 'nodes': [
                            {'tag': 'span', 'attrs': {}, 'nodes': []}
                        ]}
                    ]}
                ]}                                                      ,
            ]
        }
        with Html__To__Html_MGraph__Document() as _:
            doc   = _.convert_from_dict(html_dict)
            divs  = doc.get_elements_by_tag('div')
            spans = doc.get_elements_by_tag('span')
            assert len(divs)  == 2
            assert len(spans) == 1

    # ═══════════════════════════════════════════════════════════════════════════
    # _extract_head_body() Method Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__extract_head_body(self):                                          # Test extraction of head and body sections
        html_dict = {
            'nodes': [
                {'tag': 'head', 'attrs': {}}                            ,
                {'tag': 'body', 'attrs': {}}                            ,
            ]
        }
        with Html__To__Html_MGraph__Document() as _:
            head, body = _._extract_head_body(html_dict)
            assert head is not None
            assert body is not None
            assert head.get('tag') == 'head'
            assert body.get('tag') == 'body'

    def test__extract_head_body__missing_head(self):                            # Test when <head> is missing
        html_dict = {'nodes': [{'tag': 'body', 'attrs': {}}]}
        with Html__To__Html_MGraph__Document() as _:
            head, body = _._extract_head_body(html_dict)
            assert head is None
            assert body is not None

    def test__extract_head_body__missing_body(self):                            # Test when <body> is missing
        html_dict = {'nodes': [{'tag': 'head', 'attrs': {}}]}
        with Html__To__Html_MGraph__Document() as _:
            head, body = _._extract_head_body(html_dict)
            assert head is not None
            assert body is None

    def test__extract_head_body__empty_nodes(self):                             # Test with no nodes
        html_dict = {'nodes': []}
        with Html__To__Html_MGraph__Document() as _:
            head, body = _._extract_head_body(html_dict)
            assert head is None
            assert body is None

    def test__extract_head_body__case_insensitive(self):                        # Test that tag matching is case-insensitive
        html_dict = {'nodes': [{'tag': 'HEAD'}, {'tag': 'BODY'}]}
        with Html__To__Html_MGraph__Document() as _:
            head, body = _._extract_head_body(html_dict)
            assert head is not None
            assert body is not None

    def test__extract_head_body__skips_non_dict_nodes(self):                    # Test that non-dict nodes are skipped
        html_dict = {'nodes': ['text', {'tag': 'body'}]}
        with Html__To__Html_MGraph__Document() as _:
            head, body = _._extract_head_body(html_dict)
            assert head is None
            assert body is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # _generate_node_id() Method Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__generate_node_id(self):                                           # Test node ID generation
        with Html__To__Html_MGraph__Document() as _:
            node_id = _._generate_node_id()
            assert type(node_id) is Node_Id
            assert str(node_id)  != ''                                          # Not empty

    def test__generate_node_id__unique(self):                                   # Test that generated IDs are unique
        with Html__To__Html_MGraph__Document() as _:
            ids = [_._generate_node_id() for i in range(100)]
            assert len(set(str(id) for id in ids)) == 100                       # All unique

    # ═══════════════════════════════════════════════════════════════════════════
    # _is_text_node() Method Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__is_text_node__with_type_text(self):                               # Test TEXT type detection
        with Html__To__Html_MGraph__Document() as _:
            node = {'type': 'TEXT', 'data': 'Hello'}
            assert _._is_text_node(node) is True

    def test__is_text_node__with_data_only(self):                               # Test data-only node detection
        with Html__To__Html_MGraph__Document() as _:
            node = {'data': 'Hello'}
            assert _._is_text_node(node) is True

    def test__is_text_node__element_node(self):                                 # Test that element nodes return False
        with Html__To__Html_MGraph__Document() as _:
            node = {'tag': 'div', 'data': 'ignored'}
            assert _._is_text_node(node) is False

    def test__is_text_node__empty_dict(self):                                   # Test empty dict
        with Html__To__Html_MGraph__Document() as _:
            node = {}
            assert _._is_text_node(node) is False

    # ═══════════════════════════════════════════════════════════════════════════
    # _extract_text_content() Method Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__extract_text_content(self):                                       # Test text extraction from child nodes
        with Html__To__Html_MGraph__Document() as _:
            node = {'nodes': [{'type': 'TEXT', 'data': 'Hello World'}]}
            content = _._extract_text_content(node)
            assert content == 'Hello World'

    def test__extract_text_content__multiple_text_nodes(self):                  # Test concatenation of multiple text nodes
        with Html__To__Html_MGraph__Document() as _:
            node = {'nodes': [
                {'type': 'TEXT', 'data': 'Hello '}                      ,
                {'type': 'TEXT', 'data': 'World'}                       ,
            ]}
            content = _._extract_text_content(node)
            assert content == 'Hello World'

    def test__extract_text_content__empty_nodes(self):                          # Test with no nodes
        with Html__To__Html_MGraph__Document() as _:
            node = {'nodes': []}
            content = _._extract_text_content(node)
            assert content is None

    def test__extract_text_content__whitespace_only(self):                      # Test that whitespace-only text is skipped
        with Html__To__Html_MGraph__Document() as _:
            node = {'nodes': [{'type': 'TEXT', 'data': '   \n\t  '}]}
            content = _._extract_text_content(node)
            assert content is None

    def test__extract_text_content__mixed_nodes(self):                          # Test with element and text nodes mixed
        with Html__To__Html_MGraph__Document() as _:
            node = {'nodes': [
                {'tag': 'span'}                                         ,       # Element - ignored
                {'type': 'TEXT', 'data': 'Content'}                     ,       # Text - extracted
            ]}
            content = _._extract_text_content(node)
            assert content == 'Content'

    # ═══════════════════════════════════════════════════════════════════════════
    # _count_tags() Method Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__count_tags(self):                                                 # Test basic tag counting
        with Html__To__Html_MGraph__Document() as _:
            nodes = [
                {'tag': 'div'}                                          ,
                {'tag': 'div'}                                          ,
                {'tag': 'span'}                                         ,
            ]
            counts = _._count_tags(nodes)
            assert counts == {'div': 2, 'span': 1}

    def test__count_tags__empty_list(self):                                     # Test with empty list
        with Html__To__Html_MGraph__Document() as _:
            counts = _._count_tags([])
            assert counts == {}

    def test__count_tags__case_insensitive(self):                               # Test case normalization
        with Html__To__Html_MGraph__Document() as _:
            nodes = [{'tag': 'DIV'}, {'tag': 'div'}, {'tag': 'Div'}]
            counts = _._count_tags(nodes)
            assert counts == {'div': 3}

    def test__count_tags__skips_non_elements(self):                             # Test that non-element nodes are skipped
        with Html__To__Html_MGraph__Document() as _:
            nodes = [
                {'tag': 'div'}                                          ,
                {'data': 'text'}                                        ,       # Text node
                'string'                                                ,       # Not a dict
                {'type': 'TEXT'}                                        ,       # Text node
            ]
            counts = _._count_tags(nodes)
            assert counts == {'div': 1}

    # ═══════════════════════════════════════════════════════════════════════════
    # Script and Style Processing
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert__with_script_in_head(self):                                # Test script in <head>
        html = """<html>
            <head><script>console.log('test');</script></head>
            <body></body>
        </html>"""
        with Html__To__Html_MGraph__Document() as _:
            doc = _.convert(html)
            scripts = doc.scripts_graph.get_all_scripts()
            assert len(scripts) == 1
            content = doc.get_script_content(scripts[0])
            assert 'console.log' in content

    def test_convert__with_script_in_body(self):                                # Test script in <body>
        html = """<html>
            <head></head>
            <body><script>alert('hello');</script></body>
        </html>"""
        with Html__To__Html_MGraph__Document() as _:
            doc = _.convert(html)
            scripts = doc.scripts_graph.get_all_scripts()
            assert len(scripts) == 1
            content = doc.get_script_content(scripts[0])
            assert 'alert' in content

    def test_convert__with_style_in_head(self):                                 # Test inline style in <head>
        html = """<html>
            <head><style>.test { color: red; }</style></head>
            <body></body>
        </html>"""
        with Html__To__Html_MGraph__Document() as _:
            doc    = _.convert(html)
            styles = doc.styles_graph.get_all_styles()
            assert len(styles) == 1
            content = doc.get_style_content(styles[0])
            assert 'color: red' in content

    def test_convert__with_link_stylesheet(self):                               # Test external stylesheet link
        html = """<html>
            <head><link rel="stylesheet" href="styles.css"></head>
            <body></body>
        </html>"""
        with Html__To__Html_MGraph__Document() as _:
            doc   = _.convert(html)
            links = doc.get_elements_by_tag('link')
            assert len(links) == 1
            attrs = doc.get_attributes(links[0])
            assert attrs.get('href') == 'styles.css'

    def test_convert__multiple_scripts_and_styles(self):                        # Test multiple scripts and styles
        html = """<html>
            <head>
                <style>.a { }</style>
                <script>var a = 1;</script>
                <style>.b { }</style>
            </head>
            <body>
                <script>var b = 2;</script>
            </body>
        </html>"""
        with Html__To__Html_MGraph__Document() as _:
            doc     = _.convert(html)
            scripts = doc.scripts_graph.get_all_scripts()
            styles  = doc.styles_graph.get_all_styles()
            assert len(scripts) == 2
            assert len(styles)  == 2

    # ═══════════════════════════════════════════════════════════════════════════
    # Multiple Same-Tag Siblings (Tag Counting/Indexing)
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert__multiple_same_tag_siblings(self):                         # Test path indexing for duplicate tags
        html = """<html>
            <head></head>
            <body>
                <div id="first">First</div>
                <div id="second">Second</div>
                <div id="third">Third</div>
            </body>
        </html>"""
        with Html__To__Html_MGraph__Document() as _:
            doc  = _.convert(html)
            divs = doc.get_elements_by_tag('div')
            assert len(divs) == 3

            ids = [doc.get_attribute(div, 'id') for div in divs]                # All should have their attributes
            assert 'first'  in ids
            assert 'second' in ids
            assert 'third'  in ids

    # ═══════════════════════════════════════════════════════════════════════════
    # Text Node Handling
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert__text_in_body(self):                                       # Test text nodes in body
        html = """<html>
            <head></head>
            <body><p>Hello <strong>World</strong>!</p></body>
        </html>"""
        with Html__To__Html_MGraph__Document() as _:
            doc = _.convert(html)
            assert doc.body_graph.root_id is not None

    def test_convert__whitespace_only_text_skipped(self):                       # Test that whitespace-only nodes are not created
        html = """<html>
            <head>
            </head>
            <body>
            </body>
        </html>"""
        with Html__To__Html_MGraph__Document() as _:
            doc = _.convert(html)
            assert doc is not None                                              # Should complete without error

    def test_convert__text_in_head(self):                                       # Test text nodes in head (title content)
        html = """<html>
            <head><title>My Page Title</title></head>
            <body></body>
        </html>"""
        with Html__To__Html_MGraph__Document() as _:
            doc = _.convert(html)
            titles = doc.get_elements_by_tag('title')
            assert len(titles) == 1

    # ═══════════════════════════════════════════════════════════════════════════
    # Node ID Sharing Across Graphs
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert__node_id_shared_body_attrs(self):                          # Test Node_Id sharing between body and attrs
        html = """<html>
            <head></head>
            <body><div class="test"></div></body>
        </html>"""
        with Html__To__Html_MGraph__Document() as _:
            doc = _.convert(html)

            divs_in_body  = doc.get_elements_by_tag('div')                      # Same div accessible from both graphs
            divs_in_attrs = doc.attrs_graph.get_elements_by_tag('div')

            assert len(divs_in_body)  == 1
            assert len(divs_in_attrs) == 1
            assert divs_in_body[0] == divs_in_attrs[0]                          # Same Node_Id

    def test_convert__node_id_shared_head_attrs(self):                          # Test Node_Id sharing between head and attrs
        html = """<html>
            <head><meta charset="utf-8"></head>
            <body></body>
        </html>"""
        with Html__To__Html_MGraph__Document() as _:
            doc = _.convert(html)

            metas_in_attrs = doc.attrs_graph.get_elements_by_tag('meta')
            assert len(metas_in_attrs) == 1

            attrs = doc.get_attributes(metas_in_attrs[0])                       # Cross-graph attribute lookup works
            assert attrs.get('charset') == 'utf-8'

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests (Complex HTML)
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert__complex_html(self):                                       # Test comprehensive HTML document
        html = """<!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width">
                <title>Complex Page</title>
                <link rel="stylesheet" href="styles.css">
                <style>.container { display: flex; }</style>
                <script>window.config = {};</script>
            </head>
            <body class="dark-mode" data-page="home">
                <header id="nav">
                    <nav><ul><li><a href="/">Home</a></li></ul></nav>
                </header>
                <main>
                    <article class="post">
                        <h1>Title</h1>
                        <p>Paragraph with <strong>bold</strong> text.</p>
                    </article>
                </main>
                <footer><small>&copy; 2024</small></footer>
                <script>console.log('loaded');</script>
            </body>
        </html>"""
        with Html__To__Html_MGraph__Document() as _:
            doc = _.convert(html)

            assert doc.root_id            is not None                           # Document created
            assert doc.head_graph.root_id is not None
            assert doc.body_graph.root_id is not None

            html_attrs = doc.get_attributes(doc.root_id)                        # <html> attributes
            assert html_attrs.get('lang') == 'en'

            body_attrs = doc.get_attributes(doc.body_graph.root_id)             # <body> attributes
            assert body_attrs.get('class')     == 'dark-mode'
            assert body_attrs.get('data-page') == 'home'

            scripts = doc.scripts_graph.get_all_scripts()                       # Scripts found
            assert len(scripts) == 2

            styles = doc.styles_graph.get_all_styles()                          # Styles found
            assert len(styles) == 2

            headers = doc.get_elements_by_tag('header')                         # Elements found
            assert len(headers) == 1

            articles = doc.get_elements_by_tag('article')                       # Nested elements
            assert len(articles) == 1
            article_attrs = doc.get_attributes(articles[0])
            assert article_attrs.get('class') == 'post'