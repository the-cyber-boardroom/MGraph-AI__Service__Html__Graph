from unittest import TestCase
from mgraph_db.mgraph.MGraph                                    import MGraph
from mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value       import Schema__MGraph__Node__Value
from mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value__Data import Schema__MGraph__Node__Value__Data
from mgraph_db.mgraph.schemas.identifiers.Node_Path             import Node_Path
from MGraph_Transformer__Body__Remove_Empty_Text                import MGraph_Transformer__Body__Remove_Empty_Text

class test_MGraph_Transformer__Body__Remove_Empty_Text(TestCase):
    """Tests for the remove empty text transformer."""

    def setUp(self):
        """Create a test MGraph with empty text nodes."""

        self.mgraph = MGraph()

        self.div_node = self.mgraph.edit().new_node(node_path=Node_Path('body.div'))

        # Create text nodes: one with content, one empty, one whitespace
        text_data_1 = Schema__MGraph__Node__Value__Data(value='Hello', value_type=str)
        self.text_content = self.mgraph.edit().new_node(node_type=Schema__MGraph__Node__Value,
                                                         node_path=Node_Path('text'),
                                                         node_data=text_data_1)

        text_data_2 = Schema__MGraph__Node__Value__Data(value='   ', value_type=str)
        self.text_whitespace = self.mgraph.edit().new_node(node_type=Schema__MGraph__Node__Value,
                                                            node_path=Node_Path('text'),
                                                            node_data=text_data_2)

        text_data_3 = Schema__MGraph__Node__Value__Data(value='', value_type=str)
        self.text_empty = self.mgraph.edit().new_node(node_type=Schema__MGraph__Node__Value,
                                                       node_path=Node_Path('text'),
                                                       node_data=text_data_3)

    def test_find_empty_text_nodes(self):
        transformer = MGraph_Transformer__Body__Remove_Empty_Text()
        empty_nodes = transformer.find_empty_text_nodes(self.mgraph)

        assert len(empty_nodes) == 2  # whitespace and empty

    def test_transform__removes_empty_nodes(self):

        transformer = MGraph_Transformer__Body__Remove_Empty_Text()
        transformer.transform(self.mgraph)

        # Count remaining text nodes
        text_count = 0
        for domain_node in self.mgraph.data().nodes():
            if str(domain_node.node.data.node_path) == 'text':
                text_count += 1

        assert text_count == 1  # Only "Hello" should remain
