from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                                   import Safe_Float
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text            import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now        import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.numerical.safe_int.Safe_Int__Positive     import Safe_Int__Positive


class Schema__QA__Traces__Create__Stats(Type_Safe):
    duration__full       : Safe_Float
    duration__speedscope : Safe_Float
    duration__summary    : Safe_Float
    html__size           : Safe_Int__Positive
    html__type           : Safe_Str__Text
    timestamp            : Timestamp_Now