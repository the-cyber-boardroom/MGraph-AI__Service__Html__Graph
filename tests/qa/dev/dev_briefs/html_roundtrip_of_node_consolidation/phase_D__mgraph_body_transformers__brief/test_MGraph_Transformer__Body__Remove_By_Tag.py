from unittest                                                       import TestCase
from mgraph_db.mgraph.MGraph                                        import MGraph
from mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value           import Schema__MGraph__Node__Value
from mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value__Data     import Schema__MGraph__Node__Value__Data
from MGraph_Transformer__Body__Remove_By_Tag                        import MGraph_Transformer__Body__Remove_By_Tag
from mgraph_db.mgraph.schemas.identifiers.Node_Path import Node_Path


class test_MGraph_Transformer__Body__Remove_By_Tag(TestCase):
    """Tests for the remove by tag transformer."""

    def setUp(self):
        """Create a test MGraph with elements to remove."""


        self.mgraph = MGraph()

        # Create: body → div, body → script → text
        self.body_node   = self.mgraph.edit().new_node(node_path=Node_Path('body'))
        self.div_node    = self.mgraph.edit().new_node(node_path=Node_Path('body.div'))
        self.script_node = self.mgraph.edit().new_node(node_path=Node_Path('body.script'))

        text_data = Schema__MGraph__Node__Value__Data(value='console.log("test")', value_type=str)
        self.script_text = self.mgraph.edit().new_node(node_type=Schema__MGraph__Node__Value,
                                                        node_path=Node_Path('text'),
                                                        node_data=text_data)

        self.mgraph.edit().new_edge(from_node_id=self.body_node.node.data.node_id,
                                    to_node_id=self.div_node.node.data.node_id)
        self.mgraph.edit().new_edge(from_node_id=self.body_node.node.data.node_id,
                                    to_node_id=self.script_node.node.data.node_id)
        self.mgraph.edit().new_edge(from_node_id=self.script_node.node.data.node_id,
                                    to_node_id=self.script_text.node.data.node_id)

    def test_find_nodes_to_remove(self):

        transformer = MGraph_Transformer__Body__Remove_By_Tag(tags_to_remove={'script'})
        to_remove   = transformer.find_nodes_to_remove(self.mgraph)

        script_id = str(self.script_node.node.data.node_id)
        assert script_id in to_remove

    def test_transform__removes_script_and_children(self):
        transformer = MGraph_Transformer__Body__Remove_By_Tag(tags_to_remove={'script'})
        transformer.transform(self.mgraph)

        # Script and its text should be gone
        script_id = str(self.script_node.node.data.node_id)
        text_id   = str(self.script_text.node.data.node_id)

        remaining_ids = {str(n.node.data.node_id) for n in self.mgraph.data().nodes()}

        assert script_id not in remaining_ids
        assert text_id   not in remaining_ids

    def test_transform__preserves_div(self):
        transformer = MGraph_Transformer__Body__Remove_By_Tag(tags_to_remove={'script'})
        transformer.transform(self.mgraph)

        div_id = str(self.div_node.node.data.node_id)
        remaining_ids = {str(n.node.data.node_id) for n in self.mgraph.data().nodes()}

        assert div_id in remaining_ids

