# ═══════════════════════════════════════════════════════════════════════════════
# Enum__Storage_Mode - Storage backend mode enumeration
# ═══════════════════════════════════════════════════════════════════════════════

from enum                                                                       import Enum


class Enum__Storage_Mode(str, Enum):                                            # Storage backend mode
    LOCAL         = 'local'                                                     # Local disk storage
    MEMORY        = 'memory'                                                    # In-memory (tests)
    CACHE_SERVICE = 'cache_service'                                             # Remote cache service
