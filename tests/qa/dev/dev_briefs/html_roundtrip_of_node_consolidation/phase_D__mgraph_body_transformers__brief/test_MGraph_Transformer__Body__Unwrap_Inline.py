from unittest import TestCase

from mgraph_db.mgraph.MGraph                                    import MGraph
from mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value       import Schema__MGraph__Node__Value
from mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value__Data import Schema__MGraph__Node__Value__Data
from mgraph_db.mgraph.schemas.identifiers.Node_Path             import Node_Path
from MGraph_Transformer__Body__Unwrap_Inline                    import MGraph_Transformer__Body__Unwrap_Inline

class test_MGraph_Transformer__Body__Unwrap_Inline(TestCase):
    """Tests for the unwrap inline transformer."""

    def setUp(self):
        """Create a test MGraph with inline elements."""


        self.mgraph = MGraph()

        # Create: body → div → b → text("bold")
        self.body_node = self.mgraph.edit().new_node(node_path=Node_Path('body'))
        self.div_node  = self.mgraph.edit().new_node(node_path=Node_Path('body.div'))
        self.b_node    = self.mgraph.edit().new_node(node_path=Node_Path('body.div.b'))

        text_data      = Schema__MGraph__Node__Value__Data(value='bold text', value_type=str)
        self.text_node = self.mgraph.edit().new_node(node_type=Schema__MGraph__Node__Value,
                                                      node_path=Node_Path('text'),
                                                      node_data=text_data)

        # Create edges
        self.mgraph.edit().new_edge(from_node_id=self.body_node.node.data.node_id,
                                    to_node_id=self.div_node.node.data.node_id)
        self.mgraph.edit().new_edge(from_node_id=self.div_node.node.data.node_id,
                                    to_node_id=self.b_node.node.data.node_id)
        self.mgraph.edit().new_edge(from_node_id=self.b_node.node.data.node_id,
                                    to_node_id=self.text_node.node.data.node_id)

    def test_find_inline_wrappers__finds_b_tag(self):
        transformer = MGraph_Transformer__Body__Unwrap_Inline()
        wrappers    = transformer.find_inline_wrappers(self.mgraph)

        b_node_id = str(self.b_node.node.data.node_id)
        assert b_node_id in wrappers

    def test_find_inline_wrappers__ignores_div(self):
        transformer = MGraph_Transformer__Body__Unwrap_Inline()
        wrappers    = transformer.find_inline_wrappers(self.mgraph)

        div_node_id = str(self.div_node.node.data.node_id)
        assert div_node_id not in wrappers

    def test_transform__removes_b_tag(self):
        transformer = MGraph_Transformer__Body__Unwrap_Inline()
        transformer.transform(self.mgraph)

        # b node should be gone
        b_node_id = str(self.b_node.node.data.node_id)

        found_b = False
        for domain_node in self.mgraph.data().nodes():
            if str(domain_node.node.data.node_id) == b_node_id:
                found_b = True

        assert found_b is False

    def test_transform__preserves_text(self):
        transformer = MGraph_Transformer__Body__Unwrap_Inline()
        transformer.transform(self.mgraph)

        # Text node should still exist
        text_node_id = str(self.text_node.node.data.node_id)

        found_text = False
        for domain_node in self.mgraph.data().nodes():
            if str(domain_node.node.data.node_id) == text_node_id:
                found_text = True

        assert found_text is True

    def test_transform__returns_same_mgraph(self):
        transformer = MGraph_Transformer__Body__Unwrap_Inline()
        result      = transformer.transform(self.mgraph)

        assert result is self.mgraph

    def test_custom_inline_tags(self):
        # Only unwrap 'span', not 'b'
        transformer = MGraph_Transformer__Body__Unwrap_Inline(inline_tags={'span'})
        wrappers    = transformer.find_inline_wrappers(self.mgraph)

        b_node_id = str(self.b_node.node.data.node_id)
        assert b_node_id not in wrappers  # b is not in custom tags

