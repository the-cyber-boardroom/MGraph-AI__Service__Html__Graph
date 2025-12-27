import requests

from mgraph_ai_service_html_graph.fast_api.routes.Routes__Timestamps                        import Routes__Timestamps
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__QA__Traces__Create__Stats      import Schema__QA__Traces__Create__Stats
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Schemas    import Schema__Graph__From_Html__Request
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__Graph__With_Traces__Request    import Schema__Graph__With_Traces__Request
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__Trace_Config                   import Schema__Trace_Config
from mgraph_ai_service_html_graph.schemas.timestamps.enums.Enum__Trace_Output               import Enum__Trace_Output
from osbot_utils.helpers.duration.decorators.capture_duration                               import capture_duration
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path           import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id                           import Safe_Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                              import type_safe
from osbot_utils.utils.Files                                                                import path_combine, file_create
from osbot_utils.utils.Json                                                                 import json_to_str
from tests.unit.sample_html_files                                                           import generate__test_html, SIMPLE_HTML, HTML__WITH_SOME_TAGS, HTML__BOOTSTRAP_EXAMPLE

# FILE_NAME__FORMAT__SPEEDSCOPE        = '{type}__speedscope.json'
# FILE_NAME__FORMAT__RESPONSE__SUMMARY = '{type}__summary.json'
# FILE_NAME__FORMAT__RESPONSE__FULL    = '{type}__full.json'
# FILE_NAME__FORMAT__CREATE_STATS      = '{type}__create_stats.json'
FILE_NAME__FORMAT__SPEEDSCOPE        = 'speedscope_____{type}.json'
FILE_NAME__FORMAT__RESPONSE__SUMMARY = 'summary________{type}.json'
FILE_NAME__FORMAT__RESPONSE__FULL    = 'full_____________{type}.json'
FILE_NAME__FORMAT__CREATE_STATS      = 'create_stats_____{type}.json'


class QA_Create_Html_Transformations(Type_Safe):
    routes_timestamps : Routes__Timestamps
    transformation    : str                     = 'default'
    engine            : str                     = 'dot'
    target_folder     : Safe_Str__File__Path    = None
    trace_output      : Enum__Trace_Output      = Enum__Trace_Output.traces_only
    save_data         : bool                    = True

    def create__graph__from_html__request(self, html):
        graph__from_html_request = Schema__Graph__From_Html__Request(html           = html               ,
                                                                     transformation = self.transformation)
        return graph__from_html_request

    def create__trace_config(self):
        return Schema__Trace_Config(output=self.trace_output)

    def create__graph__with_traces__request(self, html):
        graph_request               = self.create__graph__from_html__request(html)
        trace_config                = self.create__trace_config()
        graph__with_traces__request = Schema__Graph__With_Traces__Request(graph_request= graph_request,
                                                                          trace_config  = trace_config)
        return graph__with_traces__request

    def from_html_with_traces__speedscope(self, html, html_type=None):
        request = self.create__graph__with_traces__request(html)
        response = self.routes_timestamps.from_html_with_traces_speedscope(engine         = self.engine        ,
                                                                           transformation = self.transformation,
                                                                           request        = request            )
        if self.save_data:
            self.save_speedscope_traces(traces    = response.traces,
                                        html_type = html_type     )
        return response

    def from_html_with_traces__full(self, html, html_type=None):
        request = self.create__graph__with_traces__request(html)
        response = self.routes_timestamps.from_html_with_traces_full(engine         = self.engine        ,
                                                                     transformation = self.transformation,
                                                                     request        = request            )
        if self.save_data:
            self.save_response__full(response    = response,
                                     html_type = html_type     )
        return response

    def from_html_with_traces__summary(self, html, html_type=None):
        request = self.create__graph__with_traces__request(html)
        response = self.routes_timestamps.from_html_with_traces_summary(engine         = self.engine        ,
                                                                        transformation = self.transformation,
                                                                        request        = request            )
        if self.save_data:
            self.save_response__summary(response    = response,
                                        html_type = html_type     )
        return response

    def save__create_stats(self, create_stats: Schema__QA__Traces__Create__Stats,html_type: Safe_Str__Text):
        file_name = FILE_NAME__FORMAT__CREATE_STATS.format(type = html_type)
        data      = json_to_str(create_stats.json())
        self.save_to_file(data, file_name)

    def save_response__full(self, response, html_type=None):
        file_name = FILE_NAME__FORMAT__RESPONSE__FULL.format(type = html_type)
        data      = json_to_str(response.json())
        self.save_to_file(data, file_name)

    def save_response__summary(self, response, html_type=None):
        file_name = FILE_NAME__FORMAT__RESPONSE__SUMMARY.format(type = html_type)
        data      = json_to_str(response.json())
        self.save_to_file(data, file_name)

    def save_speedscope_traces(self, traces, html_type=None):
        file_name = FILE_NAME__FORMAT__SPEEDSCOPE.format(type = html_type)
        self.save_to_file(traces, file_name)

    @type_safe
    def save_to_file(self, data: str, file_name: Safe_Id):
        if self.target_folder and file_name:
            target_file = path_combine(self.target_folder, file_name)
            file_create(target_file, data)

    # helper methods

    def create__for__html__with_size(self, size):
        html     = generate__test_html(element_count=size)
        html_type = f'with_size__{size}'
        create_stats = self.create__for__html(html=html, html_type=html_type)
        return create_stats

    def create__for__simple_html(self):
        html         = SIMPLE_HTML
        html_type    = 'simple-html'
        create_stats = self.create__for__html(html=html, html_type=html_type)
        return create_stats

    def create__for__html_with_some_tags(self):
        html         = HTML__WITH_SOME_TAGS
        html_type    = 'html-with-some-tags'
        create_stats = self.create__for__html(html=html, html_type=html_type)
        return create_stats

    def create__for__url(self, url):
        html         = requests.get(url).text
        html_type    = f'html-for-url__{url}'
        create_stats = self.create__for__html(html=html, html_type=html_type)
        return create_stats

    def create__for__html_bootstrap_example(self):
        html         = HTML__BOOTSTRAP_EXAMPLE
        html_type    = 'html-bootstrap-example'
        create_stats = self.create__for__html(html=html, html_type=html_type)
        return create_stats

    def create__for__html(self, html, html_type=None):
        with capture_duration()  as duration__speedscope:
            self.speedscope__for__html(html=html, html_type=html_type)
        with capture_duration()  as duration__summary:
            self.summary__for__html   (html=html, html_type=html_type)
        with capture_duration()  as duration__full:
            self.full__for__html      (html=html, html_type=html_type)

        create_stats = Schema__QA__Traces__Create__Stats(duration__full       = duration__full.seconds      ,
                                                         duration__speedscope = duration__speedscope.seconds,
                                                         duration__summary    = duration__summary.seconds   ,
                                                         html__type           = html_type                   ,
                                                         html__size           = len(html)                   )
        self.save__create_stats(create_stats= create_stats, html_type = html_type )
        return create_stats


    def full__for__html(self, html, html_type):
        response  = self.from_html_with_traces__full(html = html, html_type=html_type)
        return response

    def speedscope__for__html(self, html, html_type):
        response  = self.from_html_with_traces__speedscope(html = html, html_type=html_type)
        return response


    def summary__for__html(self, html, html_type):
        response  = self.from_html_with_traces__summary(html = html, html_type=html_type)
        return response

