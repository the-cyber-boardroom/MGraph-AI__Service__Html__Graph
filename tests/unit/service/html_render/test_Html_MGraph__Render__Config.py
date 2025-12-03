from unittest                                                                       import TestCase
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.utils.Objects                                                      import base_classes
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config   import Html_MGraph__Render__Config
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config   import Enum__Html_Render__Preset
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors   import Html_MGraph__Render__Colors
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors   import Enum__Html_Render__Color_Scheme
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Labels   import Html_MGraph__Render__Labels


class test_Html_MGraph__Render__Config(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = Html_MGraph__Render__Config()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                 # Test auto-initialization
        with Html_MGraph__Render__Config() as _:
            assert type(_)                is Html_MGraph__Render__Config
            assert base_classes(_)        == [Type_Safe, object]
            assert type(_.colors)         is Html_MGraph__Render__Colors
            assert type(_.labels)         is Html_MGraph__Render__Labels
            assert _.preset               == Enum__Html_Render__Preset.FULL_DETAIL

    def test__init__default_visibility(self):                                               # Test default visibility settings
        with Html_MGraph__Render__Config() as _:
            assert _.show_tag_nodes   == True
            assert _.show_attr_nodes  == True
            assert _.show_text_nodes  == True
            assert _.show_tag_edges   == True
            assert _.show_attr_edges  == True
            assert _.show_text_edges  == True
            assert _.show_child_edges == True

    def test__init__default_shapes(self):                                                   # Test default shape settings
        with Html_MGraph__Render__Config() as _:
            assert _.element_shape == 'box'
            assert _.tag_shape     == 'ellipse'
            assert _.attr_shape    == 'box'                                                 # Box for better text fit
            assert _.text_shape    == 'note'

    def test__init__default_edge_styles(self):                                              # Test default edge style settings
        with Html_MGraph__Render__Config() as _:
            assert _.child_edge_style == 'solid'
            assert _.tag_edge_style   == 'dashed'
            assert _.attr_edge_style  == 'dotted'
            assert _.text_edge_style  == 'solid'

    # ═══════════════════════════════════════════════════════════════════════════════
    # apply_preset Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_apply_preset__full_detail(self):                                               # Test full detail preset
        with Html_MGraph__Render__Config() as _:
            _.apply_preset(Enum__Html_Render__Preset.FULL_DETAIL)
            assert _.show_tag_nodes  == True
            assert _.show_attr_nodes == True
            assert _.show_text_nodes == True
            assert _.show_tag_edges  == True
            assert _.show_attr_edges == True
            assert _.show_text_edges == True

    def test_apply_preset__structure_only(self):                                            # Test structure only preset
        with Html_MGraph__Render__Config() as _:
            _.apply_preset(Enum__Html_Render__Preset.STRUCTURE_ONLY)
            assert _.show_tag_nodes  == False
            assert _.show_attr_nodes == False
            assert _.show_text_nodes == False
            assert _.show_tag_edges  == False
            assert _.show_attr_edges == False
            assert _.show_text_edges == False

    def test_apply_preset__minimal(self):                                                   # Test minimal preset
        with Html_MGraph__Render__Config() as _:
            _.apply_preset(Enum__Html_Render__Preset.MINIMAL)
            assert _.show_tag_nodes  == False
            assert _.show_attr_nodes == False
            assert _.show_text_nodes == False

    def test_apply_preset__returns_self(self):                                              # Test fluent interface
        with Html_MGraph__Render__Config() as _:
            result = _.apply_preset(Enum__Html_Render__Preset.FULL_DETAIL)
            assert result is _

    # ═══════════════════════════════════════════════════════════════════════════════
    # set_color_scheme Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_set_color_scheme__default(self):                                               # Test setting default scheme
        with Html_MGraph__Render__Config() as _:
            _.set_color_scheme(Enum__Html_Render__Color_Scheme.DEFAULT)
            assert _.colors.scheme == Enum__Html_Render__Color_Scheme.DEFAULT

    def test_set_color_scheme__monochrome(self):                                            # Test setting monochrome scheme
        with Html_MGraph__Render__Config() as _:
            _.set_color_scheme(Enum__Html_Render__Color_Scheme.MONOCHROME)
            assert _.colors.scheme == Enum__Html_Render__Color_Scheme.MONOCHROME

    def test_set_color_scheme__high_contrast(self):                                         # Test setting high contrast scheme
        with Html_MGraph__Render__Config() as _:
            _.set_color_scheme(Enum__Html_Render__Color_Scheme.HIGH_CONTRAST)
            assert _.colors.scheme == Enum__Html_Render__Color_Scheme.HIGH_CONTRAST

    def test_set_color_scheme__returns_self(self):                                          # Test fluent interface
        with Html_MGraph__Render__Config() as _:
            result = _.set_color_scheme(Enum__Html_Render__Color_Scheme.DEFAULT)
            assert result is _

    # ═══════════════════════════════════════════════════════════════════════════════
    # _escape_dot_string Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__escape_dot_string__quotes(self):                                              # Test quote escaping
        with self.config as _:
            assert _._escape_dot_string('say "hello"') == 'say \\"hello\\"'

    def test__escape_dot_string__backslashes(self):                                         # Test backslash escaping
        with self.config as _:
            assert _._escape_dot_string('path\\to\\file') == 'path\\\\to\\\\file'

    def test__escape_dot_string__newlines(self):                                            # Test newline escaping
        with self.config as _:
            assert _._escape_dot_string('line1\nline2') == 'line1\\nline2'

    def test__escape_dot_string__empty(self):                                               # Test empty string
        with self.config as _:
            assert _._escape_dot_string('')   == ''
            assert _._escape_dot_string(None) == ''
