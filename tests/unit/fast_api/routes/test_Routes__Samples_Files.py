from unittest                                                           import TestCase
from osbot_fast_api.api.Fast_API                                        import Fast_API
from mgraph_ai_service_html_graph.fast_api.routes.Routes__Graph         import Routes__Graph
from mgraph_ai_service_html_graph.fast_api.routes.Routes__Sample_Files import Routes__Samples_Files, TAG__ROUTES_SAMPLES, Schema__Sample__Html__File, Schema__Sample__Html__File__With_Size, \
    Schema__Sample__Html__File__With_Name
from mgraph_ai_service_html_graph.utils.testing.sample_html_files import generate__test_html, Enum__Sample__Html__File__Name, NESTED_HTML
from osbot_utils.testing.__                                             import __

class test_Routes__Samples_Files(TestCase):
    @classmethod
    def setUpClass(cls):
        with Fast_API() as _:
            _.add_routes(Routes__Samples_Files)
            _.add_routes(Routes__Graph)
            _.setup()
            cls.client   = _.client()
            cls.fast_api = _

    def test_html__with__size__element_count(self):
        def create_for_size(size):
            path     = f'/{TAG__ROUTES_SAMPLES}/html/with/size/{size}'
            response = self.client.get(path)
            assert response.status_code == 200
            json_data = response.json()
            return Schema__Sample__Html__File__With_Size.from_json(json_data)

        data_size_1 = create_for_size(1)

        assert data_size_1.obj() == __(duration = 0.0,
                                      html     = '<html lang="en">\n'
                                                 '    <head><title>Scaled Test (1 elements)</title></head>\n'
                                                 '    <body class="container">\n'
                                                 '        <div class="items">        <div class="item item-0" '
                                                 'data-id="0" data-type="widget"><span class="label">Item '
                                                 '0</span></div></div>\n'
                                                 '    </body>\n'
                                                 '</html>',
                                      html_size      = 259,
                                      requested_size = 1  )

        assert create_for_size(2).obj() == __(duration=0.0,
                                               html='<html lang="en">\n'
                                                    '    <head><title>Scaled Test (2 elements)</title></head>\n'
                                                    '    <body class="container">\n'
                                                    '        <div class="items">        <div class="item item-0" '
                                                    'data-id="0" data-type="widget"><span class="label">Item '
                                                    '0</span></div>\n'
                                                    '        <div class="item item-1" data-id="1" data-type="widget"><span '
                                                    'class="label">Item 1</span></div></div>\n'
                                                    '    </body>\n'
                                                    '</html>',
                                               html_size=363,
                                               requested_size=2)

        assert create_for_size(10).obj() == __(duration=0.0,
                                               html=generate__test_html(10),
                                               html_size=1196,
                                               requested_size=10)

    def test_html__with__name__file_name(self):
        def get_file(file_name: Enum__Sample__Html__File__Name):
            path = f'/{TAG__ROUTES_SAMPLES}/html/with/name/{file_name.value}'
            print()
            print(path)
            response = self.client.get(path)
            assert response.status_code == 200
            return Schema__Sample__Html__File__With_Name.from_json(response.json())

        sample_html_file = get_file(Enum__Sample__Html__File__Name.SIMPLE_HTML)
        assert sample_html_file.obj() == __(duration = 0.0,
                                            html     = '<html><body><div class="main" id="content">Hello '
                                                       'World</div></body></html>',
                                            html_size = 74,
                                            file_name = 'simple-html')
        assert get_file(Enum__Sample__Html__File__Name.NESTED_HTML).obj() == __(duration   = 0.0         ,
                                                                                html       = NESTED_HTML ,
                                                                                html_size  = 148         ,
                                                                                file_name = 'nested-html')