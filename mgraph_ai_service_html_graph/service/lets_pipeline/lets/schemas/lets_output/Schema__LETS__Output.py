# ═══════════════════════════════════════════════════════════════════════════════
# Schema__LETS__Output - Base output schema for LETS transformations
# All LETS-specific output schemas should inherit from this
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe

class Schema__LETS__Output(Type_Safe):                                           # Base LETS output schema
    pass                                                                         # Subclasses add fields