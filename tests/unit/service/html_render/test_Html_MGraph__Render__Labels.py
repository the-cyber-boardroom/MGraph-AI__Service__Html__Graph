from unittest                                                                       import TestCase
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.utils.Objects                                                      import base_classes
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Labels   import Html_MGraph__Render__Labels


class test_Html_MGraph__Render__Labels(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.labels = Html_MGraph__Render__Labels()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                 # Test auto-initialization
        with Html_MGraph__Render__Labels() as _:
            assert type(_)              is Html_MGraph__Render__Labels
            assert base_classes(_)      == [Type_Safe, object]
            assert _.max_text_length    == 30
            assert _.show_tag_brackets  == True

    def test__init__custom_settings(self):                                                  # Test custom initialization
        with Html_MGraph__Render__Labels(max_text_length=50, show_tag_brackets=False) as _:
            assert _.max_text_length   == 50
            assert _.show_tag_brackets == False

    # ═══════════════════════════════════════════════════════════════════════════════
    # label_for_node Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_label_for_node__tag_path(self):                                                # Test routing for tag paths
        with self.labels as _:
            result = _.label_for_node('tag:div', 'div')
            assert result == '<div>'

    def test_label_for_node__attr_path(self):                                               # Test routing for attr paths
        with self.labels as _:
            result = _.label_for_node('attr:class', 'main')
            assert result == 'class="main"'

    def test_label_for_node__text_path(self):                                               # Test routing for text paths
        with self.labels as _:
            result = _.label_for_node('text', 'Hello World')
            assert result == 'Hello World'

    def test_label_for_node__element_path(self):                                            # Test routing for element paths
        with self.labels as _:
            result = _.label_for_node('div.p[0]')
            assert result == '<p>'

    def test_label_for_node__empty_path(self):                                              # Test empty path handling
        with self.labels as _:
            assert _.label_for_node('', 'value')  == 'value'
            assert _.label_for_node('', None)     == ''
            assert _.label_for_node(None, 'test') == 'test'

    # ═══════════════════════════════════════════════════════════════════════════════
    # label_for_element_node Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_label_for_element_node__simple_path(self):                                     # Test simple element path
        with self.labels as _:
            assert _.label_for_element_node('div')  == '<div>'
            assert _.label_for_element_node('body') == '<body>'

    def test_label_for_element_node__nested_path(self):                                     # Test nested element path
        with self.labels as _:
            assert _.label_for_element_node('html.body.div') == '<div>'
            assert _.label_for_element_node('div.p')         == '<p>'

    def test_label_for_element_node__with_index(self):                                      # Test path with sibling index
        with self.labels as _:
            assert _.label_for_element_node('div.p[0]') == '<p>'
            assert _.label_for_element_node('div.p[2]') == '<p>'
            assert _.label_for_element_node('ul.li[5]') == '<li>'

    def test_label_for_element_node__empty(self):                                           # Test empty path
        with self.labels as _:
            assert _.label_for_element_node('') == ''

    def test_label_for_element_node__without_brackets(self):                                # Test without tag brackets
        with Html_MGraph__Render__Labels(show_tag_brackets=False) as _:
            assert _.label_for_element_node('div')       == 'div'
            assert _.label_for_element_node('div.p[0]')  == 'p'

    # ═══════════════════════════════════════════════════════════════════════════════
    # label_for_tag_node Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_label_for_tag_node__with_value(self):                                          # Test tag label with value
        with self.labels as _:
            assert _.label_for_tag_node('tag:div', 'div')   == '<div>'
            assert _.label_for_tag_node('tag:span', 'span') == '<span>'

    def test_label_for_tag_node__from_path(self):                                           # Test tag label extracted from path
        with self.labels as _:
            assert _.label_for_tag_node('tag:p', None)    == '<p>'
            assert _.label_for_tag_node('tag:body', None) == '<body>'

    def test_label_for_tag_node__no_value_no_path(self):                                    # Test fallback for missing info
        with self.labels as _:
            assert _.label_for_tag_node('', None)      == '<unknown>'
            assert _.label_for_tag_node(None, None)    == '<unknown>'

    def test_label_for_tag_node__without_brackets(self):                                    # Test without brackets
        with Html_MGraph__Render__Labels(show_tag_brackets=False) as _:
            assert _.label_for_tag_node('tag:div', 'div') == 'div'

    # ═══════════════════════════════════════════════════════════════════════════════
    # label_for_attr_node Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_label_for_attr_node__name_and_value(self):                                     # Test attr with name and value
        with self.labels as _:
            assert _.label_for_attr_node('attr:class', 'main')      == 'class="main"'
            assert _.label_for_attr_node('attr:id', 'content')      == 'id="content"'
            assert _.label_for_attr_node('attr:href', '/link')      == 'href="/link"'

    def test_label_for_attr_node__value_only(self):                                         # Test attr with value but no name
        with self.labels as _:
            assert _.label_for_attr_node('', 'value') == '"value"'

    def test_label_for_attr_node__name_only(self):                                          # Test attr with name but no value
        with self.labels as _:
            assert _.label_for_attr_node('attr:class', None) == 'class'

    def test_label_for_attr_node__empty(self):                                              # Test empty attr
        with self.labels as _:
            assert _.label_for_attr_node('', None) == 'attr'

    def test_label_for_attr_node__long_value_truncated(self):                               # Test long value gets truncated
        with self.labels as _:
            long_value = 'a' * 50
            result     = _.label_for_attr_node('attr:class', long_value)
            assert len(result) < 50                                                         # Should be truncated
            assert '...' in result                                                          # Should have ellipsis

    # ═══════════════════════════════════════════════════════════════════════════════
    # label_for_text_node Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_label_for_text_node__short_text(self):                                         # Test short text unchanged
        with self.labels as _:
            assert _.label_for_text_node('Hello World')  == 'Hello World'
            assert _.label_for_text_node('Short')        == 'Short'

    def test_label_for_text_node__long_text_truncated(self):                                # Test long text gets truncated
        with self.labels as _:
            long_text = 'This is a very long text that should be truncated'
            result    = _.label_for_text_node(long_text)
            assert len(result) <= 30
            assert result.endswith('...')

    def test_label_for_text_node__custom_max_length(self):                                  # Test custom max length
        with self.labels as _:
            text   = 'This is medium length text'
            result = _.label_for_text_node(text, max_length=15)
            assert len(result) <= 15
            assert result.endswith('...')

    def test_label_for_text_node__none_value(self):                                         # Test None value
        with self.labels as _:
            assert _.label_for_text_node(None) == '[text]'

    def test_label_for_text_node__whitespace_normalized(self):                              # Test whitespace is normalized
        with self.labels as _:
            assert _.label_for_text_node('  hello   world  ') == 'hello world'
            assert _.label_for_text_node('line1\nline2')      == 'line1 line2'

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_path_depth Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_get_path_depth__root(self):                                                    # Test root element depth
        with self.labels as _:
            assert _.get_path_depth('div')  == 1
            assert _.get_path_depth('html') == 1

    def test_get_path_depth__nested(self):                                                  # Test nested path depth
        with self.labels as _:
            assert _.get_path_depth('html.body')     == 2
            assert _.get_path_depth('html.body.div') == 3
            assert _.get_path_depth('div.p[0].span') == 3

    def test_get_path_depth__value_nodes(self):                                             # Test value node paths return 0
        with self.labels as _:
            assert _.get_path_depth('tag:div')   == 0
            assert _.get_path_depth('attr:class')== 0
            assert _.get_path_depth('text')      == 0

    def test_get_path_depth__empty(self):                                                   # Test empty path
        with self.labels as _:
            assert _.get_path_depth('')   == 0
            assert _.get_path_depth(None) == 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # extract_tag_from_path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_extract_tag_from_path__simple(self):                                           # Test simple path
        with self.labels as _:
            assert _.extract_tag_from_path('div')  == 'div'
            assert _.extract_tag_from_path('body') == 'body'

    def test_extract_tag_from_path__nested(self):                                           # Test nested path extracts last tag
        with self.labels as _:
            assert _.extract_tag_from_path('html.body.div') == 'div'
            assert _.extract_tag_from_path('div.p')         == 'p'

    def test_extract_tag_from_path__with_index(self):                                       # Test path with index
        with self.labels as _:
            assert _.extract_tag_from_path('div.p[0]')  == 'p'
            assert _.extract_tag_from_path('ul.li[5]')  == 'li'

    def test_extract_tag_from_path__value_paths(self):                                      # Test value paths return empty
        with self.labels as _:
            assert _.extract_tag_from_path('tag:div')    == ''
            assert _.extract_tag_from_path('attr:class') == ''
            assert _.extract_tag_from_path('text')       == ''

    def test_extract_tag_from_path__empty(self):                                            # Test empty path
        with self.labels as _:
            assert _.extract_tag_from_path('')   == ''
            assert _.extract_tag_from_path(None) == ''
