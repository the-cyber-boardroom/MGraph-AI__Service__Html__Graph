# ═══════════════════════════════════════════════════════════════════════════════
# test_Routes__FLeT__Html__Execute - Tests for FLeT HTML execution routes
# Tests low-level FLeT execution: html-to-cache and html-from-cache
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                   import TestCase
from fastapi                                                                                    import HTTPException
from mgraph_ai_service_html_graph.fast_api.routes.flet.Routes__FLeT__Html__Execute              import Routes__FLeT__Html__Execute
from mgraph_ai_service_html_graph.fast_api.routes.flet.Routes__FLeT__Html__Execute              import TAG__ROUTES_FLET_HTML_EXECUTE
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Create__Request          import Schema__Entity__Create__Request
from mgraph_ai_service_html_graph.schemas.flet.html.Schema__FLeT__Html__From__Cache__Request    import Schema__FLeT__Html__From__Cache__Request
from mgraph_ai_service_html_graph.schemas.flet.html.Schema__FLeT__Html__From__Cache__Response   import Schema__FLeT__Html__From__Cache__Response
from mgraph_ai_service_html_graph.schemas.flet.html.Schema__FLeT__Html__To__Cache__Request      import Schema__FLeT__Html__To__Cache__Request
from mgraph_ai_service_html_graph.schemas.flet.html.Schema__FLeT__Html__To__Cache__Response     import Schema__FLeT__Html__To__Cache__Response
from mgraph_ai_service_html_graph.service.cache.Cache__Entity__Service                          import Cache__Entity__Service
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.FLeT__Html__Execute__Service       import FLeT__Html__Execute__Service
from osbot_fast_api.api.routes.Fast_API__Routes                                                 import Fast_API__Routes
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.utils.Objects                                                                  import base_types
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                        import create_html_cache_client


class test_Routes__FLeT__Html__Execute(TestCase):

    @classmethod
    def setUpClass(cls):                                                            # Shared test objects
        cls.html_cache_client, cls.cache_service = create_html_cache_client()
        cls.execute_service = FLeT__Html__Execute__Service(html_cache_client = cls.html_cache_client)
        cls.entity_service  = Cache__Entity__Service      (html_cache_client = cls.html_cache_client)
        cls.routes          = Routes__FLeT__Html__Execute (service      = cls.execute_service)
        cls.namespace       = 'test-routes-flet-html-execute'
        cls.cache_id        = cls.create_test_entity()

    @classmethod
    def create_test_entity(cls):                                                    # Create entity for tests
        request  = Schema__Entity__Create__Request(cache_key = 'test/flet/execute')
        response = cls.entity_service.create(namespace = cls.namespace ,
                                             request   = request       )
        return response.cache_id

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                         # Test initialization
        with Routes__FLeT__Html__Execute() as _:
            assert type(_)         is Routes__FLeT__Html__Execute
            assert base_types(_)   == [Fast_API__Routes, Type_Safe, object]
            assert _.tag           == TAG__ROUTES_FLET_HTML_EXECUTE
            assert type(_.service) is FLeT__Html__Execute__Service

    def test__init____with_service(self):                                           # Test with service
        with Routes__FLeT__Html__Execute(service=self.execute_service) as _:
            assert _.service is self.execute_service

    # ═══════════════════════════════════════════════════════════════════════════════
    # Html-To-Cache Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_html__to__cache(self):                                                 # Test store HTML
        html    = '<html><body><h1>Test</h1></body></html>'
        request = Schema__FLeT__Html__To__Cache__Request(html = html)

        response = self.routes.html__to__cache(namespace = self.namespace ,
                                               cache_id  = self.cache_id  ,
                                               request   = request        )

        assert type(response)        is Schema__FLeT__Html__To__Cache__Response
        assert response.success      is True
        assert response.cache_id     == self.cache_id
        assert response.char_count   == len(html)
        assert response.data_key     == 'html'
        assert response.data_file_id == 'raw'
        assert response.flow_saved   is True

    def test_html__to__cache__custom_location(self):                                # Test with custom data_key
        html    = '<div>Custom location test</div>'
        request = Schema__FLeT__Html__To__Cache__Request(html         = html    ,
                                                         data_key     = 'custom',
                                                         data_file_id = 'v1'    )

        response = self.routes.html__to__cache(namespace = self.namespace ,
                                               cache_id  = self.cache_id  ,
                                               request   = request        )

        assert response.success      is True
        assert response.data_key     == 'custom'
        assert response.data_file_id == 'v1'

    def test_html__to__cache__empty_html(self):                                     # Test with empty HTML
        request = Schema__FLeT__Html__To__Cache__Request(html = '')

        response = self.routes.html__to__cache(namespace = self.namespace ,
                                               cache_id  = self.cache_id  ,
                                               request   = request        )

        assert response.success is False

    def test_html__to__cache__entity_not_found(self):                               # Test with non-existent entity
        request = Schema__FLeT__Html__To__Cache__Request(html = '<p>test</p>')

        with self.assertRaises(HTTPException) as context:
            self.routes.html__to__cache(namespace = self.namespace        ,
                                        cache_id  = 'nonexistent-cache-id',
                                        request   = request               )

        assert context.exception.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════════
    # Html-From-Cache Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_html__from__cache(self):                                               # Test retrieve HTML
        html          = '<html><body><p>Retrieve me!</p></body></html>'
        store_request = Schema__FLeT__Html__To__Cache__Request(html = html)
        self.routes.html__to__cache(namespace = self.namespace ,
                                    cache_id  = self.cache_id  ,
                                    request   = store_request  )

        request  = Schema__FLeT__Html__From__Cache__Request()
        response = self.routes.html__from__cache(namespace = self.namespace ,
                                                 cache_id  = self.cache_id  ,
                                                 request   = request        )

        assert type(response)      is Schema__FLeT__Html__From__Cache__Response
        assert response.success    is True
        assert response.cache_id   == self.cache_id
        assert response.found      is True
        assert response.html       == html
        assert response.char_count == len(html)
        assert response.flow_saved is True

    def test_html__from__cache__custom_location(self):                              # Test retrieve from custom location
        html    = '<div>Custom retrieve test</div>'
        request = Schema__FLeT__Html__To__Cache__Request(html         = html      ,
                                                         data_key     = 'retrieve',
                                                         data_file_id = 'custom'  )
        self.routes.html__to__cache(namespace = self.namespace ,
                                    cache_id  = self.cache_id  ,
                                    request   = request        )

        load_request = Schema__FLeT__Html__From__Cache__Request(data_key     = 'retrieve',
                                                                 data_file_id = 'custom' )
        response     = self.routes.html__from__cache(namespace = self.namespace ,
                                                     cache_id  = self.cache_id  ,
                                                     request   = load_request   )

        assert response.success is True
        assert response.html    == html

    def test_html__from__cache__not_found(self):                                    # Test retrieve non-existent
        request  = Schema__FLeT__Html__From__Cache__Request(data_key     = 'nonexistent',
                                                            data_file_id = 'missing'    )
        response = self.routes.html__from__cache(namespace = self.namespace ,
                                                 cache_id  = self.cache_id  ,
                                                 request   = request        )

        assert response.success is True
        assert response.found   is False

    def test_html__from__cache__entity_not_found(self):                             # Test with non-existent entity
        request = Schema__FLeT__Html__From__Cache__Request()

        with self.assertRaises(HTTPException) as context:
            self.routes.html__from__cache(namespace = self.namespace        ,
                                          cache_id  = 'nonexistent-cache-id',
                                          request   = request               )

        assert context.exception.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════════
    # Round-Trip Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_round_trip__store_and_retrieve(self):                                  # Test complete round-trip
        entity_request  = Schema__Entity__Create__Request(cache_key = 'test/flet/roundtrip')
        entity_response = self.entity_service.create(namespace = self.namespace ,
                                                     request   = entity_request )
        cache_id = entity_response.cache_id

        original_html = '''<!DOCTYPE html>
<html>
<head><title>Round Trip Test</title></head>
<body>
    <h1>Hello World</h1>
    <p>This is a round-trip test.</p>
</body>
</html>'''

        store_request  = Schema__FLeT__Html__To__Cache__Request(html = original_html)
        store_response = self.routes.html__to__cache(namespace = self.namespace ,
                                                     cache_id  = cache_id       ,
                                                     request   = store_request  )

        assert store_response.success is True

        load_request  = Schema__FLeT__Html__From__Cache__Request()
        load_response = self.routes.html__from__cache(namespace = self.namespace ,
                                                      cache_id  = cache_id       ,
                                                      request   = load_request   )

        assert load_response.success is True
        assert load_response.found   is True
        assert load_response.html    == original_html

    def test_multiple_data_locations(self):                                         # Test storing at multiple locations
        entity_request  = Schema__Entity__Create__Request(cache_key = 'test/flet/multi')
        entity_response = self.entity_service.create(namespace = self.namespace ,
                                                     request   = entity_request )
        cache_id = entity_response.cache_id

        html_v1 = '<p>Version 1</p>'
        self.routes.html__to__cache(namespace = self.namespace                            ,
                                    cache_id  = cache_id                                  ,
                                    request   = Schema__FLeT__Html__To__Cache__Request(html=html_v1))

        html_v2 = '<p>Version 2</p>'
        self.routes.html__to__cache(namespace = self.namespace                                       ,
                                    cache_id  = cache_id                                             ,
                                    request   = Schema__FLeT__Html__To__Cache__Request(html         = html_v2,
                                                                                       data_key     = 'html' ,
                                                                                       data_file_id = 'v2'   ))

        response_v1 = self.routes.html__from__cache(namespace = self.namespace                        ,
                                                    cache_id  = cache_id                              ,
                                                    request   = Schema__FLeT__Html__From__Cache__Request())
        assert response_v1.html == html_v1

        response_v2 = self.routes.html__from__cache(namespace = self.namespace                              ,
                                                    cache_id  = cache_id                                    ,
                                                    request   = Schema__FLeT__Html__From__Cache__Request(
                                                                    data_key     = 'html',
                                                                    data_file_id = 'v2'  ))
        assert response_v2.html == html_v2
