# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Data__Delete__Response - Response from data deletion
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__Data__Delete__Response(Type_Safe):                                  # Response from data deletion
    success : bool                                                                # Whether delete succeeded
    deleted : bool                                                                # Whether data was actually deleted
