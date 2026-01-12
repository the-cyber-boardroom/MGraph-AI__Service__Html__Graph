
from typing                                                                     import Dict, List
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text    import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id               import Node_Id


class Schema__Phase_E__Merged_Text_Info(Type_Safe):                                                # Info about merged text
    merged_text      : Safe_Str__Text                                                 # Combined text content
    source_node_ids  : List[Node_Id]