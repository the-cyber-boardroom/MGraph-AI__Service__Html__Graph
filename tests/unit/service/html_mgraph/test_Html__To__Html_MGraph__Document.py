from unittest                                                                           import TestCase
from mgraph_ai_service_html_graph.service.html_mgraph.Html__To__Html_MGraph__Document   import Html__To__Html_MGraph__Document


class test_Html__To__Html_MGraph__Document(TestCase):                           # Test HTML conversion

    def test__init__(self):                                                     # Test initialization
        with Html__To__Html_MGraph__Document() as _:
            assert type(_) is Html__To__Html_MGraph__Document

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

            body_root = doc.body_graph.root_id                                  # Check body structure
            assert doc.get_tag(body_root) == 'body'

            body_attrs = doc.get_attributes(body_root)                          # Check body attributes
            assert body_attrs.get('class') == 'container'

            all_divs = doc.get_elements_by_tag('div')                           # Check div element
            assert len(all_divs) == 1
            div_id = all_divs[0]
            assert doc.get_attribute(div_id, 'id') == 'main'

    def test_convert_with_script(self):                                         # Test HTML with script
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

    def test_convert_with_style(self):                                          # Test HTML with style
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