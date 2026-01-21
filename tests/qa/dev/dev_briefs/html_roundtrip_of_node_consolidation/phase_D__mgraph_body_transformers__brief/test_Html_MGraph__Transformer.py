# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Html_MGraph__Transformer helper class
# Part of Phase D: MGraph Body Transformers
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                import TestCase
from Html_MGraph__Transformer                import Html_MGraph__Transformer
from MGraph_Transformer__Body__Unwrap_Inline import MGraph_Transformer__Body__Unwrap_Inline
from MGraph_Transformer__Body__Merge_Text    import MGraph_Transformer__Body__Merge_Text
from Html_MGraph__Transformer                import transform_html
from Html_MGraph__Transformer                import create_flatten_transformer
from Html_MGraph__Transformer                import create_clean_transformer
# ═══════════════════════════════════════════════════════════════════════════════
# Test HTML Examples
# ═══════════════════════════════════════════════════════════════════════════════

HTML_EXAMPLE__1__INPUT = '<html><body><div>Hello <b>World</b>!</div></body></html>'

HTML_EXAMPLE__1__OUTPUT = ('<!DOCTYPE html>\n'
                           '<html>\n'
                           '    <body>\n'
                           '        <div>Hello World!</div>\n'
                           '    </body>\n'
                           '</html>\n')

HTML_EXAMPLE__2__INPUT = '''<html>
    <body>
        <div>
            This is a <a href="">link</a> with some <b>bold</b> in the mix
        </div>
        <div>
            this is the <i>2nd div</i> in here
        </div>
    </body>
</html>'''

HTML_EXAMPLE__2__OUTPUT = ('<!DOCTYPE html>\n'
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

HTML_EXAMPLE__3__INPUT = '''<html>
    <body>
        <nav>Navigation here</nav>
        <div>Main content</div>
        <script>console.log("test");</script>
    </body>
</html>'''


class test_Html_MGraph__Transformer(TestCase):
    """Tests for the Html_MGraph__Transformer helper class."""

    # ═══════════════════════════════════════════════════════════════════════════
    # Basic Usage Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_transform__simple_html(self):

        transformer = Html_MGraph__Transformer(
            transformers=[MGraph_Transformer__Body__Unwrap_Inline(),
                          MGraph_Transformer__Body__Merge_Text()   ]
        )

        result = transformer.transform(HTML_EXAMPLE__1__INPUT)

        assert '<b>'   not in result
        assert 'World' in result

    def test_transform__fluent_api(self):
        result = (Html_MGraph__Transformer()
            .add(MGraph_Transformer__Body__Unwrap_Inline())
            .add(MGraph_Transformer__Body__Merge_Text())
            .transform(HTML_EXAMPLE__1__INPUT))

        assert '<b>'   not in result
        assert 'World' in result

    # ═══════════════════════════════════════════════════════════════════════════
    # Factory Function Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_create_flatten_transformer(self):

        transformer = create_flatten_transformer()
        result      = transformer.transform(HTML_EXAMPLE__1__INPUT)

        assert result == HTML_EXAMPLE__1__OUTPUT

    def test_create_flatten_transformer__complex(self):

        transformer = create_flatten_transformer()
        result      = transformer.transform(HTML_EXAMPLE__2__INPUT)

        assert result == HTML_EXAMPLE__2__OUTPUT

    def test_create_clean_transformer(self):

        transformer = create_clean_transformer()
        result      = transformer.transform(HTML_EXAMPLE__3__INPUT)

        assert '<nav>'    not in result
        assert '<script>' not in result
        assert 'Main content' in result

    def test_create_clean_transformer__custom_tags(self):

        transformer = create_clean_transformer(remove_tags={'script'})
        result      = transformer.transform(HTML_EXAMPLE__3__INPUT)

        assert '<script>' not in result
        assert 'Navigation' in result                                           # nav NOT removed

    # ═══════════════════════════════════════════════════════════════════════════
    # Convenience Function Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_transform_html__default(self):
        result = transform_html(HTML_EXAMPLE__1__INPUT)

        assert result == HTML_EXAMPLE__1__OUTPUT

    def test_transform_html__custom_transformers(self):
        from Html_MGraph__Transformer                import transform_html
        from MGraph_Transformer__Body__Unwrap_Inline import MGraph_Transformer__Body__Unwrap_Inline

        result = transform_html(HTML_EXAMPLE__1__INPUT,
                                transformers=[MGraph_Transformer__Body__Unwrap_Inline()])

        assert '<b>' not in result
        assert 'World' in result

    # ═══════════════════════════════════════════════════════════════════════════
    # Introspection Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_count(self):

        transformer = (Html_MGraph__Transformer()
            .add(MGraph_Transformer__Body__Unwrap_Inline())
            .add(MGraph_Transformer__Body__Merge_Text()))

        assert transformer.count() == 2

    def test_list_transformers(self):

        transformer = Html_MGraph__Transformer().add(MGraph_Transformer__Body__Unwrap_Inline())
        names       = transformer.list_transformers()

        assert 'MGraph_Transformer__Body__Unwrap_Inline' in names

    def test_clear(self):

        transformer = Html_MGraph__Transformer().add(MGraph_Transformer__Body__Unwrap_Inline())

        assert transformer.count() == 1

        transformer.clear()

        assert transformer.count() == 0

    # ═══════════════════════════════════════════════════════════════════════════
    # Multiple Examples Test
    # ═══════════════════════════════════════════════════════════════════════════

    def test_multiple_transformations(self):
        """Test multiple HTML examples with the same transformer."""

        transformer = create_flatten_transformer()

        assert transformer.transform(HTML_EXAMPLE__1__INPUT) == HTML_EXAMPLE__1__OUTPUT
        assert transformer.transform(HTML_EXAMPLE__2__INPUT) == HTML_EXAMPLE__2__OUTPUT