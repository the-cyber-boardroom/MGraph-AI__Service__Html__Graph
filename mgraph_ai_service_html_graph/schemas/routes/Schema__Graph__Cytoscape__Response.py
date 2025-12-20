# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Cytoscape.js Export Response Schema
# Native format for Cytoscape.js visualization
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                import List, Optional
from osbot_utils.type_safe.Type_Safe                                       import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                      import Safe_Float
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Stats       import Schema__Graph__Stats


# ═══════════════════════════════════════════════════════════════════════════════
# Cytoscape Node Data Schema
# Cytoscape uses { data: {...}, ... } wrapper around node data
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Cytoscape__Node__Data(Type_Safe):                                 # Data payload for Cytoscape node
    id         : str                                                            # Unique identifier
    label      : str                  = ''                                      # Display label
    color      : str                  = '#E8E8E8'                               # Fill color
    fontColor  : str                  = '#333333'                               # Label color
    borderColor: str                  = '#CCCCCC'                               # Border color

    # Semantic metadata
    nodeType   : str                  = 'element'                               # element, tag, attr, text
    domPath    : str                  = ''                                      # DOM path
    category   : str                  = ''                                      # Tag category
    depth      : int                  = 0                                       # DOM depth
    value      : Optional[str]        = None                                    # Value for value nodes


class Schema__Cytoscape__Node(Type_Safe):                                       # Cytoscape node element
    data       : Schema__Cytoscape__Node__Data                                  # Node data
    group      : str                  = 'nodes'                                 # Element group


# ═══════════════════════════════════════════════════════════════════════════════
# Cytoscape Edge Data Schema
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Cytoscape__Edge__Data(Type_Safe):                                 # Data payload for Cytoscape edge
    id         : str                                                            # Unique edge identifier
    source     : str                                                            # Source node ID
    target     : str                                                            # Target node ID
    color      : str                  = '#888888'                               # Line color
    dashed     : bool                 = False                                   # Dashed line style

    # Semantic metadata
    predicate  : str                  = ''                                      # child, tag, attr, text
    position   : Optional[int]        = None                                    # Position among siblings


class Schema__Cytoscape__Edge(Type_Safe):                                       # Cytoscape edge element
    data       : Schema__Cytoscape__Edge__Data                                  # Edge data
    group      : str                  = 'edges'                                 # Element group


# ═══════════════════════════════════════════════════════════════════════════════
# Cytoscape Elements Container
# Cytoscape uses a single "elements" array containing both nodes and edges
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Cytoscape__Elements(Type_Safe):                                   # Container for all Cytoscape elements
    nodes      : List[Schema__Cytoscape__Node]                                  # Node elements
    edges      : List[Schema__Cytoscape__Edge]                                  # Edge elements


# ═══════════════════════════════════════════════════════════════════════════════
# Cytoscape Response Schema
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Graph__Cytoscape__Response(Type_Safe):                            # Response schema for Cytoscape format
    elements : Schema__Cytoscape__Elements                                      # Cytoscape elements (nodes + edges)
    stats    : Schema__Graph__Stats                                             # Graph statistics
    duration : Safe_Float             = Safe_Float(0.0)                         # Processing time in seconds
    format   : str                    = 'cytoscape'                             # Export format identifier
