"""
Schema for graph response with speedscope trace export
"""

from osbot_utils.type_safe.Type_Safe                                                     import Type_Safe
from osbot_utils.helpers.timestamp_capture.schemas.speedscope.Schema__Speedscope         import Schema__Speedscope
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Schemas import Schema__Graph__Response__Base


class Schema__Graph__With_Traces__Response__Speedscope(Type_Safe):               # Response with speedscope trace data
    graph  : Schema__Graph__Response__Base                                       # The graph output
    traces : str                                                                  # we can't return Schema__Speedscope due to need to have an $schema attribute
    #traces : Schema__Speedscope                                                  # Speedscope.app compatible format
