from unittest                                                                     import TestCase
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors import Enum__Html_Render__Color_Scheme


class test_Enum__Html_Render__Color_Scheme(TestCase):

    def test_enum_values(self):                                                             # Test enum has expected values
        assert Enum__Html_Render__Color_Scheme.DEFAULT.value       == 'default'
        assert Enum__Html_Render__Color_Scheme.MONOCHROME.value    == 'monochrome'
        assert Enum__Html_Render__Color_Scheme.HIGH_CONTRAST.value == 'high_contrast'
