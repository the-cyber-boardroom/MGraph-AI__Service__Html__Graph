import re
from unittest                                                                           import TestCase
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html   import Html_MGraph__Document__To__Html
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document             import Html_MGraph__Document
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document   import Html__To__Html_MGraph__Document
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.utils.Objects                                                          import base_classes


def normalize_html(html: str) -> str:                                           # Normalize HTML for comparison
    html = re.sub(r'\s+', ' ', html)                                            # Collapse whitespace
    html = re.sub(r'>\s+<', '><', html)                                         # Remove space between tags
    html = html.strip().lower()                                                 # Trim and lowercase
    return html


class test_Html_MGraph__Document__To__Html(TestCase):                           # Test Document to HTML round-trip conversion

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                     # Test default initialization
        with Html_MGraph__Document__To__Html() as _:
            assert type(_)         is Html_MGraph__Document__To__Html
            assert base_classes(_) == [Type_Safe, object]

    # ═══════════════════════════════════════════════════════════════════════════
    # Convert Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert__adds_doctype(self):                                       # Test DOCTYPE is added by Html_Dict__To__Html
        with Html_MGraph__Document().setup() as doc:
            doc.attrs_graph.register_element(doc.root_id, 'html')
            doc.attrs_graph.register_element(doc.head_graph.root_id, 'head')
            doc.attrs_graph.register_element(doc.body_graph.root_id, 'body')

            with Html_MGraph__Document__To__Html() as converter:
                html = converter.convert(doc)

                assert html == """<!DOCTYPE html>
<html>
    <head></head>
    <body></body>
</html>
"""

    # ═══════════════════════════════════════════════════════════════════════════
    # Round-Trip Tests - Basic
    # ═══════════════════════════════════════════════════════════════════════════

    def test_roundtrip__minimal(self):                                          # Test minimal HTML round-trip
        original = "<!doctype html><html><head></head><body></body></html>"

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert normalize_html(original) == normalize_html(result)
                assert result == """<!DOCTYPE html>
<html>
    <head></head>
    <body></body>
</html>
"""

    def test_roundtrip__with_lang(self):                                        # Test HTML with lang attribute
        original = '<html lang="en"><head></head><body></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html lang="en">
    <head></head>
    <body></body>
</html>
"""

    def test_roundtrip__with_multiple_attrs(self):                              # Test element with multiple attributes
        original = '<html lang="en" dir="ltr"><head></head><body class="main" id="app"></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html lang="en" dir="ltr">
    <head></head>
    <body class="main" id="app"></body>
</html>
"""

    # ═══════════════════════════════════════════════════════════════════════════
    # Round-Trip Tests - Head Content
    # ═══════════════════════════════════════════════════════════════════════════

    def test_roundtrip__head_with_meta(self):                                   # Test head with meta tags
        original = '<html><head><meta charset="utf-8"></head><body></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
    </head>
    <body></body>
</html>
"""

    def test_roundtrip__head_with_title(self):                                  # Test head with title
        original = '<html><head><title>My Page</title></head><body></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head>
        <title>My Page</title>
    </head>
    <body></body>
</html>
"""

    def test_roundtrip__head_with_link(self):                                   # Test head with link element
        original = '<html><head><link rel="stylesheet" href="style.css"></head><body></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" href="style.css" />
    </head>
    <body></body>
</html>
"""

    # ═══════════════════════════════════════════════════════════════════════════
    # Round-Trip Tests - Body Content
    # ═══════════════════════════════════════════════════════════════════════════

    def test_roundtrip__body_with_div(self):                                    # Test body with div element
        original = '<html><head></head><body><div class="container"></div></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head></head>
    <body>
        <div class="container"></div>
    </body>
</html>
"""

    def test_roundtrip__body_with_text(self):                                   # Test body with text content
        original = '<html><head></head><body><p>Hello World</p></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head></head>
    <body>
        <p>Hello World</p>
    </body>
</html>
"""

    def test_roundtrip__body_nested(self):                                      # Test body with nested elements
        original = '<html><head></head><body><div><span><p>Deep</p></span></div></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head></head>
    <body>
        <div>
            <span>
                <p>Deep</p>
            </span>
        </div>
    </body>
</html>
"""

    def test_roundtrip__body_siblings(self):                                    # Test body with sibling elements
        original = '<html><head></head><body><header></header><main></main><footer></footer></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head></head>
    <body>
        <header></header>
        <main></main>
        <footer></footer>
    </body>
</html>
"""

    # ═══════════════════════════════════════════════════════════════════════════
    # Round-Trip Tests - Scripts
    # ═══════════════════════════════════════════════════════════════════════════

    def test_roundtrip__inline_script(self):                                    # Test inline script
        original = "<html><head></head><body><script>console.log('test');</script></body></html>"

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head></head>
    <body>
        <script>console.log('test');</script>
    </body>
</html>
"""

    def test_roundtrip__external_script(self):                                  # Test external script
        original = '<html><head></head><body><script src="app.js"></script></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head></head>
    <body>
        <script src="app.js"></script>
    </body>
</html>
"""

    def test_roundtrip__script_in_head(self):                                   # Test script in head
        original = "<html><head><script>var x = 1;</script></head><body></body></html>"

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head>
        <script>var x = 1;</script>
    </head>
    <body></body>
</html>
"""

    def test_roundtrip__multiple_scripts(self):                                 # Test multiple scripts
        original = "<html><head><script>var a=1;</script></head><body><script>var b=2;</script></body></html>"

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head>
        <script>var a=1;</script>
    </head>
    <body>
        <script>var b=2;</script>
    </body>
</html>
"""

    # ═══════════════════════════════════════════════════════════════════════════
    # Round-Trip Tests - Styles
    # ═══════════════════════════════════════════════════════════════════════════

    def test_roundtrip__inline_style(self):                                     # Test inline style
        original = '<html><head><style>body { margin: 0; }</style></head><body></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head>
        <style>body { margin: 0; }</style>
    </head>
    <body></body>
</html>
"""

    def test_roundtrip__external_stylesheet(self):                              # Test external stylesheet link
        original = '<html><head><link rel="stylesheet" href="styles.css"></head><body></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" href="styles.css" />
    </head>
    <body></body>
</html>
"""

    def test_roundtrip__multiple_styles(self):                                  # Test multiple styles
        original = '<html><head><style>.a{}</style><style>.b{}</style></head><body></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head>
        <style>.a{}</style>
        <style>.b{}</style>
    </head>
    <body></body>
</html>
"""

    # ═══════════════════════════════════════════════════════════════════════════
    # Round-Trip Tests - Complex Documents
    # ═══════════════════════════════════════════════════════════════════════════

    def test_roundtrip__blog_page(self):                                        # Test blog-style page
        original = """<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <title>Blog Post</title>
        <style>.post { max-width: 800px; }</style>
    </head>
    <body>
        <article class="post">
            <h1>Title</h1>
            <p>First paragraph</p>
            <p>Second paragraph</p>
        </article>
    </body>
</html>
"""

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <title>Blog Post</title>
        <style>.post { max-width: 800px; }</style>
    </head>
    <body>
        <article class="post">
            <h1>Title</h1>
            <p>First paragraph</p>
            <p>Second paragraph</p>
        </article>
    </body>
</html>
"""
            assert result == original

    def test_roundtrip__dashboard(self):                                        # Test dashboard-style page
        original = '''<!DOCTYPE html>
<html>
    <head>
        <title>Dashboard</title>
        <script>window.CONFIG = {};</script>
    </head>
    <body class="dashboard">
        <header id="top-nav">
            <nav>Menu</nav>
        </header>
        <main>
            <aside class="sidebar">Sidebar</aside>
            <section class="content">Content</section>
        </main>
        <script src="app.js"></script>
    </body>
</html>
'''

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head>
        <title>Dashboard</title>
        <script>window.CONFIG = {};</script>
    </head>
    <body class="dashboard">
        <header id="top-nav">
            <nav>Menu</nav>
        </header>
        <main>
            <aside class="sidebar">Sidebar</aside>
            <section class="content">Content</section>
        </main>
        <script src="app.js"></script>
    </body>
</html>
"""
                assert result == original

    def test_roundtrip__landing_page(self):                                     # Test landing page
        original = '''<!DOCTYPE html>
<html lang="en" dir="ltr">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width" />
        <title>Welcome</title>
        <link rel="stylesheet" href="main.css" />
        <style>.hero { height: 100vh; }</style>
    </head>
    <body>
        <div class="hero">
            <h1>Welcome</h1>
            <p>Get started today</p>
            <button id="cta">Sign Up</button>
        </div>
        <script src="analytics.js"></script>
        <script>track('pageview');</script>
    </body>
</html>
'''

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html lang="en" dir="ltr">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width" />
        <title>Welcome</title>
        <link rel="stylesheet" href="main.css" />
        <style>.hero { height: 100vh; }</style>
    </head>
    <body>
        <div class="hero">
            <h1>Welcome</h1>
            <p>Get started today</p>
            <button id="cta">Sign Up</button>
        </div>
        <script src="analytics.js"></script>
        <script>track('pageview');</script>
    </body>
</html>
"""
                assert result == original

    def test_roundtrip__ecommerce_product(self):                                # Test e-commerce product page
        original = '''<!DOCTYPE html>
<html>
    <head>
        <title>Product - Widget Pro</title>
    </head>
    <body>
        <main>
            <div class="product" data-id="12345">
                <img src="widget.jpg" alt="Widget Pro" />
                <h1>Widget Pro</h1>
                <p class="price">$99.99</p>
                <button class="buy-btn">Add to Cart</button>
            </div>
        </main>
    </body>
</html>
'''

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head>
        <title>Product - Widget Pro</title>
    </head>
    <body>
        <main>
            <div class="product" data-id="12345">
                <img src="widget.jpg" alt="Widget Pro" />
                <h1>Widget Pro</h1>
                <p class="price">$99.99</p>
                <button class="buy-btn">Add to Cart</button>
            </div>
        </main>
    </body>
</html>
"""
                assert result == original

    # ═══════════════════════════════════════════════════════════════════════════
    # Edge Case Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_roundtrip__empty_elements(self):                                   # Test empty elements like br, hr
        original = '<html><head></head><body><p>Line 1<br>Line 2</p><hr></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head></head>
    <body>
        <p>Line 1<br />Line 2</p>
        <hr />
    </body>
</html>
"""

    def test_roundtrip__special_characters(self):                               # Test HTML with special content
        original = '<html><head></head><body><p>Price: $50</p></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head></head>
    <body>
        <p>Price: $50</p>
    </body>
</html>
"""

    def test_roundtrip__form_elements(self):                                    # Test form elements
        original = '<html><head></head><body><form action="/submit"><input type="text" name="user"><input type="submit" value="Go"></form></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head></head>
    <body>
        <form action="/submit">
            <input type="text" name="user" />
            <input type="submit" value="Go" />
        </form>
    </body>
</html>
"""

    def test_roundtrip__table(self):                                            # Test table structure
        original = '<html><head></head><body><table><thead><tr><th>Name</th></tr></thead><tbody><tr><td>Alice</td></tr></tbody></table></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head></head>
    <body>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Alice</td>
                </tr>
            </tbody>
        </table>
    </body>
</html>
"""

    def test_roundtrip__lists(self):                                            # Test list structures
        original = '<html><head></head><body><ul><li>One</li><li>Two</li></ul><ol><li>First</li><li>Second</li></ol></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head></head>
    <body>
        <ul>
            <li>One</li>
            <li>Two</li>
        </ul>
        <ol>
            <li>First</li>
            <li>Second</li>
        </ol>
    </body>
</html>
"""

    def test_roundtrip__semantic_html5(self):                                   # Test HTML5 semantic elements
        original = '<html><head></head><body><article><header><h1>Post</h1></header><section><p>Content</p></section><footer><small>Copyright</small></footer></article></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head></head>
    <body>
        <article>
            <header>
                <h1>Post</h1>
            </header>
            <section>
                <p>Content</p>
            </section>
            <footer>
                <small>Copyright</small>
            </footer>
        </article>
    </body>
</html>
"""

    def test_roundtrip__multiple_classes(self):                                 # Test multiple CSS classes
        original = '<html><head></head><body><div class="container fluid dark-mode"></div></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head></head>
    <body>
        <div class="container fluid dark-mode"></div>
    </body>
</html>
"""

    def test_roundtrip__data_attributes(self):                                  # Test data-* attributes
        original = '<html><head></head><body><div data-id="123" data-type="widget" data-config=\'{"a":1}\'></div></body></html>'

        with Html__To__Html_MGraph__Document() as to_doc:
            doc = to_doc.convert(original)

            with Html_MGraph__Document__To__Html() as to_html:
                result = to_html.convert(doc)

                assert result == """<!DOCTYPE html>
<html>
    <head></head>
    <body>
        <div data-id="123" data-type="widget" data-config='{"a":1}'></div>
    </body>
</html>
"""