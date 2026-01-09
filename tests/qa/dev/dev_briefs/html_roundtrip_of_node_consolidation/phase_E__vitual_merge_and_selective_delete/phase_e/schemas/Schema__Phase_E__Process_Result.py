from typing                                                                     import Dict, List
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html       import Safe_Str__Html
from osbot_utils.type_safe.primitives.core.Safe_Int                             import Safe_Int
from phase_e.core.Phase_E__Text_Extractor                                       import Schema__Phase_E__Text_Node_Info
from phase_e.core.Phase_E__Virtual_Merger                                       import Schema__Phase_E__Merged_Text_Info
from phase_e.decision.Phase_E__Decision_Engine__Base                            import Schema__Phase_E__Decision_Result


class Schema__Phase_E__Process_Result(Type_Safe):                                                # Full result with intermediate data
    html             : Safe_Str__Html                                           # Original HTML
    text_nodes       : Dict[str, Schema__Phase_E__Text_Node_Info]                                  # Extracted text nodes
    merged_texts     : Dict[str, Schema__Phase_E__Merged_Text_Info]                                # Virtual merge results
    decisions        : Dict[str, Schema__Phase_E__Decision_Result]                                # Decision results
    parents_deleted  : List[str]                                                # Deleted parent_ids
    deleted_count    : Safe_Int                                                 # Number deleted
    clean_html       : Safe_Str__Html                                                 # Output HTML
