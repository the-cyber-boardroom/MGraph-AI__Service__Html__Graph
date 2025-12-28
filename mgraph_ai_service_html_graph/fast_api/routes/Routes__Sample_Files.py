from osbot_fast_api.api.routes.Fast_API__Routes                                     import Fast_API__Routes
from mgraph_ai_service_html_graph.utils.testing.sample_html_files                   import generate__test_html, Enum__Sample__Html__File__Name, html_test_files
from osbot_utils.helpers.duration.decorators.capture_duration                       import capture_duration
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                               import Safe_Float
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id     import Safe_Str__Id
from osbot_utils.type_safe.primitives.domains.numerical.safe_int.Safe_Int__Positive import Safe_Int__Positive
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html           import Safe_Str__Html

TAG__ROUTES_SAMPLES = 'samples'
ROUTES_PATHS__SAMPLES = [f'/{TAG__ROUTES_SAMPLES}/html/with/size/{{element_count}}',
                        f'/{TAG__ROUTES_SAMPLES}/html/with/name/{{file_name}}'    ]

class Schema__Sample__Html__File(Type_Safe):
    duration       : Safe_Float
    html           : Safe_Str__Html
    html_size      : Safe_Int__Positive

class Schema__Sample__Html__File__With_Size(Schema__Sample__Html__File):
    requested_size : Safe_Int__Positive

class Schema__Sample__Html__File__With_Name(Schema__Sample__Html__File):
    file_name : Safe_Str__Id


class Routes__Samples_Files(Fast_API__Routes):
    tag =  TAG__ROUTES_SAMPLES

    def html__with__size__element_count(self,
                                        element_count: Safe_Int__Positive
                                   ) -> Schema__Sample__Html__File__With_Size:
        with capture_duration() as duration:
            html = generate__test_html(element_count)
        kwargs = dict(duration       = duration.seconds,
                      html           = html            ,
                      html_size      = len(html)       ,
                      requested_size = element_count   )
        return Schema__Sample__Html__File__With_Size(**kwargs)

    def html__with__name__file_name(self, file_name: Enum__Sample__Html__File__Name=None):
        with capture_duration() as duration:
            html = html_test_files.get(file_name)

        kwargs = dict(duration       = duration.seconds,
                      html           = html            ,
                      html_size      = len(html)       ,
                      file_name      = file_name       )
        return Schema__Sample__Html__File__With_Name(**kwargs)

    def setup_routes(self):
        self.add_route_get(self.html__with__size__element_count)
        self.add_route_get(self.html__with__name__file_name)

