# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Phase E - Virtual Merger
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                   import TestCase

from Phase_E__Text_Extractor                                                     import Phase_E__Text_Extractor
from Phase_E__Virtual_Merger                                                      import Phase_E__Virtual_Merger
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids            import Html__To__Html_Dict__With__Node_Ids
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse

class test_Phase_E__Virtual_Merger(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.extractor = Phase_E__Text_Extractor()
        cls.merger    = Phase_E__Virtual_Merger()

    def test__init__(self):                                                     # Test auto-initialization
        with self.merger as _:
            assert type(_).__name__ == 'Phase_E__Virtual_Merger'

    def test_merge__single_parent(self):                                        # Merge under single parent
        with self.merger as _:
            document     = self.create_document("<html><body><div>Hello</div></body></html>")
            text_nodes   = self.extractor.extract(document)
            merged_texts = _.merge(text_nodes, document)

            assert len(merged_texts) == 1

            parent_id = list(merged_texts.keys())[0]
            assert str(merged_texts[parent_id].merged_text)     == 'Hello'
            assert len(merged_texts[parent_id].source_node_ids) == 1

    def test_merge__multiple_parents(self):                                     # Multiple parents get separate merges
        with self.merger as _:
            html         = "<html><body><div><p>First</p><p>Second</p></div></body></html>"
            document     = self.create_document(html)
            text_nodes   = self.extractor.extract(document)
            merged_texts = _.merge(text_nodes, document)

            assert len(merged_texts) == 2

            merged_values = [str(info.merged_text) for info in merged_texts.values()]
            assert 'First'  in merged_values
            assert 'Second' in merged_values

    def test_merge__preserves_source_node_ids(self):                            # Source node_ids preserved
        with self.merger as _:
            document     = self.create_document("<html><body><div>Hello</div></body></html>")
            text_nodes   = self.extractor.extract(document)
            merged_texts = _.merge(text_nodes, document)

            parent_id       = list(merged_texts.keys())[0]
            source_node_ids = merged_texts[parent_id].source_node_ids

            assert len(source_node_ids)    == 1
            assert source_node_ids[0] in text_nodes

    def create_document(self, html: str):                                       # Helper to create document

        html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()
        return Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)
