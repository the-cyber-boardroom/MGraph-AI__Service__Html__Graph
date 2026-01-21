# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Flow__Task - Single task entry from flow execution
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                     import Type_Safe
from osbot_utils.type_safe.primitives.Safe_Float                         import Safe_Float
from osbot_utils.type_safe.primitives.domains.text.safe_str.Safe_Str__Id import Safe_Str__Id


class Schema__Flow__Task(Type_Safe):                                              # Single task entry
    task_name : Safe_Str__Id                                                      # Task identifier
    duration  : Safe_Float                                                        # Task duration in seconds
