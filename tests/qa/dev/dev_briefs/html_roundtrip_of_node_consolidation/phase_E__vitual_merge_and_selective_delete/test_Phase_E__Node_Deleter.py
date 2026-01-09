# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Phase E - Node Deleter
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                                   import TestCase
from Phase_E__Node_Deleter                                                                                      import Phase_E__Node_Deleter
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids            import Html__To__Html_Dict__With__Node_Ids
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse


class test_Phase_E__Node_Deleter(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.deleter = Phase_E__Node_Deleter()

    def test__init__(self):                                                     # Test auto-initialization
        with self.deleter as _:
            assert type(_).__name__ == 'Phase_E__Node_Deleter'

    def test_delete__single_node(self):                                         # Delete single node
        with self.deleter as _:
            document   = self.create_document("<html><body><div><p>Keep</p><p>Delete</p></div></body></html>")
            body_graph = document.body_graph.mgraph
            p_nodes    = self.find_nodes_by_tag(body_graph, 'p')

            assert len(p_nodes) == 2

            deleted = _.delete(document, [p_nodes[1]])

            assert deleted == 1

            remaining_p = self.find_nodes_by_tag(body_graph, 'p')
            assert len(remaining_p) == 1

    def test_delete__returns_count(self):                                       # Delete returns correct count
        with self.deleter as _:
            document   = self.create_document("<html><body><div><p>A</p><p>B</p><p>C</p></div></body></html>")
            body_graph = document.body_graph.mgraph
            p_nodes    = self.find_nodes_by_tag(body_graph, 'p')

            deleted = _.delete(document, p_nodes[:2])

            assert deleted == 2

    def test_delete__nonexistent_node_safe(self):                               # Non-existent node doesn't error
        with self.deleter as _:
            document = self.create_document("<div>Hello</div>")
            deleted  = _.delete(document, ['nonexistent_id'])

            assert deleted == 0

    def test_delete__empty_list(self):                                          # Empty list returns 0
        with self.deleter as _:
            document = self.create_document("<div>Hello</div>")
            deleted  = _.delete(document, [])

            assert deleted == 0

    def create_document(self, html: str):                                       # Helper to create document

        html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()
        return Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)

    def find_nodes_by_tag(self, mgraph, target_tag: str) -> list:               # Find nodes by tag
        node_ids = []

        for domain_node in mgraph.data().nodes():
            node_path = str(domain_node.node.data.node_path or '')

            if node_path == 'text':
                continue

            if '.' in node_path:
                tag = node_path.split('.')[-1]
            else:
                tag = node_path

            if '[' in tag:                                                      # Handle indexed tags like 'p[0]', 'p[1]'
                tag = tag[:tag.index('[')]

            if tag.lower() == target_tag.lower():
                node_ids.append(str(domain_node.node.data.node_id))

        return node_ids

