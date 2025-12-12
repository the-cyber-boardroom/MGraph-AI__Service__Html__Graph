# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Common Graph Schemas for Native Export Formats
# Shared data structures for vis.js, D3, Cytoscape, and Mermaid exports
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                          import Optional, List, Dict, Any
from osbot_utils.type_safe.Type_Safe                                 import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                import Safe_Float
from osbot_utils.type_safe.primitives.core.Safe_UInt                 import Safe_UInt
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id    import Safe_Id
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Stats import Schema__Graph__Stats


# ═══════════════════════════════════════════════════════════════════════════════
# Node Schemas
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Graph__Node__Style(Type_Safe):                                    # Visual styling for a node
    fill_color   : str = '#E8E8E8'                                              # Background color
    font_color   : str = '#333333'                                              # Text color
    border_color : str = '#CCCCCC'                                              # Border color
    shape        : str = 'box'                                                  # Shape type


class Schema__Graph__Node(Type_Safe):                                           # Base node schema for all export formats
    id           : str                                                          # Unique node identifier
    label        : str              = ''                                        # Display label
    node_type    : str              = 'element'                                 # Type: element, tag, attr, text
    dom_path     : str              = ''                                        # DOM path (e.g., "html.body.div")
    value        : Optional[str]    = None                                      # Value for value nodes
    depth        : Safe_UInt        = Safe_UInt(0)                              # DOM depth
    category     : str              = ''                                        # Tag category (structural, text, form, etc.)
    style        : Schema__Graph__Node__Style = None                            # Visual styling


# ═══════════════════════════════════════════════════════════════════════════════
# Edge Schemas
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Graph__Edge__Style(Type_Safe):                                    # Visual styling for an edge
    color        : str  = '#888888'                                             # Line color
    width        : int  = 1                                                     # Line width
    dashed       : bool = False                                                 # Dashed line style
    arrow        : bool = True                                                  # Show arrow


class Schema__Graph__Edge(Type_Safe):                                           # Base edge schema for all export formats
    id           : str                                                          # Unique edge identifier
    source       : str                                                          # Source node ID
    target       : str                                                          # Target node ID
    predicate    : str              = ''                                        # Semantic type: child, tag, attr, text
    position     : Optional[int]    = None                                      # Position among siblings
    style        : Schema__Graph__Edge__Style = None                            # Visual styling


# ═══════════════════════════════════════════════════════════════════════════════
# Graph Data Schema (format-agnostic)
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Graph__Data(Type_Safe):                                           # Complete graph data in format-agnostic structure
    nodes        : List[Schema__Graph__Node] = None                             # All nodes
    edges        : List[Schema__Graph__Edge] = None                             # All edges
    root_id      : Optional[str]             = None                             # Root node ID if hierarchical


# ═══════════════════════════════════════════════════════════════════════════════
# Base Response Schema
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Graph__Base__Response(Type_Safe):                                 # Base response schema for all export formats
    stats        : Schema__Graph__Stats                                         # Graph statistics
    duration     : Safe_Float        = Safe_Float(0.0)                          # Processing time in seconds
    format       : str               = ''                                       # Export format name
