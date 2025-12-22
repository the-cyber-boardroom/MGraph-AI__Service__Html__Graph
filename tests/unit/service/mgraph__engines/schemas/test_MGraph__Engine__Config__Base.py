from unittest                                                                  import TestCase
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Base import MGraph__Engine__Config__Base
from osbot_utils.type_safe.Type_Safe                                           import Type_Safe
from osbot_utils.utils.Objects                                                 import base_classes


class test_MGraph__Engine__Config__Base(TestCase):

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test config base initialization
        with MGraph__Engine__Config__Base() as _:
            assert type(_)         is MGraph__Engine__Config__Base
            assert base_classes(_) == [Type_Safe, object]

    def test__inheritance(self):                                                 # Test config inherits Type_Safe
        config = MGraph__Engine__Config__Base()
        assert isinstance(config, Type_Safe)