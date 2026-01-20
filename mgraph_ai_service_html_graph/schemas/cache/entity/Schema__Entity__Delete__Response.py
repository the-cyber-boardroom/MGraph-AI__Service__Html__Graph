# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Entity__Delete__Response - Response from entity deletion
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__Entity__Delete__Response(Type_Safe):                                # Response from entity deletion
    success : bool                                                                # Whether deletion succeeded
    deleted : bool                                                                # Whether entity was actually deleted
