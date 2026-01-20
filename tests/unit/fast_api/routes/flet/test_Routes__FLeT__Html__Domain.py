# ═══════════════════════════════════════════════════════════════════════════════
# test_Routes__FLeT__Html__Domain - Tests for domain-level HTML routes
# Tests orchestrated store/load operations with auto-entity creation
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                       import TestCase
from fastapi                                                                                        import HTTPException
from mgraph_ai_service_html_graph.fast_api.routes.flet.Routes__FLeT__Html__Domain                   import Routes__FLeT__Html__Domain
from mgraph_ai_service_html_graph.fast_api.routes.flet.Routes__FLeT__Html__Domain                   import TAG__ROUTES_FLET_HTML_DOMAIN
from osbot_fast_api.api.routes.Fast_API__Routes                                                     import Fast_API__Routes
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Load__Hash__Request             import Schema__Html__Load__Hash__Request
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Load__Id__Request               import Schema__Html__Load__Id__Request
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Load__Response                  import Schema__Html__Load__Response
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Store__Key__Request             import Schema__Html__Store__Key__Request
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Store__Raw__Request             import Schema__Html__Store__Raw__Request
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Store__Response                 import Schema__Html__Store__Response
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.FLeT__Html__Domain__Service            import FLeT__Html__Domain__Service
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                  import Cache_Id
from osbot_utils.utils.Objects                                                                      import base_types
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                            import create_html_cache_client


class test_Routes__FLeT__Html__Domain(TestCase):

    @classmethod
    def setUpClass(cls):                                                            # Shared test objects
        cls.cache_client, cls.cache_service = create_html_cache_client()
        cls.domain_service = FLeT__Html__Domain__Service(cache_client = cls.cache_client)
        cls.routes         = Routes__FLeT__Html__Domain (service      = cls.domain_service)
        cls.namespace      = 'test-routes-flet-html-domain'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                         # Test initialization
        with Routes__FLeT__Html__Domain() as _:
            assert type(_)       is Routes__FLeT__Html__Domain
            assert base_types(_) == [Fast_API__Routes, Type_Safe, object]
            assert _.tag         == TAG__ROUTES_FLET_HTML_DOMAIN
            assert _.service     is None

    def test__init____with_service(self):                                           # Test with service
        with Routes__FLeT__Html__Domain(service=self.domain_service) as _:
            assert _.service is self.domain_service

    # ═══════════════════════════════════════════════════════════════════════════════
    # Store Raw Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_store__raw(self):                                                      # Test store raw HTML
        html    = '<html><body><h1>Store Raw Test</h1></body></html>'
        request = Schema__Html__Store__Raw__Request(html = html)

        response = self.routes.store__raw(namespace = self.namespace ,
                                          request   = request        )

        assert type(response)          is Schema__Html__Store__Response
        assert response.success        is True
        assert response.cache_id       != ''
        assert response.cache_key      != ''
        assert response.cache_hash     != ''
        assert response.char_count     == len(html)

    def test_store__raw__creates_entity(self):                                      # Test entity is created
        html      = '<p>New entity test</p>'
        request   = Schema__Html__Store__Raw__Request(html = html)
        response  = self.routes.store__raw(namespace = self.namespace, request = request)
        response2 = self.routes.store__raw(namespace = self.namespace, request = request)

        assert response2.cache_id       == response.cache_id

    def test_store__raw__empty_html(self):                                          # Test with empty HTML
        request  = Schema__Html__Store__Raw__Request(html = '')
        response = self.routes.store__raw(namespace = self.namespace, request = request)

        assert response.success is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Store with Key Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_store__key(self):                                                      # Test store with explicit key
        html      = '<div>Store with key test</div>'
        cache_key = 'test/store/with-key'
        request   = Schema__Html__Store__Key__Request(html = html)

        response = self.routes.store__key(namespace = self.namespace ,
                                          cache_key = cache_key      ,
                                          request   = request        )

        assert response.success    is True
        assert response.cache_key  == cache_key
        assert response.char_count == len(html)

    def test_store__key__nested_path(self):                                         # Test with nested cache_key
        html      = '<span>Nested key test</span>'
        cache_key = 'level1/level2/level3/page'
        request   = Schema__Html__Store__Key__Request(html = html)

        response = self.routes.store__key(namespace = self.namespace ,
                                          cache_key = cache_key      ,
                                          request   = request        )

        assert response.success   is True
        assert response.cache_key == cache_key

    # ═══════════════════════════════════════════════════════════════════════════════
    # Load by ID Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_load__id(self):                                                        # Test load by cache_id
        html           = '<p>Load by ID test</p>'
        store_request  = Schema__Html__Store__Raw__Request(html = html)
        store_response = self.routes.store__raw(namespace = self.namespace ,
                                                request   = store_request  )
        cache_id = store_response.cache_id

        load_request  = Schema__Html__Load__Id__Request(cache_id = cache_id)
        load_response = self.routes.load__id(namespace = self.namespace ,
                                             request   = load_request   )

        assert type(load_response)    is Schema__Html__Load__Response
        assert load_response.success    is True
        assert load_response.found      is True
        assert load_response.html       == html
        assert load_response.cache_id   == cache_id
        assert load_response.char_count == len(html)

    def test_load__id__not_found(self):                                             # Test load non-existent ID
        load_request = Schema__Html__Load__Id__Request(cache_id = Cache_Id.new())

        with self.assertRaises(HTTPException) as context:
            self.routes.load__id(namespace = self.namespace ,
                                 request   = load_request   )

        assert context.exception.status_code == 500

    # ═══════════════════════════════════════════════════════════════════════════════
    # Load by Key Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_load__key(self):                                                       # Test load by cache_key
        html      = '<article>Load by key test</article>'
        cache_key = 'test/load/by-key-route'
        request   = Schema__Html__Store__Key__Request(html = html)

        self.routes.store__key(namespace = self.namespace ,
                               cache_key = cache_key      ,
                               request   = request        )

        load_response = self.routes.load__key(namespace = self.namespace ,
                                              cache_key = cache_key      )

        assert load_response.success   is True
        assert load_response.found     is True
        assert load_response.html      == html
        assert load_response.cache_key == cache_key

    def test_load__key__not_found(self):                                            # Test load non-existent key
        load_response = self.routes.load__key(namespace = self.namespace      ,
                                              cache_key = 'nonexistent/key/xyz')

        assert load_response.success is True
        assert load_response.found   is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Load by Hash Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_load__hash(self):                                                      # Test load by cache_hash
        html           = '<section>Load by hash test</section>'
        store_request  = Schema__Html__Store__Raw__Request(html = html)
        store_response = self.routes.store__raw(namespace = self.namespace ,
                                                request   = store_request  )
        cache_hash = store_response.cache_hash

        load_request  = Schema__Html__Load__Hash__Request(cache_hash = cache_hash)
        load_response = self.routes.load__hash(namespace = self.namespace ,
                                               request   = load_request   )

        assert load_response.success is True
        assert load_response.found   is True
        assert load_response.html    == html

    def test_load__hash__not_found(self):                                           # Test load non-existent hash
        load_request  = Schema__Html__Load__Hash__Request(cache_hash = 'aaaaa12345')
        load_response = self.routes.load__hash(namespace = self.namespace ,
                                               request   = load_request   )

        assert load_response.success is True
        assert load_response.found   is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Round-Trip Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_round_trip__store_and_load_by_id(self):                                # Test store → load by ID
        html = '<main>Round trip by ID</main>'

        store_response = self.routes.store__raw(namespace = self.namespace                        ,
                                                request   = Schema__Html__Store__Raw__Request(html=html))
        assert store_response.success is True

        load_response = self.routes.load__id(namespace = self.namespace                                       ,
                                             request   = Schema__Html__Load__Id__Request(cache_id=store_response.cache_id))
        assert load_response.html == html

    def test_round_trip__store_key_load_key(self):                                  # Test key → key round-trip
        html      = '<article>Article content</article>'
        cache_key = 'articles/2026/01/test-article'

        store_response = self.routes.store__key(namespace = self.namespace                        ,
                                                cache_key = cache_key                             ,
                                                request   = Schema__Html__Store__Key__Request(html=html))
        assert store_response.success is True

        load_response = self.routes.load__key(namespace = self.namespace ,
                                              cache_key = cache_key      )
        assert load_response.html == html

    def test_round_trip__store_raw_load_by_hash(self):                              # Test raw → hash round-trip
        html = '<section>Unique content for hash lookup</section>'

        store_response = self.routes.store__raw(namespace = self.namespace                        ,
                                                request   = Schema__Html__Store__Raw__Request(html=html))
        assert store_response.success is True
        cache_hash = store_response.cache_hash

        load_response = self.routes.load__hash(namespace = self.namespace                              ,
                                               request   = Schema__Html__Load__Hash__Request(cache_hash=cache_hash))
        assert load_response.found is True
        assert load_response.html  == html

    # ═══════════════════════════════════════════════════════════════════════════════
    # Entity Reuse Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_store_reuses_entity(self):                                             # Test entity reuse on duplicate key
        cache_key = 'test/entity-reuse'
        html_v1   = '<p>Version 1</p>'
        html_v2   = '<p>Version 2</p>'

        response1 = self.routes.store__key(namespace = self.namespace                        ,
                                           cache_key = cache_key                             ,
                                           request   = Schema__Html__Store__Key__Request(html=html_v1))

        response2 = self.routes.store__key(namespace = self.namespace                        ,
                                           cache_key = cache_key                             ,
                                           request   = Schema__Html__Store__Key__Request(html=html_v2))

        assert response2.cache_id       == response1.cache_id

        load_response = self.routes.load__key(namespace = self.namespace ,
                                              cache_key = cache_key      )
        assert load_response.html == html_v2

