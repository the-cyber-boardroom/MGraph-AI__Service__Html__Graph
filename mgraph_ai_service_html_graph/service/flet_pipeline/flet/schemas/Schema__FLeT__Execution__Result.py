from osbot_utils.type_safe.Type_Safe                  import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float import Safe_Float
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text import Safe_Str__Text


class Schema__FLeT__Execution__Result(Type_Safe):
    success      : bool
    duration     : Safe_Float
    flow_output  : Type_Safe
    message      : Safe_Str__Text