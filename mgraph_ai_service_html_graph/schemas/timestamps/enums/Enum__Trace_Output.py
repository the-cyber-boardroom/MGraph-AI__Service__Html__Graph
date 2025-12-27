"""
Enum for trace output destination
"""

from enum import Enum


class Enum__Trace_Output(str, Enum):
    traces_only   = 'traces_only'
    #response_only = 'response_only'                                              # Include traces in response only
    #external_only = 'external_only'                                              # Send to external service only (future)
    both          = 'both'                                                        # Both response and external (future)
