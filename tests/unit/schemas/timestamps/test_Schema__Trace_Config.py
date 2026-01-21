"""Tests for Schema__Trace_Config"""

from unittest                                                                       import TestCase
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__Trace_Config           import Schema__Trace_Config
from mgraph_ai_service_html_graph.schemas.timestamps.enums.Enum__Trace_Output       import Enum__Trace_Output
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.utils.Objects                                                      import base_classes


class test_Schema__Trace_Config(TestCase):

    def test__init__(self):                                                      # Test auto-initialization
        with Schema__Trace_Config() as _:
            assert type(_)         is Schema__Trace_Config
            assert base_classes(_) == [Type_Safe, object]
            assert _.output        == Enum__Trace_Output.both                   # Default value

    def test__init__with_values(self):                                           # Test initialization with values
        with Schema__Trace_Config(output=Enum__Trace_Output.both) as _:
            assert _.output == Enum__Trace_Output.both

    def test__init__with_string(self):                                           # Test enum auto-conversion from string
        with Schema__Trace_Config(output='traces_only') as _:
            assert _.output == Enum__Trace_Output.traces_only

    def test__json_roundtrip(self):                                              # Test JSON serialization
        with Schema__Trace_Config(output=Enum__Trace_Output.both) as _:
            json_str = _.json()
            restored = Schema__Trace_Config.from_json(json_str)
            assert restored.output == _.output
