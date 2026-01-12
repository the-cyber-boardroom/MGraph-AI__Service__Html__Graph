# ═══════════════════════════════════════════════════════════════════════════════
# Safe_UInt__Seconds - Duration in seconds
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.primitives.core.Safe_UInt import Safe_UInt


class Safe_UInt__Seconds(Safe_UInt):                                # Duration in seconds
    min_value = 0                                                   # Minimum (instant)
    max_value = 3600                                                # Maximum 1 hour
