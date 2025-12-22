from unittest                                                                 import TestCase
from osbot_utils.type_safe.Type_Safe                                          import Type_Safe
from osbot_utils.utils.Objects                                                import base_classes
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph             import Html_MGraph
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Screenshot import Html_MGraph__Screenshot
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config import Html_MGraph__Render__Config


class test_Html_MGraph__Screenshot(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simple_html  = '<div class="main" id="content">Hello World</div>'
        cls.html_mgraph  = Html_MGraph.from_html(cls.simple_html)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                               # Test auto-initialization
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            assert type(_)         is Html_MGraph__Screenshot
            assert base_classes(_) == [Type_Safe, object]
            assert _.html_mgraph   is self.html_mgraph
            assert type(_.config)  is Html_MGraph__Render__Config
            assert _.screenshot    is None
            assert _.target_file   is None
            assert _.png_bytes     is None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Setup Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__setup__creates_screenshot(self):                                            # Test setup creates screenshot instance
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            _.setup()
            assert _.screenshot is not None

    def test__setup__returns_self(self):                                                  # Test setup returns self for chaining
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            result = _.setup()
            assert result is _

    def test__setup__without_html_mgraph_raises(self):                                    # Test setup raises without html_mgraph
        with Html_MGraph__Screenshot(html_mgraph=None) as _:
            with self.assertRaises(ValueError) as context:
                _.setup()
            assert 'html_mgraph must be provided' in str(context.exception)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Preset Configuration Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__full_detail__returns_self(self):                                            # Test full_detail returns self
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            result = _.full_detail()
            assert result is _

    def test__structure_only__returns_self(self):                                         # Test structure_only returns self
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            result = _.structure_only()
            assert result is _

    def test__minimal__returns_self(self):                                                # Test minimal returns self
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            result = _.minimal()
            assert result is _

    # ═══════════════════════════════════════════════════════════════════════════════
    # Color Scheme Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__default_colors__returns_self(self):                                         # Test default_colors returns self
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            result = _.default_colors()
            assert result is _

    def test__monochrome__returns_self(self):                                             # Test monochrome returns self
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            result = _.monochrome()
            assert result is _

    def test__high_contrast__returns_self(self):                                          # Test high_contrast returns self
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            result = _.high_contrast()
            assert result is _

    # ═══════════════════════════════════════════════════════════════════════════════
    # Filtering Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__show_tags__returns_self(self):                                              # Test show_tags returns self
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            result = _.show_tags(True)
            assert result is _
            assert _.config.show_tag_nodes == True
            assert _.config.show_tag_edges == True

    def test__show_tags__false(self):                                                     # Test show_tags with False
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            _.show_tags(False)
            assert _.config.show_tag_nodes == False
            assert _.config.show_tag_edges == False

    def test__show_attrs__returns_self(self):                                             # Test show_attrs returns self
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            result = _.show_attrs(True)
            assert result is _
            assert _.config.show_attr_nodes == True
            assert _.config.show_attr_edges == True

    def test__show_text__returns_self(self):                                              # Test show_text returns self
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            result = _.show_text(True)
            assert result is _
            assert _.config.show_text_nodes == True
            assert _.config.show_text_edges == True

    # ═══════════════════════════════════════════════════════════════════════════════
    # Style Configuration Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__set_max_text_length__returns_self(self):                                    # Test set_max_text_length returns self
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            result = _.set_max_text_length(50)
            assert result is _
            assert _.config.labels.max_text_length == 50

    def test__set_element_shape__returns_self(self):                                      # Test set_element_shape returns self
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            result = _.set_element_shape('ellipse')
            assert result is _
            assert _.config.element_shape == 'ellipse'

    def test__set_tag_shape__returns_self(self):                                          # Test set_tag_shape returns self
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            result = _.set_tag_shape('diamond')
            assert result is _
            assert _.config.tag_shape == 'diamond'

    def test__set_attr_shape__returns_self(self):                                         # Test set_attr_shape returns self
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            result = _.set_attr_shape('hexagon')
            assert result is _
            assert _.config.attr_shape == 'hexagon'

    def test__set_text_shape__returns_self(self):                                         # Test set_text_shape returns self
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            result = _.set_text_shape('note')
            assert result is _
            assert _.config.text_shape == 'note'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Target File Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__set_target_file__returns_self(self):                                        # Test set_target_file returns self
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            result = _.set_target_file('/tmp/test.png')
            assert result is _
            assert _.target_file == '/tmp/test.png'

    def test__save_to__returns_self(self):                                                # Test save_to returns self
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            result = _.save_to('/tmp/test.png')
            assert result is _
            assert _.target_file == '/tmp/test.png'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Chaining Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__method_chaining(self):                                                      # Test method chaining works
        with Html_MGraph__Screenshot(html_mgraph=self.html_mgraph) as _:
            result = (_.full_detail()
                       .default_colors()
                       .show_tags(True)
                       .show_attrs(True)
                       .show_text(True)
                       .set_max_text_length(40)
                       .set_element_shape('box'))
            assert result is _