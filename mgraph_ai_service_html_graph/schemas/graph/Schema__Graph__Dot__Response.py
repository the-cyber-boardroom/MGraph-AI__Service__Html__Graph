from osbot_utils.type_safe.primitives.core.Safe_Float                import Safe_Float
from osbot_utils.type_safe.primitives.core.Safe_UInt                 import Safe_UInt
from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Stats import Schema__Graph__Stats
from osbot_utils.type_safe.Type_Safe                                 import Type_Safe


class Schema__Graph__Dot__Response(Type_Safe):                                                    # Response schema for DOT format conversion
    dot_string     : str                                                                          # DOT language string for Graphviz
    dot_size       : Safe_UInt                                                                    # Size of DOT string
    duration       : Safe_Float                                                                   # How long it took to calculate the dot code
    stats          : Schema__Graph__Stats                                                         # Graph statistics
    transformation : str            # todo: use Type_Safe Primitive
