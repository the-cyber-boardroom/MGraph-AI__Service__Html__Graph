# ═══════════════════════════════════════════════════════════════════════════════
# Enum__Execution_Mode - Pipeline execution modes
# ═══════════════════════════════════════════════════════════════════════════════

from enum import Enum


class Enum__Execution_Mode(Enum):
    FULL      = 'full'                                              # First time: fetch → cache all layers
    CACHED    = 'cached'                                            # Second time: read from cache only
    SELECTIVE = 'selective'                                         # Choose which layers to process
