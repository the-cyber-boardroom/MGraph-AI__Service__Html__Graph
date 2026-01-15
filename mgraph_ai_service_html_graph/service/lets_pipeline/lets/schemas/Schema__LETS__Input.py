# ═══════════════════════════════════════════════════════════════════════════════
# Schema__LETS__Input - Base input schema for LETS transformations
# All LETS-specific input schemas should inherit from this
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                             import Type_Safe


class Schema__LETS__Input(Type_Safe):                                            # Base LETS input schema
    pass                                                                         # Subclasses add fields


# ═══════════════════════════════════════════════════════════════════════════════
# Phase-Specific Input Schemas
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__LETS__Load__Input(Type_Safe):                                      # Load phase input
    pass


class Schema__LETS__Extract__Input(Type_Safe):                                   # Extract phase input
    pass


class Schema__LETS__Transform__Input(Type_Safe):                                 # Transform phase input
    pass


class Schema__LETS__Save__Input(Type_Safe):                                      # Save phase input
    pass
