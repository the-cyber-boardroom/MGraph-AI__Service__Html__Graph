from unittest                                                                     import TestCase
from mgraph_ai_service_html_graph.schemas.routes.Schema__Html__From_Url__Request  import Schema__Html__From_Url__Request
from mgraph_ai_service_html_graph.schemas.routes.Schema__Html__From_Url__Response import Schema__Html__From_Url__Response
from mgraph_ai_service_html_graph.service.html_url.Html__Url__Fetcher             import Html__Url__Fetcher

URL__DOCS_DINISCRUZ_AI = "https://docs.diniscruz.ai/"

class test_Html__Url__Fetcher(TestCase):                                                          # Tests for the URL fetcher service

    @classmethod
    def setUpClass(cls):
        cls.fetcher = Html__Url__Fetcher()


    def test__fetch_html__success(self,):                                                # Test successful fetch


        request = Schema__Html__From_Url__Request(url=URL__DOCS_DINISCRUZ_AI)
        result  = self.fetcher.fetch_html(request)

        assert type(result)       is Schema__Html__From_Url__Response

        assert "Dinis Cruz"       in result.html
        assert result.url         == URL__DOCS_DINISCRUZ_AI
        assert result.status_code == 200
        assert 'text/html'        in result.content_type




    def test__fetch_html__connection_error(self):                                       # Test connection error handling

        request = Schema__Html__From_Url__Request(url='https://unreachable')

        with self.assertRaises(ValueError) as context:
            self.fetcher.fetch_html(request)

        assert 'Connection error' in str(context.exception)