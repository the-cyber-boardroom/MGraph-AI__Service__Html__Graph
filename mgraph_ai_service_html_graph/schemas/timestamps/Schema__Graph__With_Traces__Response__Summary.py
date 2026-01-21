"""
Schema for graph response with summary trace export
"""

from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from osbot_utils.helpers.timestamp_capture.schemas.export.Schema__Export_Summary          import Schema__Export_Summary
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Schemas  import Schema__Graph__Response__Base
from mgraph_ai_service_html_graph.schemas.timestamps.enums.Schema__Trace__Response__Type  import Schema__Trace__Response__Type


class Schema__Graph__With_Traces__Response__Summary(Type_Safe):                  # Response with summary trace data
    graph         : Schema__Graph__Response__Base                                # The graph output
    response_type : Schema__Trace__Response__Type
    traces        : Schema__Export_Summary                                       # Compact hotspot summary
