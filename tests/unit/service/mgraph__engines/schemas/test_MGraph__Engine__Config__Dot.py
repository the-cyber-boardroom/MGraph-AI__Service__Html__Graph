from unittest                                                                                   import TestCase
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Dot   import MGraph__Engine__Config__Dot
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe


class test_MGraph__Engine__Config__Dot(TestCase):

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test config initialization
        with MGraph__Engine__Config__Dot() as _:
            assert type(_) is MGraph__Engine__Config__Dot
            assert isinstance(_, Type_Safe)

    def test__default_values(self):                                              # Test default config values
        with MGraph__Engine__Config__Dot() as _:
            assert _.rankdir        == 'TB'
            assert _.splines        == 'true'
            assert _.node_sep       == 0.5
            assert _.rank_sep       == 0.5
            assert _.nodesep        == 0.25
            assert _.font_name      == 'Arial'
            assert _.font_size      == 10
            assert _.node_shape     == 'box'
            assert _.node_style     == 'rounded,filled'
            assert _.node_fillcolor == '#e8f4f8'
            assert _.node_fontcolor == '#333333'
            assert _.edge_color     == '#666666'
            assert _.edge_arrowsize == 0.7
            assert _.bgcolor        == 'transparent'
            assert _.max_label_len  == 50
            assert _.show_node_ids  == False
            assert _.concentrate    == False

    def test__rankdir_literal(self):                                             # Test rankdir accepts valid values
        assert MGraph__Engine__Config__Dot(rankdir='TB').rankdir == 'TB'
        assert MGraph__Engine__Config__Dot(rankdir='LR').rankdir == 'LR'
        assert MGraph__Engine__Config__Dot(rankdir='BT').rankdir == 'BT'
        assert MGraph__Engine__Config__Dot(rankdir='RL').rankdir == 'RL'

    def test__splines_literal(self):                                             # Test splines accepts valid values
        assert MGraph__Engine__Config__Dot(splines='true').splines     == 'true'
        assert MGraph__Engine__Config__Dot(splines='false').splines    == 'false'
        assert MGraph__Engine__Config__Dot(splines='ortho').splines    == 'ortho'
        assert MGraph__Engine__Config__Dot(splines='polyline').splines == 'polyline'
        assert MGraph__Engine__Config__Dot(splines='curved').splines   == 'curved'

