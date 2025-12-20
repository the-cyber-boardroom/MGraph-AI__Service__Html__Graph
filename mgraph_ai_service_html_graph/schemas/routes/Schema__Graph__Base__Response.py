from osbot_utils.type_safe.Type_Safe                                 import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                import Safe_Float
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Stats import Schema__Graph__Stats


class Schema__Graph__Base__Response(Type_Safe):                                 # Base response schema for all export formats
    stats        : Schema__Graph__Stats                                         # Graph statistics
    duration     : Safe_Float                                                   # Processing time in seconds
    format       : str                                                          # todo: refactor to Type_Safe primitive or enum |  # Export format name