# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Phase E - Text Extractor
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                                   import TestCase
from Phase_E__Text_Extractor                                                                                    import Phase_E__Text_Extractor
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids            import Html__To__Html_Dict__With__Node_Ids
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse


class test_Phase_E__Text_Extractor(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.extractor = Phase_E__Text_Extractor()

    def test__init__(self):                                                     # Test auto-initialization
        with self.extractor as _:
            assert type(_).__name__ == 'Phase_E__Text_Extractor'

    def test_extract__simple_html(self):                                        # Extract from simple HTML
        with self.extractor as _:
            document   = self.create_document("<html><body><div>Hello</div></body></html>")
            text_nodes = _.extract(document)

            assert len(text_nodes)                 == 1

            node_id = list(text_nodes.keys())[0]
            assert str(text_nodes[node_id].text)      == 'Hello'
            assert str(text_nodes[node_id].parent_id) != ''

    def test_extract__multiple_text_nodes(self):                                # Extract multiple text nodes
        with self.extractor as _:
            document   = self.create_document("<html><body><div>Hello <b>World</b>*</div></body></html>")
            text_nodes = _.extract(document)

            assert len(text_nodes) == 3

            texts = [str(info.text) for info in text_nodes.values()]
            assert 'Hello ' in texts
            assert 'World'  in texts
            assert '*'      in texts

    def test_extract__empty_text_ignored(self):                                 # Whitespace-only ignored
        with self.extractor as _:
            document   = self.create_document("<div>   </div>")
            text_nodes = _.extract(document)

            assert len(text_nodes) == 0

    def test_extract__nested_structure(self):                                   # Nested structure
        with self.extractor as _:
            html       = "<html><body><div><p>First</p><p>Second</p></div></body></html>"
            document   = self.create_document(html)
            text_nodes = _.extract(document)

            assert len(text_nodes) == 2

            texts = [str(info.text) for info in text_nodes.values()]
            assert 'First'  in texts
            assert 'Second' in texts

    def test_extract__parent_id_captured(self):                                 # Parent ID captured correctly
        with self.extractor as _:
            document   = self.create_document("<html><body><div>Hello</div></body></html>")
            text_nodes = _.extract(document)

            node_id   = list(text_nodes.keys())[0]
            parent_id = str(text_nodes[node_id].parent_id)

            assert parent_id != ''
            assert parent_id != node_id

    def create_document(self, html: str):                                       # Helper to create document
        html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()
        return Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)

