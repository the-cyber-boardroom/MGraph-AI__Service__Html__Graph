# todo: refactor these to separate classes

# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - vis.js Export Response Schema
# Native format for vis.js Network visualization
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                import List, Optional, Dict, Any
from osbot_utils.type_safe.Type_Safe                                       import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                      import Safe_Float
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Stats       import Schema__Graph__Stats


# ═══════════════════════════════════════════════════════════════════════════════
# vis.js Node Schema
# Matches vis.js DataSet node format: https://visjs.github.io/vis-network/docs/network/nodes.html
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__VisJs__Node__Color(Type_Safe):                                    # vis.js node color configuration
    background : str = '#E8E8E8'                                                # Node background color
    border     : str = '#CCCCCC'                                                # Node border color
    highlight  : Dict[str, str] = None                                          # Colors when highlighted


class Schema__VisJs__Node__Font(Type_Safe):                                     # vis.js node font configuration
    color : str = '#333333'                                                     # Font color
    size  : int = 12                                                            # Font size


class Schema__VisJs__Node(Type_Safe):                                           # vis.js node format
    id         : str                                                            # Unique identifier
    label      : str                  = ''                                      # Display label
    title      : str                  = ''                                      # Tooltip text
    shape      : str                  = 'box'                                   # Node shape
    color      : Schema__VisJs__Node__Color = None                              # Color configuration
    font       : Schema__VisJs__Node__Font  = None                              # Font configuration

    # Semantic metadata (custom properties for filtering/styling)
    nodeType   : str                  = 'element'                               # element, tag, attr, text
    domPath    : str                  = ''                                      # DOM path
    category   : str                  = ''                                      # Tag category
    depth      : int                  = 0                                       # DOM depth


# ═══════════════════════════════════════════════════════════════════════════════
# vis.js Edge Schema
# Matches vis.js DataSet edge format: https://visjs.github.io/vis-network/docs/network/edges.html
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__VisJs__Edge__Color(Type_Safe):                                    # vis.js edge color configuration
    color     : str = '#888888'                                                 # Edge color
    highlight : str = '#6366f1'                                                 # Color when highlighted


class Schema__VisJs__Edge(Type_Safe):                                           # vis.js edge format
    id         : str                                                            # Unique identifier (auto-generated if not provided)
    from_node  : str                  = ''                                      # Source node ID (renamed from 'from' which is Python keyword)
    to         : str                  = ''                                      # Target node ID
    dashes     : bool                 = False                                   # Dashed line style
    color      : Schema__VisJs__Edge__Color = None                              # Color configuration

    # Semantic metadata
    predicate  : str                  = ''                                      # child, tag, attr, text
    position   : Optional[int]        = None                                    # Position among siblings


# ═══════════════════════════════════════════════════════════════════════════════
# vis.js Response Schema
# ═══════════════════════════════════════════════════════════════════════════════

# class Schema__Graph__VisJs__Response(Type_Safe):                                # Response schema for vis.js format
#     nodes    : List[Schema__VisJs__Node]                                        # Node dataset
#     edges    : List[Schema__VisJs__Edge]                                        # Edge dataset
#     stats    : Schema__Graph__Stats                                             # Graph statistics
#     duration : Safe_Float             = Safe_Float(0.0)                         # Processing time in seconds
#     format   : str                    = 'visjs'                                 # Export format identifier