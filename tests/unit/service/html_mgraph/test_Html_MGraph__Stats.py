from unittest                                                                               import TestCase
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                           import Html_MGraph
from mgraph_ai_service_html_graph.schemas.html.Schema__Html_MGraph           import (
    Schema__Html_MGraph__Stats__Base      ,
    Schema__Html_MGraph__Stats__Head      ,
    Schema__Html_MGraph__Stats__Body      ,
    Schema__Html_MGraph__Stats__Attributes,
    Schema__Html_MGraph__Stats__Scripts   ,
    Schema__Html_MGraph__Stats__Styles    ,
    Schema__Html_MGraph__Stats__Document  ,
)
from mgraph_db.utils.testing.mgraph_test_ids import mgraph_test_ids
from osbot_utils.testing.__ import __


class test_Html_MGraph__Stats(TestCase):                                        # Test stats methods return Schema objects

    # ═══════════════════════════════════════════════════════════════════════════
    # Setup
    # ═══════════════════════════════════════════════════════════════════════════

    @classmethod
    def setUpClass(cls):
        cls.html = '''<html lang="en">
            <head>
                <meta charset="utf-8">
                <title>Test Page</title>
                <style>.main { color: red; }</style>
                <link rel="stylesheet" href="styles.css">
            </head>
            <body class="page" id="app">
                <header>Header</header>
                <main>
                    <article>
                        <h1>Title</h1>
                        <p>First paragraph</p>
                        <p>Second paragraph</p>
                    </article>
                </main>
                <script>console.log('inline');</script>
                <script src="app.js"></script>
            </body>
        </html>'''
        with mgraph_test_ids():
            cls.mgraph = Html_MGraph.from_html(cls.html)

    # ═══════════════════════════════════════════════════════════════════════════
    # Head Stats Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_head_stats__returns_schema(self):                                  # Test head stats returns Schema type
        stats = self.mgraph.head_graph.stats()
        assert type(stats) is Schema__Html_MGraph__Stats__Head

    def test_head_stats__has_base_fields(self):                                 # Test base fields present
        stats = self.mgraph.head_graph.stats()
        assert stats.total_nodes >= 0
        assert stats.total_edges >= 0
        assert stats.root_id     is not None

    def test_head_stats__has_head_fields(self):                                 # Test head-specific fields
        stats = self.mgraph.head_graph.stats()
        assert stats.element_nodes >= 0
        assert stats.text_nodes    >= 0

    def test_head_stats__counts_elements(self):                                 # Test element counting
        stats = self.mgraph.head_graph.stats()
        assert stats.element_nodes >= 4                                         # head, meta, title, style, link

    def test_head_stats__json_export(self):                                     # Test JSON export works
        stats      = self.mgraph.head_graph.stats()
        stats_dict = stats.json()

        assert type(stats_dict)            is dict
        assert 'total_nodes'               in stats_dict
        assert 'element_nodes'             in stats_dict
        assert 'text_nodes'                in stats_dict

    # ═══════════════════════════════════════════════════════════════════════════
    # Body Stats Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_body_stats__returns_schema(self):                                  # Test body stats returns Schema type
        stats = self.mgraph.body_graph.stats()
        assert type(stats) is Schema__Html_MGraph__Stats__Body

    def test_body_stats__has_body_fields(self):                                 # Test body-specific fields
        stats = self.mgraph.body_graph.stats()
        assert stats.element_nodes >= 0
        assert stats.text_nodes    >= 0

    def test_body_stats__counts_elements(self):                                 # Test element counting
        stats = self.mgraph.body_graph.stats()
        assert stats.element_nodes >= 7                                         # body, header, main, article, h1, p, p, script, script

    # ═══════════════════════════════════════════════════════════════════════════
    # Attributes Stats Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_attrs_stats__returns_schema(self):                                 # Test attrs stats returns Schema type
        stats = self.mgraph.attrs_graph.stats()
        assert type(stats) is Schema__Html_MGraph__Stats__Attributes

    def test_attrs_stats__has_attrs_fields(self):                               # Test attrs-specific fields
        stats = self.mgraph.attrs_graph.stats()
        assert stats.registered_elements >= 0
        assert stats.total_attributes    >= 0
        assert stats.unique_tags         >= 0

    def test_attrs_stats__counts_attributes(self):                              # Test attribute counting
        stats = self.mgraph.attrs_graph.stats()
        assert stats.total_attributes >= 4                                      # lang, charset, class, id, rel, href, src

    def test_attrs_stats__counts_unique_tags(self):                             # Test unique tag counting
        stats = self.mgraph.attrs_graph.stats()
        assert stats.unique_tags >= 5                                           # html, head, meta, title, style, link, body, header, main, article, h1, p, script

    # ═══════════════════════════════════════════════════════════════════════════
    # Scripts Stats Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_scripts_stats__returns_schema(self):                               # Test scripts stats returns Schema type
        stats = self.mgraph.scripts_graph.stats()
        assert type(stats) is Schema__Html_MGraph__Stats__Scripts

    def test_scripts_stats__has_scripts_fields(self):                           # Test scripts-specific fields
        stats = self.mgraph.scripts_graph.stats()
        assert stats.total_scripts    >= 0
        assert stats.inline_scripts   >= 0
        assert stats.external_scripts >= 0

    def test_scripts_stats__counts_scripts(self):                               # Test script counting
        stats = self.mgraph.scripts_graph.stats()
        assert type(stats) is Schema__Html_MGraph__Stats__Scripts
        assert stats.obj()            == __(total_scripts=2,
                                            inline_scripts=1,
                                            external_scripts=1,
                                            total_nodes=5,
                                            total_edges=3,
                                            root_id='c0000007')
        assert stats.total_scripts    >= 2
        assert stats.inline_scripts   >= 1                                      # console.log('inline');
        assert stats.external_scripts == 1                                      # src="app.js"

    # ═══════════════════════════════════════════════════════════════════════════
    # Styles Stats Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_styles_stats__returns_schema(self):                                # Test styles stats returns Schema type
        stats = self.mgraph.styles_graph.stats()
        assert type(stats) is Schema__Html_MGraph__Stats__Styles

    def test_styles_stats__has_styles_fields(self):                             # Test styles-specific fields
        stats = self.mgraph.styles_graph.stats()
        assert stats.total_styles    >= 0
        assert stats.inline_styles   >= 0
        assert stats.external_styles >= 0

    def test_styles_stats__counts_styles(self):                                 # Test style counting
        stats = self.mgraph.styles_graph.stats()
        assert stats.total_styles    >= 2
        assert stats.inline_styles   >= 1                                       # .main { color: red; }
        assert stats.external_styles >= 1                                       # href="styles.css"

    # ═══════════════════════════════════════════════════════════════════════════
    # Document Stats Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_document_stats__returns_schema(self):                              # Test document stats returns Schema type
        stats = self.mgraph.document.stats()
        assert type(stats) is Schema__Html_MGraph__Stats__Document

    def test_document_stats__has_all_components(self):                          # Test all component stats present
        stats = self.mgraph.document.stats()

        assert stats.document   is not None
        assert stats.head       is not None
        assert stats.body       is not None
        assert stats.attributes is not None
        assert stats.scripts    is not None
        assert stats.styles     is not None

    def test_document_stats__component_types(self):                             # Test component stats have correct types
        stats = self.mgraph.document.stats()

        assert type(stats.document)   is Schema__Html_MGraph__Stats__Base
        assert type(stats.head)       is Schema__Html_MGraph__Stats__Head
        assert type(stats.body)       is Schema__Html_MGraph__Stats__Body
        assert type(stats.attributes) is Schema__Html_MGraph__Stats__Attributes
        assert type(stats.scripts)    is Schema__Html_MGraph__Stats__Scripts
        assert type(stats.styles)     is Schema__Html_MGraph__Stats__Styles

    def test_document_stats__nested_access(self):                               # Test nested field access
        stats = self.mgraph.document.stats()

        # Access nested fields with type safety
        assert stats.head.element_nodes        >= 0
        assert stats.body.text_nodes           >= 0
        assert stats.attributes.unique_tags    >= 0
        assert stats.scripts.inline_scripts    >= 0
        assert stats.styles.external_styles    >= 0

    def test_document_stats__json_export(self):                                 # Test full JSON export
        stats      = self.mgraph.document.stats()
        stats_dict = stats.json()

        assert type(stats_dict)            is dict
        assert 'document'                  in stats_dict
        assert 'head'                      in stats_dict
        assert 'body'                      in stats_dict
        assert 'attributes'                in stats_dict
        assert 'scripts'                   in stats_dict
        assert 'styles'                    in stats_dict

    # ═══════════════════════════════════════════════════════════════════════════
    # Facade Stats Tests (Html_MGraph.stats())
    # ═══════════════════════════════════════════════════════════════════════════

    def test_facade_stats__returns_schema(self):                                # Test facade stats returns Schema type
        stats = self.mgraph.stats()

        # Facade delegates to document.stats()
        assert type(stats) is Schema__Html_MGraph__Stats__Document

    def test_facade_stats__same_as_document(self):                              # Test facade stats matches document
        facade_stats   = self.mgraph.stats()
        document_stats = self.mgraph.document.stats()

        assert facade_stats.head.element_nodes == document_stats.head.element_nodes
        assert facade_stats.body.text_nodes    == document_stats.body.text_nodes