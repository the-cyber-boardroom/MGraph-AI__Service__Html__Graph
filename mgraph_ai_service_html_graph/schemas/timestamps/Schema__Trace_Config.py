"""
Schema for trace configuration
"""

from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from mgraph_ai_service_html_graph.schemas.timestamps.enums.Enum__Trace_Output    import Enum__Trace_Output


class Schema__Trace_Config(Type_Safe):                                           # Configuration for trace capture
    output : Enum__Trace_Output = Enum__Trace_Output.both                        # Where to send trace data
