# ═══════════════════════════════════════════════════════════════════════════════
# Integration Tests for MGraph Body Transformers - Full Roundtrip
# Part of Phase D: MGraph Body Transformers
#
# Tests the complete pipeline: HTML → MGraph → Transform → HTML
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                                   import TestCase
from MGraph_Transformer__Body__Remove_Empty_Text                                                                import MGraph_Transformer__Body__Remove_Empty_Text
from MGraph_Transformer__Body__Remove_By_Tag                                                                    import MGraph_Transformer__Body__Remove_By_Tag
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids            import Html__To__Html_Dict__With__Node_Ids
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse
from MGraph_Transformer__Body__Pipeline                                                                         import MGraph_Transformer__Body__Pipeline
from MGraph_Transformer__Body__Unwrap_Inline                                                                    import MGraph_Transformer__Body__Unwrap_Inline
from MGraph_Transformer__Body__Merge_Text                                                                       import MGraph_Transformer__Body__Merge_Text

class test_MGraph_Transformer__Roundtrip_Integration(TestCase):
    """Integration tests for full HTML → Transform → HTML roundtrip."""

    # ═══════════════════════════════════════════════════════════════════════════
    # Test HTML Samples
    # ═══════════════════════════════════════════════════════════════════════════

    SIMPLE_HTML = '<html><body><div>Hello <b>World</b>!</div></body></html>'

    COMPLEX_HTML = '''<html>
    <body>
        <div>
            This is a <a href="">link</a> with some <b>bold</b> in the mix
        </div>
        <div>
            this is the <i>2nd div</i> in here
        </div>
    </body>
</html>'''

    HTML_WITH_SCRIPT = '''<html>
    <body>
        <div>Content here</div>
        <script>console.log("test");</script>
    </body>
</html>'''

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def html_to_mgraph_document(self, html: str):
        """Convert HTML to Html_MGraph__Document using Phase A + B."""

        html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()
        doc       = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)
        return doc

    def mgraph_document_to_html(self, doc) -> str:
        """Convert Html_MGraph__Document back to HTML."""
        from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html import Html_MGraph__Document__To__Html

        return Html_MGraph__Document__To__Html().convert(doc)

    # ═══════════════════════════════════════════════════════════════════════════
    # Roundtrip Without Transformation
    # ═══════════════════════════════════════════════════════════════════════════

    def test_roundtrip__no_transform__preserves_structure(self):
        """HTML → MGraph → HTML without transformation should preserve structure."""
        doc         = self.html_to_mgraph_document(self.SIMPLE_HTML)
        output_html = self.mgraph_document_to_html(doc)

        # Key elements should be preserved
        assert '<div>'   in output_html
        assert '<b>'     in output_html
        assert 'Hello'   in output_html
        assert 'World'   in output_html

    # ═══════════════════════════════════════════════════════════════════════════
    # Roundtrip With Unwrap Inline
    # ═══════════════════════════════════════════════════════════════════════════

    def test__roundtrip__unwrap_inline__removes_b_tag(self):
        """Unwrap inline should remove <b> tags."""
        html        = self.SIMPLE_HTML
        doc         = self.html_to_mgraph_document(html)
        body_graph  = doc.body_graph.mgraph

        # Transform
        transformer = MGraph_Transformer__Body__Unwrap_Inline()
        transformer.transform(body_graph)

        # Convert back
        output_html = self.mgraph_document_to_html(doc)

        assert html        == "<html><body><div>Hello <b>World</b>!</div></body></html>"
        assert output_html ==('<!DOCTYPE html>\n'
                                 '<html>\n'
                                 '    <body>\n'
                                 '        <div>Hello World!</div>\n'
                                 '    </body>\n'
                                 '</html>\n')

        # <b> should be gone, text preserved
        assert '<b>'    not in output_html
        assert '</b>'   not in output_html
        assert 'World'      in html
        assert 'World'      in output_html       # BUG

    def test__bug__roundtrip__unwrap_inline__complex_html(self):
        """Unwrap inline on complex HTML with multiple inline elements."""
        html       = self.COMPLEX_HTML
        doc        = self.html_to_mgraph_document(html)
        body_graph = doc.body_graph.mgraph

        # Transform
        transformer = MGraph_Transformer__Body__Unwrap_Inline()
        transformer.transform(body_graph)

        # Convert back
        output_html = self.mgraph_document_to_html(doc)
        assert html        ==  ( '<html>\n'
                                 '    <body>\n'
                                 '        <div>\n'
                                 '            This is a <a href="">link</a> with some <b>bold</b> in the mix\n'
                                 '        </div>\n'
                                 '        <div>\n'
                                 '            this is the <i>2nd div</i> in here\n'
                                 '        </div>\n'
                                 '    </body>\n'
                                 '</html>')
        assert output_html == ('<!DOCTYPE html>\n'
                                 '<html>\n'
                                 '    <body>\n'
                                 '        <div>\n'
                                 '            This is a link with some bold in the mix\n'
                                 '        </div>\n'
                                 '        <div>\n'
                                 '            this is the 2nd div in here\n'
                                 '        </div>\n'
                                 '    </body>\n'
                                 '</html>\n')


        # Inline tags should be gone
        assert '<a'  not in output_html.lower()
        assert '<i'  not in output_html.lower()

        # Text should be preserved
        assert 'link'        in html
        assert 'bold'        in html
        assert '2nd div'     in html
        assert 'link'        in output_html
        assert 'bold'        in output_html
        assert '2nd div'     in output_html

    # ═══════════════════════════════════════════════════════════════════════════
    # Roundtrip With Pipeline
    # ═══════════════════════════════════════════════════════════════════════════

    def test_roundtrip__pipeline__unwrap_and_merge(self):

        doc        = self.html_to_mgraph_document(self.SIMPLE_HTML)
        body_graph = doc.body_graph.mgraph

        # Create pipeline
        pipeline = (MGraph_Transformer__Body__Pipeline()
            .add(MGraph_Transformer__Body__Unwrap_Inline())
            .add(MGraph_Transformer__Body__Merge_Text()))

        # Transform
        pipeline.transform(body_graph)

        # Convert back
        output_html = self.mgraph_document_to_html(doc)

        # <b> should be gone
        assert '<b>' not in output_html

    # ═══════════════════════════════════════════════════════════════════════════
    # Roundtrip With Remove By Tag
    # ═══════════════════════════════════════════════════════════════════════════

    def test_roundtrip__remove_script(self):
        doc        = self.html_to_mgraph_document(self.HTML_WITH_SCRIPT)
        body_graph = doc.body_graph.mgraph

        # Transform
        transformer = MGraph_Transformer__Body__Remove_By_Tag(tags_to_remove={'script'})
        transformer.transform(body_graph)

        # Convert back
        output_html = self.mgraph_document_to_html(doc)

        # Script should be gone
        assert '<script'    not in output_html.lower()
        assert 'console.log' not in output_html

        # Content should remain
        assert 'Content here' in output_html

    # ═══════════════════════════════════════════════════════════════════════════
    # In-Place Modification Test
    # ═══════════════════════════════════════════════════════════════════════════

    def test_inplace_modification__same_graph_reference(self):

        doc        = self.html_to_mgraph_document(self.SIMPLE_HTML)
        body_graph = doc.body_graph.mgraph

        # Store reference
        original_graph = body_graph

        # Transform
        transformer = MGraph_Transformer__Body__Unwrap_Inline()
        result      = transformer.transform(body_graph)

        # Should be same object
        assert result is original_graph
        assert doc.body_graph.mgraph is original_graph

    # ═══════════════════════════════════════════════════════════════════════════
    # Full Workflow Test
    # ═══════════════════════════════════════════════════════════════════════════

    def test_full_workflow__clean_html(self):
        """Full workflow: HTML with inline elements → Clean HTML."""

        input_html = self.COMPLEX_HTML

        # Phase A + B: HTML → MGraph
        doc        = self.html_to_mgraph_document(input_html)
        body_graph = doc.body_graph.mgraph

        # Phase D: Transform
        pipeline = (MGraph_Transformer__Body__Pipeline()
                        .add(MGraph_Transformer__Body__Unwrap_Inline    ())
                        .add(MGraph_Transformer__Body__Merge_Text       ())
                        .add(MGraph_Transformer__Body__Remove_Empty_Text()))

        pipeline.transform(body_graph)

        # Convert back to HTML
        output_html = self.mgraph_document_to_html(doc)

        # Verify inline tags removed
        assert '<a'  not in output_html.lower()
        assert '<i'  not in output_html.lower()

        # Verify text preserved
        assert 'link' in output_html
        assert 'bold' in output_html
        assert '2nd div' in output_html

        assert input_html == ('<html>\n'
                              '    <body>\n'
                              '        <div>\n'
                              '            This is a <a href="">link</a> with some <b>bold</b> in the mix\n'
                              '        </div>\n'
                              '        <div>\n'
                              '            this is the <i>2nd div</i> in here\n'
                              '        </div>\n'
                              '    </body>\n'
                              '</html>')

        assert output_html == ( '<!DOCTYPE html>\n'
                                 '<html>\n'
                                 '    <body>\n'
                                 '        <div>\n'
                                 '            This is a link with some bold in the mix\n'
                                 '        </div>\n'
                                 '        <div>\n'
                                 '            this is the 2nd div in here\n'
                                 '        </div>\n'
                                 '    </body>\n'
                                 '</html>\n')

        # Print for visual verification
        # print(f"\nINPUT:\n{input_html}")
        # print(f"\nOUTPUT:\n{output_html}")

    def test_create_flatten_transformer(self):
        from Html_MGraph__Transformer import create_flatten_transformer

        # def transform_html(input_html):
        #
        #     doc        = self.html_to_mgraph_document(input_html)
        #     body_graph = doc.body_graph.mgraph
        #
        #     pipeline = (MGraph_Transformer__Body__Pipeline()
        #                     .add(MGraph_Transformer__Body__Unwrap_Inline    ())
        #                     .add(MGraph_Transformer__Body__Merge_Text       ())
        #                     .add(MGraph_Transformer__Body__Remove_Empty_Text())
        #                 )
        #     pipeline.transform(body_graph)
        #
        #     # Convert back to HTML
        #     output_html = self.mgraph_document_to_html(doc)
        #     return output_html

        #print(transform_html(HTML_EXAMPLE__3__input))
        assert create_flatten_transformer().transform(HTML_EXAMPLE__1__input) == HTML_EXAMPLE__1__OUTPUT
        assert create_flatten_transformer().transform(HTML_EXAMPLE__2__input) == HTML_EXAMPLE__2__OUTPUT
        assert create_flatten_transformer().transform(HTML_EXAMPLE__3__input) == HTML_EXAMPLE__3__OUTPUT        # BUG
        assert create_flatten_transformer().transform(HTML_EXAMPLE__4__input) == HTML_EXAMPLE__4__OUTPUT        # BUG


HTML_EXAMPLE__1__input = '''<html>
    <body>
        <div>
            This is a <a href="">link</a> with some <b>bold</b> in the mix
        </div>
        <div>
            this is the <i>2nd div</i> in here
        </div>
    </body>
</html>'''

HTML_EXAMPLE__1__OUTPUT = '''\
<!DOCTYPE html>
<html>
    <body>
        <div>
            This is a link with some bold in the mix
        </div>
        <div>
            this is the 2nd div in here
        </div>
    </body>
</html>
'''

HTML_EXAMPLE__2__input = """\
<!DOCTYPE html>
<html>
    <head>
        <title>Simple HTML page</title>
    </head>
    <body>
        <div>
            <h1>Hello World</h1>
            <p>Welcome to HTML Graph</p>
        </div>
    </body>
</html>"""

HTML_EXAMPLE__2__OUTPUT = """\
<!DOCTYPE html>
<html>
    <head>
        <title>Simple HTML page</title>
    </head>
    <body>
        <div>
            <h1>Hello World</h1>
            <p>Welcome to HTML Graph</p>
        </div>
    </body>
</html>
"""

HTML_EXAMPLE__3__input = '''<html>
    <body>
        <div>
            <b>Hello</b><i> </i><span>World</span><b>!</b>
        </div>
    </body>
</html>'''

HTML_EXAMPLE__3__OUTPUT = '''\
<!DOCTYPE html>
<html>
    <body>
        <div>HelloWorld!<i></i></div>
    </body>
</html>
'''                 # BUG

HTML_EXAMPLE__4__input = '''<html>
    <body>
        <div>
            Start <span>middle <b>bold</b></span> end
        </div>
    </body>
</html>'''

HTML_EXAMPLE__4__OUTPUT = '''\
<!DOCTYPE html>
<html>
    <body>
        <div>
            Start middle  end
        </div>
    </body>
</html>
'''     # BUG


HTML_EXAMPLE__5__input = '''<html>
    <body>
        <div>
            Hello
            <b>
                World
            </b>
        </div>
    </body>
</html>'''

HTML_EXAMPLE__5__OUTPUT = '''\
<!DOCTYPE html>
<html>
    <body>
        <div>
            Hello World
        </div>
    </body>
</html>
'''

HTML_EXAMPLE__6__input = '''<html>
    <body>
        <div>
            <span><b><i><u>Deep</u></i></b></span> text
        </div>
    </body>
</html>'''

HTML_EXAMPLE__6__OUTPUT = '''\
<!DOCTYPE html>
<html>
    <body>
        <div>
            Deep text
        </div>
    </body>
</html>
'''

HTML_EXAMPLE__7__input = '''<html>
    <body>
        <div>
            <b>Hello</b>
            <p><i>World</i></p>
        </div>
    </body>
</html>'''

HTML_EXAMPLE__7__OUTPUT = '''\
<!DOCTYPE html>
<html>
    <body>
        <div>
            Hello
            <p>
                World
            </p>
        </div>
    </body>
</html>
'''

HTML_EXAMPLE__8__input = '''<html>
    <body>
        <div>
            <span> </span><b></b><i>   </i>
        </div>
    </body>
</html>'''

HTML_EXAMPLE__8__OUTPUT = '''\
<!DOCTYPE html>
<html>
    <body>
        <div>
        </div>
    </body>
</html>
'''

HTML_EXAMPLE__9__input = '''<html>
    <body>
        <div>
            Start <b>here</b>
            <script>evil()</script>
            <i>end</i>
        </div>
    </body>
</html>'''

HTML_EXAMPLE__9__OUTPUT = '''\
<!DOCTYPE html>
<html>
    <body>
        <div>
            Start here end
        </div>
    </body>
</html>
'''

HTML_EXAMPLE__10__input = '''<html>
    <head>
        <title><b>Title</b></title>
    </head>
    <body>
        <div><b>Body</b> text</div>
    </body>
</html>'''

HTML_EXAMPLE__10__OUTPUT = '''\
<!DOCTYPE html>
<html>
    <head>
        <title><b>Title</b></title>
    </head>
    <body>
        <div>
            Body text
        </div>
    </body>
</html>
'''


