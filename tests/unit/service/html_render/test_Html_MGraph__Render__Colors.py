from unittest                                                                       import TestCase
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.utils.Objects                                                      import base_classes
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors   import Html_MGraph__Render__Colors
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors   import Enum__Html_Render__Color_Scheme


class test_Html_MGraph__Render__Colors(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.colors = Html_MGraph__Render__Colors()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                 # Test auto-initialization
        with Html_MGraph__Render__Colors() as _:
            assert type(_)         is Html_MGraph__Render__Colors
            assert base_classes(_) == [Type_Safe, object]
            assert _.scheme        == Enum__Html_Render__Color_Scheme.DEFAULT

    def test__init__with_scheme(self):                                                      # Test initialization with specific scheme
        with Html_MGraph__Render__Colors(scheme=Enum__Html_Render__Color_Scheme.MONOCHROME) as _:
            assert _.scheme == Enum__Html_Render__Color_Scheme.MONOCHROME

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_element_color Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_get_element_color__depth_0(self):                                              # Test root element color
        with self.colors as _:
            color = _.get_element_color(0)
            assert color == '#FFFFFF'                                                       # White for root

    def test_get_element_color__depth_1(self):                                              # Test depth 1 color
        with self.colors as _:
            color = _.get_element_color(1)
            assert color == '#F5F5F5'

    def test_get_element_color__depth_exceeds_max(self):                                    # Test depth beyond defined colors
        with self.colors as _:
            color = _.get_element_color(100)                                                # Should return last color
            assert color == '#B0B0B0'

    def test_get_element_color__monochrome_scheme(self):                                    # Test element color with monochrome
        with Html_MGraph__Render__Colors(scheme=Enum__Html_Render__Color_Scheme.MONOCHROME) as _:
            assert _.get_element_color(0) == '#FFFFFF'
            assert _.get_element_color(1) == '#F0F0F0'

    def test_get_element_color__high_contrast_scheme(self):                                 # Test element color with high contrast
        with Html_MGraph__Render__Colors(scheme=Enum__Html_Render__Color_Scheme.HIGH_CONTRAST) as _:
            assert _.get_element_color(0) == '#FFFFFF'
            assert _.get_element_color(1) == '#E8E8E8'

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_tag_color Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_get_tag_color__structural(self):                                               # Test structural tags get blue
        with self.colors as _:
            assert _.get_tag_color('div')     == '#4A90D9'
            assert _.get_tag_color('span')    == '#4A90D9'
            assert _.get_tag_color('section') == '#4A90D9'

    def test_get_tag_color__text(self):                                                     # Test text tags get green
        with self.colors as _:
            assert _.get_tag_color('p')  == '#5CB85C'
            assert _.get_tag_color('h1') == '#5CB85C'
            assert _.get_tag_color('a')  == '#5CB85C'

    def test_get_tag_color__list(self):                                                     # Test list tags get cyan
        with self.colors as _:
            assert _.get_tag_color('ul') == '#5BC0DE'
            assert _.get_tag_color('ol') == '#5BC0DE'
            assert _.get_tag_color('li') == '#5BC0DE'

    def test_get_tag_color__table(self):                                                    # Test table tags get orange
        with self.colors as _:
            assert _.get_tag_color('table') == '#F0AD4E'
            assert _.get_tag_color('tr')    == '#F0AD4E'
            assert _.get_tag_color('td')    == '#F0AD4E'

    def test_get_tag_color__form(self):                                                     # Test form tags get red
        with self.colors as _:
            assert _.get_tag_color('form')   == '#D9534F'
            assert _.get_tag_color('input')  == '#D9534F'
            assert _.get_tag_color('button') == '#D9534F'

    def test_get_tag_color__media(self):                                                    # Test media tags get purple
        with self.colors as _:
            assert _.get_tag_color('img')   == '#9B59B6'
            assert _.get_tag_color('video') == '#9B59B6'
            assert _.get_tag_color('svg')   == '#9B59B6'

    def test_get_tag_color__meta(self):                                                     # Test meta tags get blue-gray
        with self.colors as _:
            assert _.get_tag_color('meta')   == '#607D8B'
            assert _.get_tag_color('title')  == '#607D8B'
            assert _.get_tag_color('script') == '#607D8B'

    def test_get_tag_color__unknown(self):                                                  # Test unknown tags get gray
        with self.colors as _:
            assert _.get_tag_color('custom-element') == '#777777'
            assert _.get_tag_color('unknown')        == '#777777'

    def test_get_tag_color__case_insensitive(self):                                         # Test tag lookup is case insensitive
        with self.colors as _:
            assert _.get_tag_color('DIV') == _.get_tag_color('div')
            assert _.get_tag_color('Span') == _.get_tag_color('span')

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_tag_category Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_get_tag_category__structural(self):                                            # Test structural category detection
        with self.colors as _:
            assert _.get_tag_category('div')  == 'structural'
            assert _.get_tag_category('body') == 'structural'

    def test_get_tag_category__unknown(self):                                               # Test unknown category for custom tags
        with self.colors as _:
            assert _.get_tag_category('my-custom-tag') == 'unknown'

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_attr_color Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_get_attr_color__default(self):                                                 # Test default attribute color
        with self.colors as _:
            assert _.get_attr_color() == '#B39DDB'                                          # Muted purple

    def test_get_attr_color__monochrome(self):                                              # Test monochrome attribute color
        with Html_MGraph__Render__Colors(scheme=Enum__Html_Render__Color_Scheme.MONOCHROME) as _:
            assert _.get_attr_color() == '#C0C0C0'

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_text_color Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_get_text_color__default(self):                                                 # Test default text color
        with self.colors as _:
            assert _.get_text_color() == '#FFF9C4'                                          # Light yellow

    def test_get_text_color__high_contrast(self):                                           # Test high contrast text color
        with Html_MGraph__Render__Colors(scheme=Enum__Html_Render__Color_Scheme.HIGH_CONTRAST) as _:
            assert _.get_text_color() == '#FFEB3B'

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_edge_color Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_get_edge_color__child(self):                                                   # Test child edge color
        with self.colors as _:
            assert _.get_edge_color('child') == '#333333'

    def test_get_edge_color__tag(self):                                                     # Test tag edge color
        with self.colors as _:
            assert _.get_edge_color('tag') == '#888888'

    def test_get_edge_color__attr(self):                                                    # Test attr edge color
        with self.colors as _:
            assert _.get_edge_color('attr') == '#B39DDB'

    def test_get_edge_color__text(self):                                                    # Test text edge color
        with self.colors as _:
            assert _.get_edge_color('text') == '#FFC107'

    def test_get_edge_color__unknown_predicate(self):                                       # Test unknown predicate defaults to child
        with self.colors as _:
            assert _.get_edge_color('unknown') == '#333333'

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_font_color Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_get_font_color__element(self):                                                 # Test element font color
        with self.colors as _:
            assert _.get_font_color('element') == '#333333'

    def test_get_font_color__tag(self):                                                     # Test tag font color (white for readability)
        with self.colors as _:
            assert _.get_font_color('tag') == '#FFFFFF'

    def test_get_font_color__attr(self):                                                    # Test attr font color
        with self.colors as _:
            assert _.get_font_color('attr') == '#333333'

    def test_get_font_color__text(self):                                                    # Test text font color
        with self.colors as _:
            assert _.get_font_color('text') == '#333333'

    def test_get_font_color__unknown_type(self):                                            # Test unknown type defaults to element
        with self.colors as _:
            assert _.get_font_color('unknown') == '#333333'


