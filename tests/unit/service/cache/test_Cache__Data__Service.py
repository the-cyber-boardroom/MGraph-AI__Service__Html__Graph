# ═══════════════════════════════════════════════════════════════════════════════
# Test__Cache__Data__Service - Tests for cache data file service
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                               import TestCase
from mgraph_ai_service_cache_client.client.cache_service.register_cache_service             import register_cache_service__in_memory
from mgraph_ai_service_cache_client.schemas.cache.data.Schema__Cache__Data__List__Response  import Schema__Cache__Data__List__Response
from mgraph_ai_service_cache_client.schemas.cache.data.Schema__Cache__Data__Store__Response import Schema__Cache__Data__Store__Response
from mgraph_ai_service_cache_client.client.client_entities.Cache__Entity                    import Cache__Entity
from mgraph_ai_service_cache_client.client.client_entities.Cache__Entity__Data_File         import Cache__Entity__Data_File
from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type              import Enum__Cache__Data_Type
from mgraph_ai_service_html_graph.schemas.cache.data.Schema__Data__Delete__Response         import Schema__Data__Delete__Response
from mgraph_ai_service_html_graph.schemas.cache.data.Schema__Data__Exists__Response         import Schema__Data__Exists__Response
from mgraph_ai_service_html_graph.schemas.cache.data.Schema__Data__Paths__Response          import Schema__Data__Paths__Response
from mgraph_ai_service_html_graph.schemas.cache.data.Schema__Data__Update__Response         import Schema__Data__Update__Response
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Create__Request      import Schema__Entity__Create__Request
from mgraph_ai_service_html_graph.service.cache.Cache__Data__Service                        import Cache__Data__Service
from mgraph_ai_service_html_graph.service.cache.Cache__Entity__Service                      import Cache__Entity__Service
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                  import Html_Cache__Client
from osbot_utils.testing.__                                                                 import __, __SKIP__
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid                       import Random_Guid
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List                       import Type_Safe__List


class test_Cache__Data__Service(TestCase):

    @classmethod
    def setUpClass(cls):                                                          # Shared test objects
        cls.cache_service_client = register_cache_service__in_memory(return_client=True)
        cls.html_cache_client    = Html_Cache__Client()
        cls.entity_service = Cache__Entity__Service(html_cache_client=cls.html_cache_client)
        cls.data_service   = Cache__Data__Service  (html_cache_client=cls.html_cache_client)
        cls.namespace      = 'test-cache-data-service'
        cls.create_test_data()

    @classmethod
    def create_test_data(cls):                                                              # Per-test setup
        cls.cache_key             = f'test/data/{Random_Guid()}'
        cls.data_key              = 'html/content'
        cls.data_file_id          = 'raw'
        cls.test_content          = '<html><body>Test Content</body></html>'
        cls.test_json             = {'key': 'value', 'count': 42, 'nested': {'a': 1}}

        create_request            = Schema__Entity__Create__Request(cache_key = cls.cache_key                        )
        create_result             = cls.entity_service.create      (namespace = cls.namespace, request=create_request)
        cls.cache_id              = create_result.cache_id
        cls.test_entity           = Cache__Entity                  (cache_client = cls.html_cache_client.cache_client,
                                                                    cache_id     = cls.cache_id                      ,
                                                                    namespace    = cls.namespace                     )
        cls.test_entity_data_file = cls.test_entity.data_file      (data_key     = cls.data_key                      ,
                                                                    data_file_id = cls.data_file_id                  )

    # ═══════════════════════════════════════════════════════════════════════════
    # test setup
    # ═══════════════════════════════════════════════════════════════════════════

    def test__setUpClass(self):
        assert self.entity_service.html_cache_client == self.html_cache_client

    def test__create_test_data(self):
        cache_id  = self.cache_id
        namespace = self.namespace
        cache_key = self.cache_key
        with self.test_entity as _:
            assert type(_) is Cache__Entity
            assert _.obj() == __(cache_client=__(),
                                 cache_id  = cache_id,
                                 namespace = namespace)

            assert _.entry__json() == {'cache_key': cache_key}

        with self.test_entity_data_file as _:
            assert type(_) is Cache__Entity__Data_File
            assert _.obj() is None                          # confirm it doesn't exist just (this is not created during the create_test_data



    # ═══════════════════════════════════════════════════════════════════════════
    # store_string / get_string Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__store_string__success(self):
        data_key       = self.data_key
        data_file_id   = self.data_file_id
        content        = self.test_content
        namespace      = self.namespace
        result = self.data_service.store_string(namespace    = namespace     ,
                                                cache_id     = self.cache_id ,
                                                data_key     = data_key      ,
                                                data_file_id = data_file_id  ,
                                                content      = content       )


        assert type(result)     is Schema__Cache__Data__Store__Response
        assert result.cache_id  == self.cache_id
        assert result.data_key  == data_key
        assert result.data_key  == 'html/content'
        assert result.data_type == 'string'
        assert result.file_size == 38
        assert result.obj()     == __(cache_id           = self.cache_id                                            ,
                                      data_files_created = [f'test-cache-data-service/data/key-based/{self.cache_key}/root/data/{self.data_key}/raw.txt'],
                                      data_key           = data_key                                                                                      ,
                                      data_type          = 'string'                                                                                      ,
                                      extension          = 'txt'                                                                                         ,
                                      file_id            = 'raw'                                                                                         ,
                                      file_size          = 38                                                                                            ,
                                      namespace          = namespace                                                                                     ,
                                      timestamp          = __SKIP__                                                                                      )

        with self.test_entity.data_file(data_key = data_key ,data_file_id = data_file_id ) as _:
            assert type(_)            is Cache__Entity__Data_File
            assert _.exists__string() is True
            assert _.string           () == content

    def test__get_string__success(self):
        self.data_service.store_string(namespace    = self.namespace   ,
                                       cache_id     = self.cache_id    ,
                                       data_key     = self.data_key    ,
                                       data_file_id = self.data_file_id,
                                       content      = self.test_content)

        result = self.data_service.get_string(namespace    = self.namespace   ,
                                              cache_id     = self.cache_id    ,
                                              data_key     = self.data_key    ,
                                              data_file_id = self.data_file_id)

        assert result == self.test_content

    def test__get_string__returns_none_when_not_found(self):
        result = self.data_service.get_string(namespace    = self.namespace  ,
                                              cache_id     = self.cache_id   ,
                                              data_key     = 'nonexistent'   ,
                                              data_file_id = 'missing'       )

        assert result is None

    # ═══════════════════════════════════════════════════════════════════════════
    # store_json / get_json Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__store_json__success(self):
        result = self.data_service.store_json(namespace    = self.namespace   ,
                                              cache_id     = self.cache_id    ,
                                              data_key     = self.data_key    ,
                                              data_file_id = self.data_file_id,
                                              content      = self.test_json   )

        assert type(result)    is Schema__Cache__Data__Store__Response
        assert result.data_type == 'json'

    def test__get_json__success(self):
        self.data_service.store_json(namespace    = self.namespace   ,
                                     cache_id     = self.cache_id    ,
                                     data_key     = self.data_key    ,
                                     data_file_id = self.data_file_id,
                                     content      = self.test_json   )

        result = self.data_service.get_json(namespace    = self.namespace   ,
                                            cache_id     = self.cache_id    ,
                                            data_key     = self.data_key    ,
                                            data_file_id = self.data_file_id)

        assert result == self.test_json

    def test__get_json__returns_none_when_not_found(self):
        result = self.data_service.get_json(namespace    = self.namespace  ,
                                            cache_id     = self.cache_id   ,
                                            data_key     = 'nonexistent'   ,
                                            data_file_id = 'missing'       )

        assert result is None

    # ═══════════════════════════════════════════════════════════════════════════
    # update_string Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__update_string__success(self):
        self.data_service.store_string(namespace    = self.namespace   ,
                                       cache_id     = self.cache_id    ,
                                       data_key     = self.data_key    ,
                                       data_file_id = self.data_file_id,
                                       content      = self.test_content)

        updated_content = '<html><body>Updated Content</body></html>'
        result = self.data_service.update_string(namespace    = self.namespace   ,
                                                 cache_id     = self.cache_id    ,
                                                 data_key     = self.data_key    ,
                                                 data_file_id = self.data_file_id,
                                                 content      = updated_content  )

        assert type(result)   is Schema__Data__Update__Response
        assert result.success is True

        retrieved = self.data_service.get_string(namespace    = self.namespace   ,
                                                 cache_id     = self.cache_id    ,
                                                 data_key     = self.data_key    ,
                                                 data_file_id = self.data_file_id)
        assert retrieved == updated_content

    # ═══════════════════════════════════════════════════════════════════════════
    # update_json Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__update_json__success(self):
        self.data_service.store_json(namespace    = self.namespace   ,
                                     cache_id     = self.cache_id    ,
                                     data_key     = self.data_key    ,
                                     data_file_id = self.data_file_id,
                                     content      = self.test_json   )

        updated_json = {'key': 'updated', 'new_field': True}
        result = self.data_service.update_json(namespace    = self.namespace   ,
                                               cache_id     = self.cache_id    ,
                                               data_key     = self.data_key    ,
                                               data_file_id = self.data_file_id,
                                               content      = updated_json     )

        assert type(result)   is Schema__Data__Update__Response
        assert result.success is True

        retrieved = self.data_service.get_json(namespace    = self.namespace   ,
                                               cache_id     = self.cache_id    ,
                                               data_key     = self.data_key    ,
                                               data_file_id = self.data_file_id)
        assert retrieved == updated_json

    # ═══════════════════════════════════════════════════════════════════════════
    # list_files Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__list_files__success_with_files(self):
        assert self.data_service.delete_all(namespace    = self.namespace  ,
                                            cache_id     = self.cache_id   ).obj() == __(success=True, deleted=True)
        self.data_service.store_string(namespace    = self.namespace  ,
                                       cache_id     = self.cache_id   ,
                                       data_key     = 'html'          ,
                                       data_file_id = 'raw'           ,
                                       content      = self.test_content)

        self.data_service.store_json(namespace    = self.namespace  ,
                                     cache_id     = self.cache_id   ,
                                     data_key     = 'meta'          ,
                                     data_file_id = 'info'          ,
                                     content      = self.test_json)

        result = self.data_service.list_files(namespace = self.namespace,
                                              cache_id  = self.cache_id )

        assert type(result)  is Schema__Cache__Data__List__Response
        assert result.obj()  == __(cache_id=self.cache_id ,
                                   namespace=self.namespace,
                                   data_key='',
                                   file_count=2,
                                   files=[__(data_file_id='raw',
                                             data_key='html',
                                             data_type='string',
                                             file_path=f'test-cache-data-service/data/key-based/{self.cache_key}/root/data/html/raw.txt',
                                             file_size=38,
                                             extension='txt'),
                                          __(data_file_id='info',
                                             data_key='meta',
                                             data_type='json',
                                             file_path=f'test-cache-data-service/data/key-based/{self.cache_key}/root/data/meta/info.json',
                                             file_size=77,
                                             extension='json')],
                                   total_size=115)



    def test__list_files__empty_entity(self):
        new_cache_key   = f'test/empty/{Random_Guid()}'
        create_request  = Schema__Entity__Create__Request(cache_key=new_cache_key)
        create_result   = self.entity_service.create(namespace=self.namespace, request=create_request)

        result = self.data_service.list_files(namespace=self.namespace, cache_id=create_result.cache_id)
        assert result.obj() == __(cache_id=create_result.cache_id ,
                                  namespace='test-cache-data-service',
                                  data_key='',
                                  file_count=0,
                                  files=[],
                                  total_size=0)
        assert result.files   == []

    def test__list_files__with_data_key_filter(self):
        assert self.data_service.delete_all(namespace    = self.namespace  ,
                                            cache_id     = self.cache_id   ).obj() == __(success=True, deleted=True)
        self.data_service.store_string(namespace    = self.namespace    ,
                                       cache_id     = self.cache_id     ,
                                       data_key     = 'html/content'    ,
                                       data_file_id = 'raw'             ,
                                       content      = self.test_content)

        self.data_service.store_json(namespace    = self.namespace    ,
                                     cache_id     = self.cache_id     ,
                                     data_key     = 'meta/info'       ,
                                     data_file_id = 'data'            ,
                                     content      = self.test_json)

        result = self.data_service.list_files(namespace = self.namespace ,
                                              cache_id  = self.cache_id  ,
                                              data_key  = 'html'         )

        assert result.obj() == __(cache_id    = self.cache_id                        ,
                                  namespace   = 'test-cache-data-service'           ,
                                  data_key    = 'html'                               ,
                                  file_count  = 1                                    ,
                                  files       = [__(data_file_id = 'raw'            ,
                                                     data_key     = 'html/content'  ,
                                                     data_type    = 'string'        ,
                                                     file_path    = f'test-cache-data-service/data/key-based/{self.cache_key}/root/data/html/content/raw.txt',
                                                     file_size    = 38              ,
                                                     extension    = 'txt'           )],
                                  total_size  = 38                                   )




    # ═══════════════════════════════════════════════════════════════════════════
    # list_paths Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__list_paths__success(self):
        assert self.data_service.delete_all(namespace    = self.namespace  ,
                                            cache_id     = self.cache_id   ).obj() == __(success=True, deleted=True)
        self.data_service.store_string(namespace=self.namespace, cache_id=self.cache_id,
                                       data_key='html', data_file_id='raw', content=self.test_content)

        result = self.data_service.list_paths(namespace=self.namespace, cache_id=self.cache_id)

        assert type(result)            is Schema__Data__Paths__Response
        assert result.success          is True
        assert result.count            >= 1
        assert type(result.file_paths) is Type_Safe__List
        assert result.obj()            == __(success    = True  ,
                                             file_paths = [f'test-cache-data-service/data/key-based/{self.cache_key}/root/data/html/raw.txt'],
                                             count      = 1 )

    def test__list_paths__empty_entity(self):
        new_cache_key  = f'test/empty/{Random_Guid()}'
        create_request = Schema__Entity__Create__Request(cache_key=new_cache_key)
        create_result  = self.entity_service.create(namespace=self.namespace, request=create_request)

        result = self.data_service.list_paths(namespace=self.namespace, cache_id=create_result.cache_id)

        assert result.success    is False
        assert result.file_paths == []
        assert result.count      == 0

    # ═══════════════════════════════════════════════════════════════════════════
    # exists Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__exists__returns_true_when_exists(self):
        self.data_service.store_string(namespace=self.namespace, cache_id=self.cache_id,
                                       data_key=self.data_key, data_file_id=self.data_file_id,
                                       content=self.test_content)

        result = self.data_service.exists(namespace    = self.namespace                ,
                                          cache_id     = self.cache_id                 ,
                                          data_key     = self.data_key                 ,
                                          data_file_id = self.data_file_id             ,
                                          data_type    = Enum__Cache__Data_Type.STRING )

        assert type(result)  is Schema__Data__Exists__Response
        assert result.exists is True

    def test__exists__returns_false_when_not_exists(self):
        result = self.data_service.exists(namespace    = self.namespace              ,
                                          cache_id     = self.cache_id               ,
                                          data_key     = 'nonexistent'               ,
                                          data_file_id = 'missing'                   ,
                                          data_type    = Enum__Cache__Data_Type.JSON )

        assert result.exists is False

    # ═══════════════════════════════════════════════════════════════════════════
    # delete Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__delete__success(self):
        self.data_service.store_string(namespace=self.namespace, cache_id=self.cache_id,
                                       data_key=self.data_key, data_file_id=self.data_file_id,
                                       content=self.test_content)

        result = self.data_service.delete(namespace    = self.namespace                ,
                                          cache_id     = self.cache_id                 ,
                                          data_key     = self.data_key                 ,
                                          data_file_id = self.data_file_id             ,
                                          data_type    = Enum__Cache__Data_Type.STRING )

        assert type(result)   is Schema__Data__Delete__Response
        assert result.success is True
        assert result.deleted is True

        exists_result = self.data_service.exists(namespace    = self.namespace                ,
                                                 cache_id     = self.cache_id                 ,
                                                 data_key     = self.data_key                 ,
                                                 data_file_id = self.data_file_id             ,
                                                 data_type    = Enum__Cache__Data_Type.STRING )
        assert exists_result.exists is False                                      # Confirm deleted

    def test__delete__returns_false_when_not_found(self):
        result = self.data_service.delete(namespace    = self.namespace              ,
                                          cache_id     = self.cache_id               ,
                                          data_key     = 'nonexistent'               ,
                                          data_file_id = 'missing'                   ,
                                          data_type    = Enum__Cache__Data_Type.JSON )

        assert result.success is True                                             # Operation succeeded
        assert result.deleted is False                                            # But nothing was deleted
