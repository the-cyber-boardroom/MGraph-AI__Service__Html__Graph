import pytest
from unittest                                                                       import TestCase
from osbot_utils.utils.Env                                                          import env_var_set, load_dotenv
from osbot_utils.utils.Files                                                        import path_combine, file_exists
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.utils.Objects                                                      import base_classes
from mgraph_db.mgraph.MGraph                                                        import MGraph
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph                    import Html_MGraph
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Screenshot       import Html_MGraph__Screenshot
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config   import Html_MGraph__Render__Config
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config   import Enum__Html_Render__Preset
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors   import Enum__Html_Render__Color_Scheme
from tests.unit.service.html_graph.test_Html_MGraph                                 import SIMPLE_HTML_DICT, NESTED_HTML_DICT


class test_Html_MGraph__Screenshot(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.html_mgraph_simple = Html_MGraph.from_html_dict(SIMPLE_HTML_DICT)
        cls.html_mgraph_nested = Html_MGraph.from_html_dict(NESTED_HTML_DICT)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                 # Test auto-initialization
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            assert type(_)          is Html_MGraph__Screenshot
            assert base_classes(_)  == [Type_Safe, object]
            assert type(_.config)   is Html_MGraph__Render__Config
            assert _.mgraph         is self.html_mgraph_simple.mgraph
            assert _.screenshot     is None                                                 # Not created until setup
            assert _.target_file    is None
            assert _.png_bytes      is None

    def test__init__without_mgraph(self):                                                   # Test initialization without mgraph
        with Html_MGraph__Screenshot() as _:
            assert type(_.mgraph) is MGraph

    # ═══════════════════════════════════════════════════════════════════════════════
    # Preset Configuration Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_set_preset__full_detail(self):                                                 # Test setting full detail preset
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.set_preset(Enum__Html_Render__Preset.FULL_DETAIL)
            assert result is _                                                              # Fluent interface
            assert _.config.preset == Enum__Html_Render__Preset.FULL_DETAIL

    def test_set_preset__structure_only(self):                                              # Test setting structure only preset
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.set_preset(Enum__Html_Render__Preset.STRUCTURE_ONLY)
            assert result is _
            assert _.config.preset == Enum__Html_Render__Preset.STRUCTURE_ONLY

    def test_set_preset__minimal(self):                                                     # Test setting minimal preset
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.set_preset(Enum__Html_Render__Preset.MINIMAL)
            assert result is _
            assert _.config.preset == Enum__Html_Render__Preset.MINIMAL

    # ═══════════════════════════════════════════════════════════════════════════════
    # Preset Shortcut Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_full_detail__shortcut(self):                                                   # Test full_detail shortcut method
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.full_detail()
            assert result is _
            assert _.config.preset == Enum__Html_Render__Preset.FULL_DETAIL

    def test_structure_only__shortcut(self):                                                # Test structure_only shortcut method
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.structure_only()
            assert result is _
            assert _.config.preset == Enum__Html_Render__Preset.STRUCTURE_ONLY

    def test_minimal__shortcut(self):                                                       # Test minimal shortcut method
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.minimal()
            assert result is _
            assert _.config.preset == Enum__Html_Render__Preset.MINIMAL

    # ═══════════════════════════════════════════════════════════════════════════════
    # Color Scheme Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_set_color_scheme__default(self):                                               # Test setting default color scheme
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.set_color_scheme(Enum__Html_Render__Color_Scheme.DEFAULT)
            assert result is _
            assert _.config.colors.scheme == Enum__Html_Render__Color_Scheme.DEFAULT

    def test_set_color_scheme__monochrome(self):                                            # Test setting monochrome color scheme
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.set_color_scheme(Enum__Html_Render__Color_Scheme.MONOCHROME)
            assert result is _
            assert _.config.colors.scheme == Enum__Html_Render__Color_Scheme.MONOCHROME

    def test_set_color_scheme__high_contrast(self):                                         # Test setting high contrast color scheme
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.set_color_scheme(Enum__Html_Render__Color_Scheme.HIGH_CONTRAST)
            assert result is _
            assert _.config.colors.scheme == Enum__Html_Render__Color_Scheme.HIGH_CONTRAST

    # ═══════════════════════════════════════════════════════════════════════════════
    # Color Scheme Shortcut Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_default_colors__shortcut(self):                                                # Test default_colors shortcut
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.default_colors()
            assert result is _
            assert _.config.colors.scheme == Enum__Html_Render__Color_Scheme.DEFAULT

    def test_monochrome__shortcut(self):                                                    # Test monochrome shortcut
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.monochrome()
            assert result is _
            assert _.config.colors.scheme == Enum__Html_Render__Color_Scheme.MONOCHROME

    def test_high_contrast__shortcut(self):                                                 # Test high_contrast shortcut
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.high_contrast()
            assert result is _
            assert _.config.colors.scheme == Enum__Html_Render__Color_Scheme.HIGH_CONTRAST

    # ═══════════════════════════════════════════════════════════════════════════════
    # Visibility Configuration Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_show_tags__enable(self):                                                       # Test enabling tag visibility
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            _.config.show_tag_nodes = False                                                 # Start disabled
            result = _.show_tags(True)
            assert result is _
            assert _.config.show_tag_nodes == True
            assert _.config.show_tag_edges == True

    def test_show_tags__disable(self):                                                      # Test disabling tag visibility
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.show_tags(False)
            assert result is _
            assert _.config.show_tag_nodes == False
            assert _.config.show_tag_edges == False

    def test_show_attrs__enable(self):                                                      # Test enabling attr visibility
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.show_attrs(True)
            assert result is _
            assert _.config.show_attr_nodes == True
            assert _.config.show_attr_edges == True

    def test_show_attrs__disable(self):                                                     # Test disabling attr visibility
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.show_attrs(False)
            assert result is _
            assert _.config.show_attr_nodes == False
            assert _.config.show_attr_edges == False

    def test_show_text__enable(self):                                                       # Test enabling text visibility
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.show_text(True)
            assert result is _
            assert _.config.show_text_nodes == True
            assert _.config.show_text_edges == True

    def test_show_text__disable(self):                                                      # Test disabling text visibility
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.show_text(False)
            assert result is _
            assert _.config.show_text_nodes == False
            assert _.config.show_text_edges == False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Style Configuration Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_set_max_text_length(self):                                                     # Test setting max text length
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.set_max_text_length(50)
            assert result is _
            assert _.config.labels.max_text_length == 50

    def test_set_element_shape(self):                                                       # Test setting element shape
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.set_element_shape('diamond')
            assert result is _
            assert _.config.element_shape == 'diamond'

    def test_set_tag_shape(self):                                                           # Test setting tag shape
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.set_tag_shape('circle')
            assert result is _
            assert _.config.tag_shape == 'circle'

    def test_set_attr_shape(self):                                                          # Test setting attr shape
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.set_attr_shape('box')
            assert result is _
            assert _.config.attr_shape == 'box'

    def test_set_text_shape(self):                                                          # Test setting text shape
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.set_text_shape('rectangle')
            assert result is _
            assert _.config.text_shape == 'rectangle'

    # ═══════════════════════════════════════════════════════════════════════════════
    # File Path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_set_target_file(self):                                                         # Test setting target file
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.set_target_file('/tmp/test.png')
            assert result is _
            assert _.target_file == '/tmp/test.png'

    def test_save_to(self):                                                                 # Test save_to method
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:
            result = _.save_to('/tmp/graph.png')
            assert result is _
            assert _.target_file == '/tmp/graph.png'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Fluent Interface Chain Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_fluent_chain(self):                                                            # Test method chaining works
        with Html_MGraph__Screenshot(mgraph=self.html_mgraph_simple.mgraph) as _:

            result = (_.full_detail()
                       .default_colors()
                       .show_tags(True)
                       .show_attrs(True)
                       .show_text(True)
                       .set_max_text_length(40)
                       .set_element_shape('box')
                       .save_to('/tmp/test.png'))
            assert result is _
            assert _.config.preset                 == Enum__Html_Render__Preset.FULL_DETAIL
            assert _.config.colors.scheme          == Enum__Html_Render__Color_Scheme.DEFAULT
            assert _.config.show_tag_nodes         == True
            assert _.config.labels.max_text_length == 40
            assert _.target_file                   == '/tmp/test.png'


