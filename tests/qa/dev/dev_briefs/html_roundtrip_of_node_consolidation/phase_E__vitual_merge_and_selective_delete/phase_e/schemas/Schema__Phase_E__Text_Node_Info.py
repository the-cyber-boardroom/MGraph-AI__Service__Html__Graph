from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text    import Safe_Str__Text


class Schema__Phase_E__Text_Node_Info(Type_Safe):                                                  # Info about a text node
    text      : Safe_Str__Text                                                        # Text content
    parent_id : Safe_Str__Text                                                        # Parent element's node_id