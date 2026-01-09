# ═══════════════════════════════════════════════════════════════════════════════
# Phase_E__Pipeline - Orchestrates full Phase E workflow
# Part of Phase E: Virtual Merge and Selective Delete
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import Dict, List
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html import Safe_Str__Html
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                             import Safe_Str__Text
from osbot_utils.type_safe.primitives.core.Safe_Int                             import Safe_Int
from Phase_E__Text_Extractor                                            import Phase_E__Text_Extractor
from Phase_E__Text_Extractor                                            import TextNodeInfo
from Phase_E__Virtual_Merger                                            import Phase_E__Virtual_Merger
from Phase_E__Virtual_Merger                                            import MergedTextInfo
from Phase_E__Decision_Engine__Base                                     import Phase_E__Decision_Engine__Base
from Phase_E__Decision_Engine__Base                                     import DecisionResult
from Phase_E__Decision_Engine__Hash_Based                               import Phase_E__Decision_Engine__Hash_Based
from Phase_E__Node_Deleter                                              import Phase_E__Node_Deleter


class Process_Result(Type_Safe):                                                # Full result with intermediate data
    html             : Safe_Str__Html                                           # Original HTML
    text_nodes       : Dict[str, TextNodeInfo]                                  # Extracted text nodes
    merged_texts     : Dict[str, MergedTextInfo]                                # Virtual merge results
    decisions        : Dict[str, DecisionResult]                                # Decision results
    parents_deleted  : List[str]                                                # Deleted parent_ids
    deleted_count    : Safe_Int                                                 # Number deleted
    clean_html       : Safe_Str__Html                                                 # Output HTML


class Phase_E__Pipeline(Type_Safe):                                             # Orchestrates full Phase E workflow

    decision_engine: Phase_E__Decision_Engine__Base = None                      # Pluggable decision engine

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.decision_engine is None:
            self.decision_engine = Phase_E__Decision_Engine__Hash_Based()

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Process Methods
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def process(self, html: str) -> str:                                        # Full workflow: HTML → process → clean HTML
        document   = self.html_to_document(html)
        document   = self.process_document(document)
        clean_html = self.document_to_html(document)

        return clean_html

    def process_document(self, document) -> object:                             # Process document in-place
        text_nodes   = Phase_E__Text_Extractor().extract(document)              # Step 1: Extract
        merged_texts = Phase_E__Virtual_Merger().merge(text_nodes, document)    # Step 2: Virtual merge
        decisions    = self.decision_engine.classify_all(merged_texts)          # Step 3: Decision

        parents_to_delete = self.decision_engine.get_parents_to_delete(decisions)  # Step 4: Collect

        Phase_E__Node_Deleter().delete(document, parents_to_delete)             # Step 5: Delete

        return document

    # ═══════════════════════════════════════════════════════════════════════════
    # Process with Details (for debugging/inspection)
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def process_with_details(self, html: str) -> Process_Result:                 # Full workflow with intermediate results
        document     = self.html_to_document(html)

        text_nodes   = Phase_E__Text_Extractor().extract(document)              # Step 1
        merged_texts = Phase_E__Virtual_Merger().merge(text_nodes, document)    # Step 2
        decisions    = self.decision_engine.classify_all(merged_texts)          # Step 3

        parents_to_delete = self.decision_engine.get_parents_to_delete(decisions)  # Step 4

        deleted_count = Phase_E__Node_Deleter().delete(document, parents_to_delete)  # Step 5

        clean_html = self.document_to_html(document)                            # Step 6

        return Process_Result(html            = html,
                              text_nodes      = text_nodes,
                              merged_texts    = merged_texts,
                              decisions       = decisions,
                              parents_deleted = parents_to_delete,
                              deleted_count   = deleted_count,
                              clean_html      = clean_html)

    # ═══════════════════════════════════════════════════════════════════════════
    # Conversion Helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def html_to_document(self, html: str):                                      # Convert HTML to document using Phase A + B
        from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids            import Html__To__Html_Dict__With__Node_Ids
        from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse

        html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()
        document  = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)

        return document

    def document_to_html(self, document) -> str:                                # Convert document back to HTML
        from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html import Html_MGraph__Document__To__Html

        return Html_MGraph__Document__To__Html().convert(document)