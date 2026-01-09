from unittest                                                   import TestCase
from mgraph_db.mgraph.MGraph                                    import MGraph
from mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value       import Schema__MGraph__Node__Value
from mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value__Data import Schema__MGraph__Node__Value__Data
from mgraph_db.mgraph.schemas.identifiers.Node_Path             import Node_Path
from MGraph_Transformer__Body__Merge_Text                       import MGraph_Transformer__Body__Merge_Text


class test_MGraph_Transformer__Body__Merge_Text(TestCase):
    """Tests for the merge text transformer."""

    def setUp(self):
        """Create a test MGraph with multiple text children."""
        self.mgraph = MGraph()

        # Create: div with two text children
        self.div_node = self.mgraph.edit().new_node(node_path=Node_Path('body.div'))

        text_data_1    = Schema__MGraph__Node__Value__Data(value='Hello ', value_type=str)
        self.text_node_1 = self.mgraph.edit().new_node(node_type=Schema__MGraph__Node__Value,
                                                        node_path=Node_Path('text'),
                                                        node_data=text_data_1)

        text_data_2    = Schema__MGraph__Node__Value__Data(value='World!', value_type=str)
        self.text_node_2 = self.mgraph.edit().new_node(node_type=Schema__MGraph__Node__Value,
                                                        node_path=Node_Path('text'),
                                                        node_data=text_data_2)

        # Create edges
        self.mgraph.edit().new_edge(from_node_id=self.div_node.node.data.node_id,
                                    to_node_id=self.text_node_1.node.data.node_id)
        self.mgraph.edit().new_edge(from_node_id=self.div_node.node.data.node_id,
                                    to_node_id=self.text_node_2.node.data.node_id)

    def test_find_parents_with_multiple_text_children(self):
        transformer = MGraph_Transformer__Body__Merge_Text()
        parents     = transformer.find_parents_with_multiple_text_children(self.mgraph)

        div_id = str(self.div_node.node.data.node_id)
        assert div_id in parents
        assert len(parents[div_id]) == 2

    def test_transform__merges_text_nodes(self):
        transformer = MGraph_Transformer__Body__Merge_Text()
        transformer.transform(self.mgraph)

        # Count text nodes
        text_count = 0
        for domain_node in self.mgraph.data().nodes():
            if str(domain_node.node.data.node_path) == 'text':
                text_count += 1

        assert text_count == 1  # Should now have only 1 text node

    def test_transform__returns_same_mgraph(self):
        transformer = MGraph_Transformer__Body__Merge_Text()
        result      = transformer.transform(self.mgraph)

        assert result is self.mgraph
