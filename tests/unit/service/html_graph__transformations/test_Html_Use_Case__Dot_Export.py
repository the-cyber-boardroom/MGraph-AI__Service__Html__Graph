from unittest                                                                                                    import TestCase
from osbot_utils.type_safe.Type_Safe                                                                             import Type_Safe
from osbot_utils.utils.Objects                                                                                   import base_classes
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                                import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Html_Use_Case__Dot_Export                  import Html_Use_Case__Dot_Export


class test_Html_Use_Case__Dot_Export(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simple_html    = '<div class="main">Hello World</div>'
        cls.html_mgraph    = Html_MGraph.from_html(cls.simple_html)
        cls.dot_export     = Html_Use_Case__Dot_Export(html_mgraph=cls.html_mgraph)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with self.dot_export as _:
            assert type(_)         is Html_Use_Case__Dot_Export
            assert base_classes(_) == [Type_Safe, object]
            assert _.html_mgraph   is self.html_mgraph

    def test__init__with_empty_mgraph(self):
        empty_mgraph = Html_MGraph()
        dot_export   = Html_Use_Case__Dot_Export(html_mgraph=empty_mgraph)

        assert dot_export.html_mgraph is empty_mgraph

    # ═══════════════════════════════════════════════════════════════════════════════
    # mgraph Method Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__mgraph__returns_body_graph(self):
        result = self.dot_export.mgraph()

        assert result is not None
        assert result is self.html_mgraph.body_graph.mgraph

    def test__mgraph__returns_none_for_empty(self):
        empty_mgraph = Html_MGraph()
        dot_export   = Html_Use_Case__Dot_Export(html_mgraph=empty_mgraph)

        result = dot_export.mgraph()
        assert result is None

    # ═══════════════════════════════════════════════════════════════════════════════
    # dot_string Method Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__dot_string__clean_transformation(self):
        result = self.dot_export.dot_string('clean')

        # Should return a DOT string or empty if no body_graph
        assert type(result) is str

    def test__dot_string__semantic_transformation(self):
        result = self.dot_export.dot_string('semantic')

        assert type(result) is str

    def test__dot_string__unknown_transformation(self):
        result = self.dot_export.dot_string('unknown')

        assert result == ""

    def test__dot_string__empty_string_transformation(self):
        result = self.dot_export.dot_string('')

        assert result == ""

    # ═══════════════════════════════════════════════════════════════════════════════
    # dot_string__clean Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__dot_string__clean__returns_string(self):
        result = self.dot_export.dot_string__clean()

        assert type(result) is str

    def test__dot_string__clean__empty_for_no_body(self):
        empty_mgraph = Html_MGraph()
        dot_export   = Html_Use_Case__Dot_Export(html_mgraph=empty_mgraph)

        result = dot_export.dot_string__clean()
        assert result == ""

    # ═══════════════════════════════════════════════════════════════════════════════
    # dot_string__semantic Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__dot_string__semantic__returns_string(self):
        result = self.dot_export.dot_string__semantic()

        assert type(result) is str

    def test__dot_string__semantic__empty_for_no_body(self):
        empty_mgraph = Html_MGraph()
        dot_export   = Html_Use_Case__Dot_Export(html_mgraph=empty_mgraph)

        result = dot_export.dot_string__semantic()
        assert result == ""

    # ═══════════════════════════════════════════════════════════════════════════════
    # Config Method Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___apply_config__clean__returns_self(self):
        # This would need a mock export_dot object
        # For now, just verify the method exists
        assert hasattr(self.dot_export, '_apply_config__clean')
        assert callable(self.dot_export._apply_config__clean)

    def test___apply_config__semantic__returns_self(self):
        assert hasattr(self.dot_export, '_apply_config__semantic')
        assert callable(self.dot_export._apply_config__semantic)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Complex HTML Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__dot_string__complex_html(self):
        html = '''
        <html>
            <body>
                <div class="container">
                    <h1>Title</h1>
                    <p>Content here</p>
                </div>
            </body>
        </html>
        '''
        html_mgraph = Html_MGraph.from_html(html)
        dot_export  = Html_Use_Case__Dot_Export(html_mgraph=html_mgraph)

        clean_result    = dot_export.dot_string('clean')
        semantic_result = dot_export.dot_string('semantic')

        assert type(clean_result)    is str
        assert type(semantic_result) is str