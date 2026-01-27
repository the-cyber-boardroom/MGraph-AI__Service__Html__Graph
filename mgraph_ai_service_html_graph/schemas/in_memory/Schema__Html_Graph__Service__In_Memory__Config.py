# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html_Graph__Service__In_Memory__Config
# Configuration schema for in-memory Html Graph service instances
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe


class Schema__Html_Graph__Service__In_Memory__Config(Type_Safe):                # Config for in-memory Html Graph
    enable_api_key : bool = False                                               # Disable API key for testing
