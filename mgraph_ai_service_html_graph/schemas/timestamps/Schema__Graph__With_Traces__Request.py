"""
Schema for graph request with trace capture
"""

from osbot_utils.type_safe.Type_Safe                                                     import Type_Safe
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__Trace_Config                import Schema__Trace_Config
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Schemas import Schema__Graph__From_Html__Request


class Schema__Graph__With_Traces__Request(Type_Safe):                            # Request combining graph request with trace config
    graph_request : Schema__Graph__From_Html__Request                            # The graph conversion request
    trace_config  : Schema__Trace_Config                                         # Trace capture configuration
