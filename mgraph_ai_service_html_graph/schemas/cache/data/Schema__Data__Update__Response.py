# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Data__Update__Response - Response from data update operation
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__Data__Update__Response(Type_Safe):                                  # Response from data update
    success : bool                                                                # Whether update succeeded
    updated : bool                                                                # Whether data was actually updated
