from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Edge_Id                import Edge_Id
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from mgraph_ai_service_html_graph.schemas.graph.edges.Schema__Graph__Edge__Style import Schema__Graph__Edge__Style
from osbot_utils.type_safe.primitives.core.Safe_UInt                             import Safe_UInt

# todo: review this name so that It is not confusing with the other MGraph schemas
class Schema__Graph__Edge(Type_Safe):                                           # Base edge schema for all export formats
    id           : Edge_Id                                                      # Unique edge identifier
    source       : Node_Id                                                      # Source node ID
    target       : Node_Id                                                      # Target node ID
    predicate    : str              = ''                                        # todo: refactor to Type_Safe primitive |  Semantic type: child, tag, attr, text
    position     : Safe_UInt        = None                                      # Position among siblings
    style        : Schema__Graph__Edge__Style = None