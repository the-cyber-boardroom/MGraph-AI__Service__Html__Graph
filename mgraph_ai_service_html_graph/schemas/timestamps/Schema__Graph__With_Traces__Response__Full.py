"""
Schema for graph response with full trace export
"""

from osbot_utils.type_safe.Type_Safe                                                     import Type_Safe
from osbot_utils.helpers.timestamp_capture.schemas.export.Schema__Export_Full            import Schema__Export_Full
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Schemas import Schema__Graph__Response__Base


class Schema__Graph__With_Traces__Response__Full(Type_Safe):                     # Response with full trace data
    graph  : Schema__Graph__Response__Base                                       # The graph output
    traces : Schema__Export_Full                                                 # Complete trace export
