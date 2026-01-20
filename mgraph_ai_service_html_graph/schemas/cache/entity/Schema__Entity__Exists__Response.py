# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Entity__Exists__Response - Response from entity existence check
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__Entity__Exists__Response(Type_Safe):                                # Response from existence check
    exists : bool                                                                 # Whether entity exists
