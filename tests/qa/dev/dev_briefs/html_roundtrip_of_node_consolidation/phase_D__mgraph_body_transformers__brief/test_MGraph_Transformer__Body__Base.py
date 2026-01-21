# ═══════════════════════════════════════════════════════════════════════════════
# Tests for MGraph_Transformer__Body transformers
# Part of Phase D: MGraph Body Transformers
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                       import TestCase
from MGraph_Transformer__Body__Base import MGraph_Transformer__Body__Base
from mgraph_db.mgraph.MGraph        import MGraph



class test_MGraph_Transformer__Body__Base(TestCase):
    """Tests for the base transformer class helper methods."""

    # ═══════════════════════════════════════════════════════════════════════════
    # get_node_tag Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_node_tag__simple_path(self):
        transformer = MGraph_Transformer__Body__Base()

        assert transformer.get_node_tag('body')         == 'body'
        assert transformer.get_node_tag('body.div')     == 'div'
        assert transformer.get_node_tag('body.div.p')   == 'p'
        assert transformer.get_node_tag('body.div.a')   == 'a'

    def test_get_node_tag__with_index(self):
        transformer = MGraph_Transformer__Body__Base()

        assert transformer.get_node_tag('body.div[0]')     == 'div'
        assert transformer.get_node_tag('body.div[0].p')   == 'p'
        assert transformer.get_node_tag('body.div[1].a')   == 'a'

    def test_get_node_tag__empty_path(self):
        transformer = MGraph_Transformer__Body__Base()

        assert transformer.get_node_tag('')     == ''
        assert transformer.get_node_tag(None)   == ''

    def test_get_node_tag__text_node(self):
        transformer = MGraph_Transformer__Body__Base()

        assert transformer.get_node_tag('text') == 'text'

    # ═══════════════════════════════════════════════════════════════════════════
    # Transform Not Implemented Test
    # ═══════════════════════════════════════════════════════════════════════════

    def test_transform__raises_not_implemented(self):
        transformer = MGraph_Transformer__Body__Base()
        mgraph      = MGraph()

        with self.assertRaises(NotImplementedError):
            transformer.transform(mgraph)








