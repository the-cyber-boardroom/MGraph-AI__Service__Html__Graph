# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Data__Exists__Response - Response from data existence check
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__Data__Exists__Response(Type_Safe):                                  # Response from existence check
    exists : bool                                                                 # Whether data file exists
