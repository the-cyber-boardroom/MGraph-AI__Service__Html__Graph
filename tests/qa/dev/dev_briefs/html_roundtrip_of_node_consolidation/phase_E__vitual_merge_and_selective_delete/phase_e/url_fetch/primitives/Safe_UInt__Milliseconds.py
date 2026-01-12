# ═══════════════════════════════════════════════════════════════════════════════
# Safe_UInt__Milliseconds - Duration in milliseconds
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.primitives.core.Safe_UInt import Safe_UInt


class Safe_UInt__Milliseconds(Safe_UInt):                           # Duration in milliseconds
    min_value = 0                                                   # Minimum (instant)
    max_value = 600_000                                             # Maximum 10 minutes
