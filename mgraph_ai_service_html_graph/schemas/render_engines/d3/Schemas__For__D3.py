# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - D3.js Export Response Schema
# Native format for D3.js force-directed visualization
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                import List, Optional
from osbot_utils.type_safe.Type_Safe                                       import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                      import Safe_Float
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Stats       import Schema__Graph__Stats


# ═══════════════════════════════════════════════════════════════════════════════
# D3.js Node Schema
# Matches D3 force simulation node format
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__D3__Node(Type_Safe):                                              # D3.js node format
    id         : str                                                            # Unique identifier (used by links)
    label      : str                  = ''                                      # Display label
    color      : str                  = '#E8E8E8'                               # Fill color
    fontColor  : str                  = '#333333'                               # Label color
    radius     : int                  = 20                                      # Node radius (for circular layouts)

    # Semantic metadata
    nodeType   : str                  = 'element'                               # element, tag, attr, text
    domPath    : str                  = ''                                      # DOM path
    category   : str                  = ''                                      # Tag category (structural, text, etc.)
    depth      : int                  = 0                                       # DOM depth
    value      : Optional[str]        = None                                    # Value for value nodes

    # D3 force simulation (optional initial positions)
    x          : Optional[float]      = None                                    # Initial x position
    y          : Optional[float]      = None                                    # Initial y position
    fx         : Optional[float]      = None                                    # Fixed x position
    fy         : Optional[float]      = None                                    # Fixed y position


# ═══════════════════════════════════════════════════════════════════════════════
# D3.js Link Schema
# D3 uses "links" (source/target) instead of "edges" (from/to)
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__D3__Link(Type_Safe):                                              # D3.js link format
    source     : str                                                            # Source node ID
    target     : str                                                            # Target node ID
    color      : str                  = '#888888'                               # Line color
    dashed     : bool                 = False                                   # Dashed line style
    width      : int                  = 1                                       # Line width

    # Semantic metadata
    predicate  : str                  = ''                                      # child, tag, attr, text
    position   : Optional[int]        = None                                    # Position among siblings


# ═══════════════════════════════════════════════════════════════════════════════
# D3.js Response Schema
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Graph__D3__Response(Type_Safe):                                   # Response schema for D3.js format
    nodes    : List[Schema__D3__Node]                                           # Node array
    links    : List[Schema__D3__Link]                                           # Link array (D3 convention)
    stats    : Schema__Graph__Stats                                             # Graph statistics
    duration : Safe_Float             = Safe_Float(0.0)                         # Processing time in seconds
    format   : str                    = 'd3'                                    # Export format identifier