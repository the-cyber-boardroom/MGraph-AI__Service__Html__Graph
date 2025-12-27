from unittest import TestCase

from mgraph_ai_service_html_graph.fast_api.routes.Routes__Timestamps import Routes__Timestamps
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Schemas                 import Schema__Graph__From_Html__Request, Schema__Graph__Response__Base, Schema__Graph__Dot__Response
#from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Html__Request                       import Schema__Graph__From_Html__Request
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__Graph__With_Traces__Request import Schema__Graph__With_Traces__Request
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__Trace_Config import Schema__Trace_Config
from mgraph_ai_service_html_graph.schemas.timestamps.enums.Enum__Trace_Output import Enum__Trace_Output
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service import Html_Graph__Export__Service
from osbot_utils.utils.Files import path_combine, file_create
from osbot_utils.utils.Json import json_to_file
from tests.unit.sample_html_files import SIMPLE_HTML, HTML__WITH_SOME_TAGS, HTML__BOOTSTRAP_EXAMPLE


class test_Routes__Timestamps__html_processing(TestCase):
    @classmethod
    def setUpClass(cls):                                                                             # Setup shared test objects
        cls.routes_timestamps = Routes__Timestamps()


    def test__simple_html(self):
        #html           =  SIMPLE_HTML
        #html = HTML__WITH_SOME_TAGS
        html  = HTML__BOOTSTRAP_EXAMPLE
        transformation = 'default'
        engine         = 'dot'
        request = Schema__Graph__With_Traces__Request(graph_request = Schema__Graph__From_Html__Request(html           = html           ,
                                                                                                        transformation = transformation),
                                                      trace_config  = Schema__Trace_Config(output=Enum__Trace_Output.both))

        response = self.routes_timestamps.from_html_with_traces_speedscope(engine         = engine        ,
                                                                           transformation = transformation,
                                                                           request        = request       )

        speedscope_traces = response.traces
        target_file = path_combine(__file__,'../_traces/speedscope-html.json')
        file_create(target_file, speedscope_traces)