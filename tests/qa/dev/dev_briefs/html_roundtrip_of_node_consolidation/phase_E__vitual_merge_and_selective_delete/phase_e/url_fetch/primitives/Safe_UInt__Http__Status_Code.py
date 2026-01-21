# ═══════════════════════════════════════════════════════════════════════════════
# Safe_UInt__Http__Status_Code - HTTP status code (100-599)
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.primitives.core.Safe_UInt import Safe_UInt


class Safe_UInt__Http__Status_Code(Safe_UInt):                      # HTTP status code
    min_value = 100                                                 # Minimum valid HTTP status
    max_value = 599                                                 # Maximum valid HTTP status
