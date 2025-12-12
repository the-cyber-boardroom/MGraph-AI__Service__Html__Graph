# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Mermaid Export Response Schema
# Native format for Mermaid.js visualization
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                       import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                      import Safe_Float
from osbot_utils.type_safe.primitives.core.Safe_UInt                       import Safe_UInt
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Stats       import Schema__Graph__Stats


# ═══════════════════════════════════════════════════════════════════════════════
# Mermaid Response Schema
# Mermaid uses a text-based DSL, so we just return the generated code
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Graph__Mermaid__Response(Type_Safe):                              # Response schema for Mermaid format
    mermaid      : str                                                          # Mermaid flowchart code
    mermaid_size : Safe_UInt          = Safe_UInt(0)                            # Size of Mermaid string in bytes
    stats        : Schema__Graph__Stats                                         # Graph statistics
    duration     : Safe_Float         = Safe_Float(0.0)                         # Processing time in seconds
    format       : str                = 'mermaid'                               # Export format identifier