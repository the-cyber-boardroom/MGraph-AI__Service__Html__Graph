from unittest                                                                                import TestCase
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__D3 import MGraph__Engine__Config__D3
from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe


class test_MGraph__Engine__Config__D3(TestCase):

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test config initialization
        with MGraph__Engine__Config__D3() as _:
            assert type(_) is MGraph__Engine__Config__D3
            assert isinstance(_, Type_Safe)

    def test__default_values(self):                                              # Test default config values
        with MGraph__Engine__Config__D3() as _:
            assert _.charge_strength  == -300.0
            assert _.link_distance    == 100
            assert _.collision_radius == 30
            assert _.center_strength  == 0.1
            assert _.node_radius      == 20
            assert _.include_stats    == True
            assert _.include_types    == True
            assert _.max_label_len    == 50

    def test__custom_values(self):                                               # Test custom config values
        config = MGraph__Engine__Config__D3(
            charge_strength  = -500.0,
            link_distance    = 150   ,
            collision_radius = 50    ,
            node_radius      = 30    ,
        )
        assert config.charge_strength  == -500.0
        assert config.link_distance    == 150
        assert config.collision_radius == 50
        assert config.node_radius      == 30

