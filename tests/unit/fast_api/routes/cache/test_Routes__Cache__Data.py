# ═══════════════════════════════════════════════════════════════════════════════
# test_Routes__Cache__Data - Tests for cache data file routes
# Tests CRUD operations: list, get, store, update, exists, delete
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                    import TestCase
from fastapi                                                                                     import HTTPException
from mgraph_ai_service_cache_client.schemas.cache.data.Schema__Cache__Data__List__Response       import Schema__Cache__Data__List__Response
from mgraph_ai_service_cache_client.schemas.cache.data.Schema__Cache__Data__Store__Response      import Schema__Cache__Data__Store__Response
from mgraph_ai_service_html_graph.fast_api.routes.cache.Routes__Cache__Data                      import Routes__Cache__Data
from mgraph_ai_service_html_graph.fast_api.routes.cache.Routes__Cache__Data                      import TAG__ROUTES_CACHE_DATA
from mgraph_ai_service_html_graph.schemas.cache.data.Schema__Data__Delete__Response              import Schema__Data__Delete__Response
from mgraph_ai_service_html_graph.schemas.cache.data.Schema__Data__Exists__Response              import Schema__Data__Exists__Response
from mgraph_ai_service_html_graph.schemas.cache.data.Schema__Data__Paths__Response               import Schema__Data__Paths__Response
from mgraph_ai_service_html_graph.schemas.cache.data.Schema__Data__Store__Json__Request          import Schema__Data__Store__Json__Request
from mgraph_ai_service_html_graph.schemas.cache.data.Schema__Data__Store__String__Request        import Schema__Data__Store__String__Request
from mgraph_ai_service_html_graph.schemas.cache.data.Schema__Data__Update__Response              import Schema__Data__Update__Response
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Create__Request           import Schema__Entity__Create__Request
from mgraph_ai_service_html_graph.service.cache.Cache__Data__Service                             import Cache__Data__Service
from mgraph_ai_service_html_graph.service.cache.Cache__Entity__Service                           import Cache__Entity__Service
from osbot_fast_api.api.routes.Fast_API__Routes                                                  import Fast_API__Routes
from osbot_utils.type_safe.Type_Safe                                                             import Type_Safe
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List                            import Type_Safe__List
from osbot_utils.utils.Objects                                                                   import base_types
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                         import create_html_cache_client


class test_Routes__Cache__Data(TestCase):

    @classmethod
    def setUpClass(cls):                                                            # Shared test objects
        cls.cache_client, cls.cache_service = create_html_cache_client()
        cls.data_service   = Cache__Data__Service  (cache_client = cls.cache_client)
        cls.entity_service = Cache__Entity__Service(html_cache_client = cls.cache_client)
        cls.routes         = Routes__Cache__Data   (service      = cls.data_service)
        cls.namespace      = 'test-routes-cache-data'
        cls.cache_id       = cls.create_test_entity()

    @classmethod
    def create_test_entity(cls):                                                    # Create entity for tests
        request  = Schema__Entity__Create__Request(cache_key = 'test/data/entity')
        response = cls.entity_service.create(namespace = cls.namespace ,
                                             request   = request       )
        return response.cache_id

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                         # Test initialization
        with Routes__Cache__Data() as _:
            assert type(_)         is Routes__Cache__Data
            assert base_types(_)   == [Fast_API__Routes, Type_Safe, object]
            assert _.tag           == TAG__ROUTES_CACHE_DATA
            assert type(_.service) is Cache__Data__Service

    def test__init____with_service(self):                                           # Test with service
        with Routes__Cache__Data(service=self.data_service) as _:
            assert _.service is self.data_service

    # ═══════════════════════════════════════════════════════════════════════════════
    # Store String Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_data__store_string(self):                                              # Test store string
        request = Schema__Data__Store__String__Request(content = 'Hello, World!')

        response = self.routes.data__store_string(namespace    = self.namespace ,
                                                  cache_id     = self.cache_id  ,
                                                  data_key     = 'test'         ,
                                                  data_file_id = 'hello'        ,
                                                  request      = request        )

        assert type(response)    is Schema__Cache__Data__Store__Response
        assert response.data_key == 'test'
        assert response.data_type== 'string'

    def test_data__store_string__nested_path(self):                                 # Test store with nested data_key
        request = Schema__Data__Store__String__Request(content = 'Nested content')

        response = self.routes.data__store_string(namespace    = self.namespace          ,
                                                  cache_id     = self.cache_id           ,
                                                  data_key     = 'level1/level2/level3'  ,
                                                  data_file_id = 'deep'                  ,
                                                  request      = request                 )

        assert response.data_key == 'level1/level2/level3'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Store JSON Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_data__store_json(self):                                                # Test store JSON
        request = Schema__Data__Store__Json__Request(content = {'key': 'value', 'num': 42})

        response = self.routes.data__store_json(namespace    = self.namespace ,
                                                cache_id     = self.cache_id  ,
                                                data_key     = 'test'         ,
                                                data_file_id = 'config'       ,
                                                request      = request        )

        assert type(response)    is Schema__Cache__Data__Store__Response
        assert response.data_key == 'test'
        assert response.data_type== 'json'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get String Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_data__get_string(self):                                                # Test get string
        store_request = Schema__Data__Store__String__Request(content = 'Get me back!')
        self.routes.data__store_string(namespace    = self.namespace ,
                                       cache_id     = self.cache_id  ,
                                       data_key     = 'test'         ,
                                       data_file_id = 'get-string'   ,
                                       request      = store_request  )

        result = self.routes.data__get_string(namespace    = self.namespace ,
                                              cache_id     = self.cache_id  ,
                                              data_key     = 'test'         ,
                                              data_file_id = 'get-string'   )

        assert result == 'Get me back!'

    def test_data__get_string__not_found(self):                                     # Test get string not found
        with self.assertRaises(HTTPException) as context:
            self.routes.data__get_string(namespace    = self.namespace ,
                                         cache_id     = self.cache_id  ,
                                         data_key     = 'nonexistent'  ,
                                         data_file_id = 'missing'      )

        assert context.exception.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get JSON Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_data__get_json(self):                                                  # Test get JSON
        test_data = {'name': 'test', 'value': 123, 'nested': {'a': 1}}
        store_request = Schema__Data__Store__Json__Request(content = test_data)
        self.routes.data__store_json(namespace    = self.namespace ,
                                     cache_id     = self.cache_id  ,
                                     data_key     = 'test'         ,
                                     data_file_id = 'get-json'     ,
                                     request      = store_request  )

        result = self.routes.data__get_json(namespace    = self.namespace ,
                                            cache_id     = self.cache_id  ,
                                            data_key     = 'test'         ,
                                            data_file_id = 'get-json'     )

        assert result == test_data

    # ═══════════════════════════════════════════════════════════════════════════════
    # Update Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_data__update_string(self):                                             # Test update string
        store_request = Schema__Data__Store__String__Request(content = 'Original')
        self.routes.data__store_string(namespace    = self.namespace ,
                                       cache_id     = self.cache_id  ,
                                       data_key     = 'test'         ,
                                       data_file_id = 'update-str'   ,
                                       request      = store_request  )

        update_request  = Schema__Data__Store__String__Request(content = 'Updated')
        update_response = self.routes.data__update_string(namespace    = self.namespace  ,
                                                          cache_id     = self.cache_id   ,
                                                          data_key     = 'test'          ,
                                                          data_file_id = 'update-str'    ,
                                                          request      = update_request  )

        assert type(update_response) is Schema__Data__Update__Response
        assert update_response.success is True

        result = self.routes.data__get_string(namespace    = self.namespace ,
                                              cache_id     = self.cache_id  ,
                                              data_key     = 'test'         ,
                                              data_file_id = 'update-str'   )
        assert result == 'Updated'

    def test_data__update_json(self):                                               # Test update JSON
        store_request = Schema__Data__Store__Json__Request(content = {'v': 1})
        self.routes.data__store_json(namespace    = self.namespace ,
                                     cache_id     = self.cache_id  ,
                                     data_key     = 'test'         ,
                                     data_file_id = 'update-json'  ,
                                     request      = store_request  )

        update_request  = Schema__Data__Store__Json__Request(content = {'v': 2, 'new': True})
        update_response = self.routes.data__update_json(namespace    = self.namespace  ,
                                                        cache_id     = self.cache_id   ,
                                                        data_key     = 'test'          ,
                                                        data_file_id = 'update-json'   ,
                                                        request      = update_request  )

        assert update_response.success is True

        result = self.routes.data__get_json(namespace    = self.namespace ,
                                            cache_id     = self.cache_id  ,
                                            data_key     = 'test'         ,
                                            data_file_id = 'update-json'  )
        assert result == {'v': 2, 'new': True}

    # ═══════════════════════════════════════════════════════════════════════════════
    # Exists Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_data__exists__true(self):                                              # Test exists returns true
        store_request = Schema__Data__Store__String__Request(content = 'Exists test')
        self.routes.data__store_string(namespace    = self.namespace ,
                                       cache_id     = self.cache_id  ,
                                       data_key     = 'test'         ,
                                       data_file_id = 'exists-true'  ,
                                       request      = store_request  )

        result = self.routes.data__exists(namespace    = self.namespace ,
                                          cache_id     = self.cache_id  ,
                                          data_type    = 'string'       ,
                                          data_key     = 'test'         ,
                                          data_file_id = 'exists-true'  )

        assert type(result)  is Schema__Data__Exists__Response
        assert result.exists is True

    def test_data__exists__false(self):                                             # Test exists returns false
        result = self.routes.data__exists(namespace    = self.namespace ,
                                          cache_id     = self.cache_id  ,
                                          data_type    = 'string'       ,
                                          data_key     = 'nonexistent'  ,
                                          data_file_id = 'missing'      )

        assert result.exists is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Delete Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_data__delete(self):                                                    # Test delete
        store_request = Schema__Data__Store__String__Request(content = 'Delete me')
        self.routes.data__store_string(namespace    = self.namespace   ,
                                       cache_id     = self.cache_id    ,
                                       data_key     = 'test'           ,
                                       data_file_id = 'to-delete'      ,
                                       request      = store_request    )

        exists_before = self.routes.data__exists(namespace    = self.namespace ,
                                                 cache_id     = self.cache_id  ,
                                                 data_type    = 'string'       ,
                                                 data_key     = 'test'         ,
                                                 data_file_id = 'to-delete'    )
        assert exists_before.exists is True

        delete_response = self.routes.data__delete(namespace    = self.namespace ,
                                                   cache_id     = self.cache_id  ,
                                                   data_type    = 'string'       ,
                                                   data_key     = 'test'         ,
                                                   data_file_id = 'to-delete'    )

        assert type(delete_response)  is Schema__Data__Delete__Response
        assert delete_response.success is True
        assert delete_response.deleted is True

        exists_after = self.routes.data__exists(namespace    = self.namespace ,
                                                cache_id     = self.cache_id  ,
                                                data_type    = 'string'       ,
                                                data_key     = 'test'         ,
                                                data_file_id = 'to-delete'    )
        assert exists_after.exists is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # List Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_data__list(self):                                                      # Test list files
        response = self.routes.data__list(namespace = self.namespace ,
                                          cache_id  = self.cache_id  )

        assert type(response)       is Schema__Cache__Data__List__Response
        assert type(response.files) is Type_Safe__List

    def test_data__paths(self):                                                     # Test get paths
        response = self.routes.data__paths(namespace = self.namespace ,
                                           cache_id  = self.cache_id  )

        assert type(response) is Schema__Data__Paths__Response


    # ═══════════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_full_data_workflow(self):                                              # Test complete CRUD workflow
        data_key     = 'workflow'
        data_file_id = 'full-test'
        content      = 'Full workflow content'

        # Store
        store_response = self.routes.data__store_string(namespace    = self.namespace                                     ,
                                                        cache_id     = self.cache_id                                      ,
                                                        data_key     = data_key                                           ,
                                                        data_file_id = data_file_id                                       ,
                                                        request      = Schema__Data__Store__String__Request(content=content))

        assert type(store_response) is Schema__Cache__Data__Store__Response

        # Get
        get_result = self.routes.data__get_string(namespace    = self.namespace ,
                                                  cache_id     = self.cache_id  ,
                                                  data_key     = data_key       ,
                                                  data_file_id = data_file_id   )
        assert get_result == content

        # Update
        new_content     = 'Updated workflow content'
        update_response = self.routes.data__update_string(
            namespace    = self.namespace                                        ,
            cache_id     = self.cache_id                                         ,
            data_key     = data_key                                              ,
            data_file_id = data_file_id                                          ,
            request      = Schema__Data__Store__String__Request(content=new_content))

        assert update_response.success is True

        # Verify updated
        get_updated = self.routes.data__get_string(namespace    = self.namespace ,
                                                   cache_id     = self.cache_id  ,
                                                   data_key     = data_key       ,
                                                   data_file_id = data_file_id   )
        assert get_updated == new_content

        # Delete
        delete_response = self.routes.data__delete(namespace    = self.namespace ,
                                                   cache_id     = self.cache_id  ,
                                                   data_type    = 'string'       ,
                                                   data_key     = data_key       ,
                                                   data_file_id = data_file_id   )

        assert delete_response.deleted is True

        # Verify gone
        with self.assertRaises(HTTPException):
            self.routes.data__get_string(namespace    = self.namespace ,
                                         cache_id     = self.cache_id  ,
                                         data_key     = data_key       ,
                                         data_file_id = data_file_id   )
