from osbot_utils.type_safe.primitives.core.Safe_UInt import Safe_UInt
from osbot_utils.type_safe.Type_Safe                 import Type_Safe


class Schema__Graph__Stats(Type_Safe):              # Graph statistics schema
    total_nodes   : Safe_UInt                       # Total number of nodes
    total_edges   : Safe_UInt                       # Total number of edges
    element_nodes : Safe_UInt                       # Number of HTML element nodes
    value_nodes   : Safe_UInt                       # Number of value nodes (tag, attr, text)
    tag_nodes     : Safe_UInt                       # Number of tag value nodes
    text_nodes    : Safe_UInt                       # Number of text value nodes
    attr_nodes    : Safe_UInt                       # Number of attribute value nodes