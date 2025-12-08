from unittest                                                                        import TestCase
from mgraph_ai_service_html_graph.fast_api.routes.Routes__Html                       import Routes__Html, TAG__ROUTES_HTML, ROUTES_PATHS__HTML
from mgraph_ai_service_html_graph.schemas.routes.Schema__Html__From_Url__Request     import Schema__Html__From_Url__Request
from mgraph_ai_service_html_graph.schemas.routes.Schema__Html__From_Url__Response    import Schema__Html__From_Url__Response
from mgraph_ai_service_html_graph.service.html_url.Html__Url__Fetcher                import Html__Url__Fetcher


class test_Routes__Html(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.routes_html = Routes__Html()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                       # Test auto-initialization
        with Routes__Html() as _:
            assert type(_)              is Routes__Html
            assert _.tag                == TAG__ROUTES_HTML
            assert type(_.url_fetcher)  is Html__Url__Fetcher

    def test__routes_paths(self):                                                                 # Test route paths constant
        assert '/html/from/url' in ROUTES_PATHS__HTML
        assert len(ROUTES_PATHS__HTML) == 1

    # ═══════════════════════════════════════════════════════════════════════════════
    # from__url Tests (with mocking)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__from_url__success(self):                                                  # Test successful URL fetch

        request = Schema__Html__From_Url__Request(url='https://www.google.com')
        result  = self.routes_html.from__url(request)

        assert type(result)         is Schema__Html__From_Url__Response
        assert '<html'  in result.html
        assert 'Google' in result.html
        assert result.status_code   == 200

    def test__from_url__invalid_url(self):                                                        # Test invalid URL handling
        request = Schema__Html__From_Url__Request(url='http://not-a-valid-url')

        with self.assertRaises(ValueError):
            self.routes_html.from__url(request)

    # ═══════════════════════════════════════════════════════════════════════════════
    # setup_routes Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__setup_routes(self):                                                                 # Test setup_routes returns self
        routes = Routes__Html()
        result = routes.setup_routes()

        assert result is routes


