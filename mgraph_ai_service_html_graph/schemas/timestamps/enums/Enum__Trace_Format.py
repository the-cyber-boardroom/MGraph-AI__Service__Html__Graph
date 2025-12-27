"""
Enum for trace export formats
"""

from enum import Enum


class Enum__Trace_Format(str, Enum):
    full       = 'full'                                                          # Complete export with all data
    summary    = 'summary'                                                        # Compact hotspot overview
    speedscope = 'speedscope'                                                     # speedscope.app compatible format
