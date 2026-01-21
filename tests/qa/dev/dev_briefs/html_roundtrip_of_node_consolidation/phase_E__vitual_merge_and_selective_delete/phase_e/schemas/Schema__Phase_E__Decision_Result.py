from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                             import Safe_Str__Text
from osbot_utils.type_safe.primitives.core.Safe_Float                           import Safe_Float


class Schema__Phase_E__Decision_Result(Type_Safe):                                                # Result of a keep/discard decision
    keep   : bool                                                               # True to keep, False to discard
    score  : Safe_Float                                                         # Confidence/relevance score (0.0 to 1.0)
    reason : Safe_Str__Text                                                           # Human-readable reason for decision
