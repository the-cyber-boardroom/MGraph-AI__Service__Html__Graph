from unittest                                                                                   import TestCase
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transform__Semantic import Graph_Transform__Semantic
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                               import Html_MGraph


class test_Graph_Transform__Semantic__Utility_Methods(TestCase):         # Tests for the internal utility methods of the Semantic transformation.

    @classmethod
    def setUpClass(cls):
        cls.transformation = Graph_Transform__Semantic()

    def test___is_single_child_parent(self):
        html_mgraph = Html_MGraph.from_html('<div><p>Only child</p></div>')

        if html_mgraph.body_graph:
            # This tests the internal method
            mgraph = html_mgraph.body_graph.mgraph
            nodes  = mgraph.graph.model.data.nodes

            for node_id in nodes:
                result = self.transformation._is_single_child_parent(mgraph, node_id)
                assert type(result) is bool

    def test___get_incoming_edge_path(self):
        html_mgraph = Html_MGraph.from_html('<div><p>Content</p></div>')

        if html_mgraph.body_graph:
            mgraph = html_mgraph.body_graph.mgraph
            nodes  = mgraph.graph.model.data.nodes

            for node_id in list(nodes.keys())[:2]:
                result = self.transformation._get_incoming_edge_path(mgraph, node_id)
                # May be None for root or a path string
                assert result is None or type(result) is str

    def test___get_parent_nodes_with_text_children(self):
        html_mgraph = Html_MGraph.from_html('<div>Text here</div>')

        if html_mgraph.body_graph:
            result = self.transformation._get_parent_nodes_with_text_children(html_mgraph.body_graph.mgraph)

            assert type(result) is list

    def test___get_text_children_ordered(self):
        html_mgraph = Html_MGraph.from_html('<div>Hello World</div>')

        if html_mgraph.body_graph:
            mgraph = html_mgraph.body_graph.mgraph
            nodes  = mgraph.graph.model.data.nodes

            for node_id in list(nodes.keys())[:1]:
                result = self.transformation._get_text_children_ordered(mgraph, node_id)
                assert type(result) is list