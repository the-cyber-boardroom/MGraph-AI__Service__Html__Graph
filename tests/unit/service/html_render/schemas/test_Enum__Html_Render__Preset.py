from unittest                                                                     import TestCase
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config import Enum__Html_Render__Preset


class test_Enum__Html_Render__Preset(TestCase):

    def test_enum_values(self):                                                             # Test enum has expected values
        assert Enum__Html_Render__Preset.FULL_DETAIL.value    == 'full_detail'
        assert Enum__Html_Render__Preset.STRUCTURE_ONLY.value == 'structure_only'
        assert Enum__Html_Render__Preset.MINIMAL.value        == 'minimal'
