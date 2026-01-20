# ═══════════════════════════════════════════════════════════════════════════════
# test_Routes__Cache__Entity - Tests for cache entity routes
# Tests CRUD operations: create, lookup, get, exists, delete
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                   import TestCase
from fastapi                                                                                    import HTTPException
from mgraph_ai_service_cache_client.schemas.cache.file.Schema__Cache__File__Metadata            import Schema__Cache__File__Metadata
from mgraph_ai_service_html_graph.fast_api.routes.cache.Routes__Cache__Entity                   import Routes__Cache__Entity
from mgraph_ai_service_html_graph.fast_api.routes.cache.Routes__Cache__Entity                   import TAG__ROUTES_CACHE_ENTITY
from osbot_fast_api.api.routes.Fast_API__Routes                                                 import Fast_API__Routes
from mgraph_ai_service_html_graph.service.cache.Cache__Entity__Service                          import Cache__Entity__Service
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                              import Cache_Id
from osbot_utils.utils.Objects                                                                  import base_types
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Create__Request          import Schema__Entity__Create__Request
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Create__Response         import Schema__Entity__Create__Response
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Delete__Response         import Schema__Entity__Delete__Response
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Exists__Response         import Schema__Entity__Exists__Response
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Lookup__Request          import Schema__Entity__Lookup__Request
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Lookup__Response         import Schema__Entity__Lookup__Response
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                        import create_html_cache_client


class test_Routes__Cache__Entity(TestCase):

    @classmethod
    def setUpClass(cls):                                                            # Shared test objects
        cls.cache_client, cls.cache_service = create_html_cache_client()
        cls.service   = Cache__Entity__Service(cache_client = cls.cache_client)
        cls.routes    = Routes__Cache__Entity (service      = cls.service     )
        cls.namespace = 'test-routes-cache-entity'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                         # Test initialization
        with Routes__Cache__Entity() as _:
            assert type(_)         is Routes__Cache__Entity
            assert base_types(_)   == [Fast_API__Routes, Type_Safe, object]
            assert _.tag           == TAG__ROUTES_CACHE_ENTITY
            assert type(_.service) is Cache__Entity__Service

    def test__init____with_service(self):                                           # Test with service
        with Routes__Cache__Entity(service=self.service) as _:
            assert _.service is self.service

    # ═══════════════════════════════════════════════════════════════════════════════
    # Create Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_entity__create(self):                                                  # Test entity creation
        request = Schema__Entity__Create__Request(cache_key = 'test/create/entity',
                                                  file_id   = 'root'              )

        response = self.routes.entity__create(namespace = self.namespace ,
                                              request   = request        )

        assert type(response)    is Schema__Entity__Create__Response
        assert response.success  is True
        assert response.cache_id != ''

    def test_entity__create__duplicate(self):                                       # Test duplicate returns existing
        cache_key = 'test/create/duplicate'
        request   = Schema__Entity__Create__Request(cache_key = cache_key ,
                                                    file_id   = 'root'    )

        response1 = self.routes.entity__create(namespace = self.namespace, request = request)
        response2 = self.routes.entity__create(namespace = self.namespace, request = request)

        assert response1.cache_id != response2.cache_id

    def test_entity__create__empty_cache_key(self):                                 # Test empty cache_key fails
        request = Schema__Entity__Create__Request(cache_key = '')

        response = self.routes.entity__create(namespace = self.namespace ,
                                              request   = request        )

        assert response.success is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Lookup Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_entity__lookup__by_cache_key(self):                                    # Test lookup by cache_key
        cache_key       = 'test/lookup/by-key'
        create_request  = Schema__Entity__Create__Request(cache_key = cache_key)
        create_response = self.routes.entity__create(namespace = self.namespace ,
                                                     request   = create_request )

        lookup_request  = Schema__Entity__Lookup__Request(cache_key = cache_key)
        lookup_response = self.routes.entity__lookup(namespace = self.namespace ,
                                                     request   = lookup_request )

        assert type(lookup_response)  is Schema__Entity__Lookup__Response
        assert lookup_response.success  is True
        assert lookup_response.found    is True
        assert lookup_response.cache_id == create_response.cache_id

    def test_entity__lookup__not_found(self):                                       # Test lookup not found
        lookup_request = Schema__Entity__Lookup__Request(cache_key = 'nonexistent/key/12345')

        lookup_response = self.routes.entity__lookup(namespace = self.namespace ,
                                                     request   = lookup_request )

        assert lookup_response.success  is True
        assert lookup_response.found    is False
        assert lookup_response.cache_id == ''

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_entity__get(self):                                                     # Test get entity
        create_request  = Schema__Entity__Create__Request(cache_key = 'test/get/entity')
        create_response = self.routes.entity__create(namespace = self.namespace ,
                                                     request   = create_request )
        cache_id = create_response.cache_id

        result = self.routes.entity__get(namespace = self.namespace ,
                                         cache_id  = cache_id       )

        assert type(result) is dict
        assert result == {'cache_key': 'test/get/entity'}

    def test_entity__get__not_found(self):                                          # Test get not found
        with self.assertRaises(HTTPException) as context:
            self.routes.entity__get(namespace = self.namespace        ,
                                    cache_id  = Cache_Id.new())

        assert context.exception.status_code == 404

    def test_entity__get_metadata(self):                                            # Test get metadata
        create_request  = Schema__Entity__Create__Request(cache_key = 'test/get/metadata')
        create_response = self.routes.entity__create(namespace = self.namespace ,
                                                     request   = create_request )
        cache_id = create_response.cache_id

        result = self.routes.entity__metadata(namespace = self.namespace ,
                                             cache_id  = cache_id       )

        assert type(result)         is Schema__Cache__File__Metadata
        assert result.data.cache_id == cache_id

    def test_entity__get_metadata__not_found(self):                                 # Test get metadata not found
        with self.assertRaises(HTTPException) as context:
            self.routes.entity__metadata(namespace = self.namespace        ,
                                         cache_id  = Cache_Id.new())

        assert context.exception.status_code == 404


    # ═══════════════════════════════════════════════════════════════════════════════
    # Exists Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_entity__exists__true(self):                                            # Test exists returns true
        create_request  = Schema__Entity__Create__Request(cache_key = 'test/exists/true')
        create_response = self.routes.entity__create(namespace = self.namespace ,
                                                     request   = create_request )
        cache_id = create_response.cache_id

        result = self.routes.entity__exists(namespace = self.namespace ,
                                            cache_id  = cache_id       )

        assert type(result)  is Schema__Entity__Exists__Response
        assert result.exists is True

    def test_entity__exists__false(self):                                           # Test exists returns false
        result = self.routes.entity__exists(namespace = self.namespace ,
                                            cache_id  = Cache_Id.new() )

        assert result.exists is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Delete Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_entity__delete(self):                                                  # Test delete entity
        create_request  = Schema__Entity__Create__Request(cache_key = 'test/delete/entity')
        create_response = self.routes.entity__create(namespace = self.namespace ,
                                                     request   = create_request )
        cache_id = create_response.cache_id

        exists_before = self.routes.entity__exists(namespace = self.namespace ,
                                                   cache_id  = cache_id       )
        assert exists_before.exists is True

        delete_response = self.routes.entity__delete(namespace = self.namespace ,
                                                     cache_id  = cache_id       )

        assert type(delete_response)  is Schema__Entity__Delete__Response
        assert delete_response.success is True
        assert delete_response.deleted is True

        exists_after = self.routes.entity__exists(namespace = self.namespace ,
                                                  cache_id  = cache_id       )
        assert exists_after.exists is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_full_entity_workflow(self):                                            # Test complete CRUD workflow
        cache_key = 'test/workflow/full'

        # Create
        create_request  = Schema__Entity__Create__Request(cache_key = cache_key)
        create_response = self.routes.entity__create(namespace = self.namespace ,
                                                     request   = create_request )

        assert create_response.success is True
        cache_id = create_response.cache_id

        # Lookup
        lookup_request  = Schema__Entity__Lookup__Request(cache_key = cache_key)
        lookup_response = self.routes.entity__lookup(namespace = self.namespace ,
                                                     request   = lookup_request )

        assert lookup_response.found    is True
        assert lookup_response.cache_id == cache_id

        # Get
        entity = self.routes.entity__get(namespace = self.namespace ,
                                         cache_id  = cache_id       )

        assert type(entity) is dict

        # Exists
        exists = self.routes.entity__exists(namespace = self.namespace ,
                                            cache_id  = cache_id       )

        assert exists.exists is True

        # Delete
        delete = self.routes.entity__delete(namespace = self.namespace ,
                                            cache_id  = cache_id       )

        assert delete.deleted is True

        # Verify gone
        exists_after = self.routes.entity__exists(namespace = self.namespace ,
                                                  cache_id  = cache_id       )

        assert exists_after.exists is False