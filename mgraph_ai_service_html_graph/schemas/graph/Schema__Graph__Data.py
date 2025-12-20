# ═══════════════════════════════════════════════════════════════════════════════
# Graph Data Schema (format-agnostic)
# ═══════════════════════════════════════════════════════════════════════════════
from typing                                                                 import List
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Node__Style  import Schema__Graph__Node, Schema__Graph__Edge
from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id           import Node_Id


class Schema__Graph__Data(Type_Safe):                                           # Complete graph data in format-agnostic structure
    nodes        : List[Schema__Graph__Node] = None                             # All nodes
    edges        : List[Schema__Graph__Edge] = None                             # All edges
    root_id      : Node_Id             = None                                   # Root node ID if hierarchical