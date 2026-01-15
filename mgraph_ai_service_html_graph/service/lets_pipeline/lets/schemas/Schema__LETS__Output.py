# ═══════════════════════════════════════════════════════════════════════════════
# Schema__LETS__Output - Base output schema for LETS transformations
# All LETS-specific output schemas should inherit from this
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                             import Type_Safe


class Schema__LETS__Output(Type_Safe):                                           # Base LETS output schema
    pass                                                                         # Subclasses add fields


# ═══════════════════════════════════════════════════════════════════════════════
# Phase-Specific Output Schemas
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__LETS__Load__Output(Type_Safe):                                     # Load phase output
    pass


class Schema__LETS__Extract__Output(Type_Safe):                                  # Extract phase output
    pass


class Schema__LETS__Transform__Output(Type_Safe):                                # Transform phase output
    pass


class Schema__LETS__Save__Output(Type_Safe):                                     # Save phase output
    success : bool
