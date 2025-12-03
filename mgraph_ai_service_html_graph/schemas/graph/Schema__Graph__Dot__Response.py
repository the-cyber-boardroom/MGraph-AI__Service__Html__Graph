from mgraph_ai_service_html_graph.schemas.graph.Schema__Graph__Stats import Schema__Graph__Stats
from osbot_utils.type_safe.Type_Safe                                 import Type_Safe



class Schema__Graph__Dot__Response(Type_Safe):                                                    # Response schema for DOT format conversion
    dot   : str                                                                                   # DOT language string for Graphviz
    stats : Schema__Graph__Stats                                                                  # Graph statistics