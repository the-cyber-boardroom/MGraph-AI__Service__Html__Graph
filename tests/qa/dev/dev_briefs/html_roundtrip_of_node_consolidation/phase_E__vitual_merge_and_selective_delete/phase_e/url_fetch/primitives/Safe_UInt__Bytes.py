# ═══════════════════════════════════════════════════════════════════════════════
# Safe_UInt__Bytes - Content length in bytes
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.primitives.core.Safe_UInt import Safe_UInt


class Safe_UInt__Bytes(Safe_UInt):                                  # Size in bytes
    min_value = 0                                                   # Minimum (empty)
    max_value = 100_000_000                                         # Maximum 100MB
