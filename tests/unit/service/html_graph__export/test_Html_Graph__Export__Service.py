from unittest                                                                            import TestCase
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Stats                     import Schema__Graph__Stats
from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Html__Request       import Schema__Graph__From_Html__Request
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service import Html_Graph__Export__Service
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config        import Enum__Html_Render__Preset
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors        import Enum__Html_Render__Color_Scheme


class test_Html_Graph__Export__Service(TestCase):                                                      # Tests for the underlying service

    @classmethod
    def setUpClass(cls):
        cls.service = Html_Graph__Export__Service()

    def test__html_to_mgraph(self):                                                               # Test HTML to MGraph conversion
        html      = '<div><p>Test</p></div>'
        html_mgraph = self.service.html_to_mgraph(html)

        assert html_mgraph is not None
        assert html_mgraph.mgraph is not None

    def test__create_config__defaults(self):                                                      # Test config creation with defaults
        request = Schema__Graph__From_Html__Request(html='<div></div>')
        config  = self.service.create_config(request)

        assert config.show_tag_nodes  == True
        assert config.show_attr_nodes == True
        assert config.show_text_nodes == True

    def test__create_config__custom(self):                                                        # Test config creation with custom values
        request = Schema__Graph__From_Html__Request(html            = '<div></div>'                        ,
                                                    preset          = Enum__Html_Render__Preset.MINIMAL    ,
                                                    show_tag_nodes  = False                                ,
                                                    show_attr_nodes = False                                ,
                                                    color_scheme    = Enum__Html_Render__Color_Scheme.MONOCHROME)
        config  = self.service.create_config(request)

        assert config.show_tag_nodes  == False
        assert config.show_attr_nodes == False

    def test__get_stats(self):                                                                    # Test stats generation
        html_mgraph = self.service.html_to_mgraph('<div><p>Hello</p></div>')
        stats       = self.service.get_stats(html_mgraph)

        assert type(stats) is Schema__Graph__Stats
        assert stats.total_nodes > 0