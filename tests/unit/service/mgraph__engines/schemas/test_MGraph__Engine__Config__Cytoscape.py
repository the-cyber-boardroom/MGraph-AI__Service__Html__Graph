from unittest                                                                                       import TestCase
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Cytoscape import MGraph__Engine__Config__Cytoscape
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe


class test_MGraph__Engine__Config__Cytoscape(TestCase):

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test config initialization
        with MGraph__Engine__Config__Cytoscape() as _:
            assert type(_) is MGraph__Engine__Config__Cytoscape
            assert isinstance(_, Type_Safe)

    def test__default_values(self):                                              # Test default config values
        with MGraph__Engine__Config__Cytoscape() as _:
            assert _.layout_name       == 'dagre'
            assert _.layout_direction  == 'TB'
            assert _.node_width        == 100
            assert _.node_height       == 40
            assert _.node_shape        == 'roundrectangle'
            assert _.node_bg_color     == '#e8f4f8'
            assert _.node_border_color == '#666666'
            assert _.node_border_width == 1
            assert _.edge_color        == '#666666'
            assert _.edge_width        == 2
            assert _.edge_arrow_shape  == 'triangle'
            assert _.font_size         == 12
            assert _.max_label_len     == 50
            assert _.include_stats     == True
            assert _.include_style     == True

    def test__layout_direction_literal(self):                                    # Test direction accepts valid values
        assert MGraph__Engine__Config__Cytoscape(layout_direction='TB').layout_direction == 'TB'
        assert MGraph__Engine__Config__Cytoscape(layout_direction='LR').layout_direction == 'LR'
        assert MGraph__Engine__Config__Cytoscape(layout_direction='BT').layout_direction == 'BT'
        assert MGraph__Engine__Config__Cytoscape(layout_direction='RL').layout_direction == 'RL'

