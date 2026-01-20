# ═══════════════════════════════════════════════════════════════════════════════
# Test__Cache__Entity__Service - Tests for cache entity service
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                   import TestCase
from mgraph_ai_service_cache_client.schemas.cache.file.Schema__Cache__File__Metadata            import Schema__Cache__File__Metadata
from mgraph_ai_service_cache_client.schemas.cache.file.Schema__Cache__File__Refs                import Schema__Cache__File__Refs
from mgraph_ai_service_cache_client.client.client_entities.Cache__Entity                        import Cache__Entity
from mgraph_ai_service_cache_client.utils.Version                                               import version__mgraph_ai_service_cache_client
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Create__Request          import Schema__Entity__Create__Request
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Create__Response         import Schema__Entity__Create__Response
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Lookup__Request          import Schema__Entity__Lookup__Request
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Lookup__Response         import Schema__Entity__Lookup__Response
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Exists__Response         import Schema__Entity__Exists__Response
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Delete__Response         import Schema__Entity__Delete__Response
from mgraph_ai_service_html_graph.service.cache.Cache__Entity__Service                          import Cache__Entity__Service
from osbot_utils.testing.__                                                                     import __, __SKIP__
from osbot_utils.type_safe.primitives.domains.identifiers.Guid                                  import Guid
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid                           import Random_Guid
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                        import create_html_cache_client


class test_Cache__Entity__Service(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.html_cache_client, cls.cache_service = create_html_cache_client()
        cls.entity_service = Cache__Entity__Service(cache_client=cls.html_cache_client)
        cls.namespace      = 'test-cache-entity-service'
        cls.create_test_data()

    @classmethod
    def create_test_data(cls):
        cls.cache_key   = f'test/entity/{Random_Guid()}'
        create_request  = Schema__Entity__Create__Request(cache_key=cls.cache_key)
        create_result   = cls.entity_service.create(namespace=cls.namespace, request=create_request)
        cls.cache_id    = create_result.cache_id
        cls.cache_hash  = create_result.cache_hash
        cls.test_entity = Cache__Entity(cache_client = cls.html_cache_client.cache_client,
                                        cache_id     = cls.cache_id                      ,
                                        namespace    = cls.namespace                     )

        cls.cache_key_2 = f'test/entity/{Random_Guid()}'

    # ═══════════════════════════════════════════════════════════════════════════
    # test setup
    # ═══════════════════════════════════════════════════════════════════════════

    def test__setUpClass(self):
        assert self.entity_service.cache_client == self.html_cache_client

    def test__create_test_data(self):
        cache_id  = self.cache_id
        namespace = self.namespace
        cache_key = self.cache_key
        with self.test_entity as _:
            assert type(_) is Cache__Entity
            assert _.obj() == __(cache_client = __(config = __(base_url         = None                                   ,
                                                               api_key          = None                                   ,
                                                               api_key_header   = None                                   ,
                                                               mode             = 'in_memory'                            ,
                                                               fast_api_app     = 'FastAPI'                              ,
                                                               timeout          = 30                                     ,
                                                               service_name     = 'Cache__Service__Fast_API'             ,
                                                               service_version  = version__mgraph_ai_service_cache_client)),
                                 cache_id     = cache_id                                                                  ,
                                 namespace    = namespace                                                                 )

            assert _.entry__json() == {'cache_key': cache_key}

    # ═══════════════════════════════════════════════════════════════════════════
    # create Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__create__success_new_entity(self):
        new_cache_key = f'test/entity/new-{Random_Guid()}'
        request       = Schema__Entity__Create__Request(cache_key=new_cache_key)

        result = self.entity_service.create(namespace=self.namespace, request=request)

        assert type(result)    is Schema__Entity__Create__Response
        assert result.success  is True
        assert result.cache_id != ''

    def test__create__returns_new_entity_on_same_hash(self):
        new_cache_key = f'test/entity/existing-{Guid("seed")}'          # create a deterministic GUID
        cache_hash    = self.cache_service.hash__from_string(new_cache_key)
        request       = Schema__Entity__Create__Request(cache_key=new_cache_key)

        result_1      = self.entity_service.create(namespace=self.namespace, request=request)           # this will create a new entry
        result_2      = self.entity_service.create(namespace=self.namespace, request=request)           # so will this

        cache_id_1          = result_1.cache_id
        cache_id_2          = result_2.cache_id
        cache_id_1__sharded = f"{cache_id_1[0:2]}/{cache_id_1[2:4]}/{cache_id_1}"
        cache_id_2__sharded = f"{cache_id_2[0:2]}/{cache_id_2[2:4]}/{cache_id_2}"

        assert result_1.obj()    == __(success    = True      ,
                                       cache_id   = cache_id_1,                 # this is a unique value
                                       cache_hash = cache_hash)                 # this is the same on both

        assert result_2.obj()    == __(success   = True       ,
                                       cache_id  = cache_id_2 ,                 # different from result_1
                                       cache_hash = cache_hash)                 # same as in result_1

        assert cache_id_1          != cache_id_2
        assert result_1.cache_id   != result_2.cache_id                         # these are the different
        assert result_1.cache_hash == result_2.cache_hash                       # these are the same

        cache_entity_1 = Cache__Entity(cache_client = self.html_cache_client.cache_client, namespace=self.namespace, cache_id=cache_id_1)
        cache_entity_2 = Cache__Entity(cache_client = self.html_cache_client.cache_client, namespace=self.namespace, cache_id=cache_id_2)

        assert cache_entity_1.entry__json__obj()             == __(cache_key=new_cache_key)
        assert cache_entity_2.entry__json__obj()             == __(cache_key=new_cache_key)

        assert cache_entity_1.exists()                       is True
        assert cache_entity_2.exists()                       is True

        assert cache_entity_1.refs().all_paths.by_hash.obj() == ['test-cache-entity-service/refs/by-hash/4f/9c/4f9c4753e0eb2e59.json']
        assert cache_entity_2.refs().all_paths.by_hash.obj() == ['test-cache-entity-service/refs/by-hash/4f/9c/4f9c4753e0eb2e59.json']

        assert cache_entity_1.refs().all_paths.by_id  .obj() == [f'test-cache-entity-service/refs/by-id/{cache_id_1__sharded}.json']
        assert cache_entity_2.refs().all_paths.by_id  .obj() == [f'test-cache-entity-service/refs/by-id/{cache_id_2__sharded}.json']
        assert cache_entity_1.cache__hash()                  == cache_hash
        assert cache_entity_1.cache__file__hash__obj()       == __(cache_hash     = cache_hash,
                                                                   cache_ids      = [__(cache_id  = cache_id_1,
                                                                                        timestamp =__SKIP__),
                                                                                     __(cache_id  = cache_id_2,
                                                                                        timestamp = __SKIP__)],
                                                                   latest_id      = cache_id_2,
                                                                   total_versions = 2)




    def test__create__with_custom_file_id(self):
        new_cache_key = f'test/entity/custom-{Random_Guid()}'
        request       = Schema__Entity__Create__Request(cache_key=new_cache_key, file_id='custom-file')

        result = self.entity_service.create(namespace=self.namespace, request=request)

        assert result.success  is True
        assert result.cache_id != ''

    def test__create__different_keys_create_different_entities(self):
        cache_key_a = f'test/entity/a-{Random_Guid()}'
        cache_key_b = f'test/entity/b-{Random_Guid()}'
        request_1   = Schema__Entity__Create__Request(cache_key=cache_key_a)
        request_2   = Schema__Entity__Create__Request(cache_key=cache_key_b)

        result_1 = self.entity_service.create(namespace=self.namespace, request=request_1)
        result_2 = self.entity_service.create(namespace=self.namespace, request=request_2)

        assert result_1.cache_id != result_2.cache_id

    # ═══════════════════════════════════════════════════════════════════════════
    # lookup Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__lookup__by_cache_key_found(self):
        lookup_request = Schema__Entity__Lookup__Request(cache_key=self.cache_key)

        result = self.entity_service.lookup(namespace=self.namespace, request=lookup_request)

        assert type(result)    is Schema__Entity__Lookup__Response
        assert result.success  is True
        assert result.found    is True
        assert result.cache_id == self.cache_id

    def test__lookup__by_cache_key_not_found(self):
        lookup_request = Schema__Entity__Lookup__Request(cache_key=f'nonexistent/{Random_Guid()}')

        result = self.entity_service.lookup(namespace=self.namespace, request=lookup_request)

        assert result.success is True
        assert result.found   is False

    def test__lookup__no_key_or_hash_returns_failure(self):
        lookup_request = Schema__Entity__Lookup__Request()

        result = self.entity_service.lookup(namespace=self.namespace, request=lookup_request)

        assert result.success is False

    # ═══════════════════════════════════════════════════════════════════════════
    # get Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__get__returns_entry_data(self):
        result = self.entity_service.get(namespace=self.namespace, cache_id=self.cache_id)

        assert result is not None
        assert type(result) is dict

    def test__get__returns_none_when_not_found(self):
        result = self.entity_service.get(namespace=self.namespace, cache_id=Random_Guid())

        assert result is None

    # ═══════════════════════════════════════════════════════════════════════════
    # get_metadata Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__get_metadata__returns_metadata(self):
        result = self.entity_service.get_metadata(namespace=self.namespace, cache_id=self.cache_id)
        assert type(result)           is Schema__Cache__File__Metadata
        assert result.data.cache_hash == self.cache_hash

    # ═══════════════════════════════════════════════════════════════════════════
    # get_refs Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__get_refs__returns_refs(self):
        result = self.entity_service.get_refs(namespace=self.namespace, cache_id=self.cache_id)
        assert type(result) is Schema__Cache__File__Refs
        assert result.cache_hash == self.cache_hash


    # ═══════════════════════════════════════════════════════════════════════════
    # exists Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__exists__returns_true_when_exists(self):
        result = self.entity_service.exists(namespace=self.namespace, cache_id=self.cache_id)

        assert type(result)  is Schema__Entity__Exists__Response
        assert result.exists is True

    def test__exists__returns_false_when_not_exists(self):
        result = self.entity_service.exists(namespace=self.namespace, cache_id=Random_Guid())

        assert result.exists is False

    # ═══════════════════════════════════════════════════════════════════════════
    # delete Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__delete__success_deleted(self):
        new_cache_key  = f'test/entity/delete-{Random_Guid()}'
        create_request = Schema__Entity__Create__Request(cache_key=new_cache_key)
        create_result  = self.entity_service.create(namespace=self.namespace, request=create_request)

        result = self.entity_service.delete(namespace=self.namespace, cache_id=create_result.cache_id)

        assert type(result)   is Schema__Entity__Delete__Response
        assert result.success is True
        assert result.deleted is True

        exists_result = self.entity_service.exists(namespace=self.namespace, cache_id=create_result.cache_id)
        assert exists_result.exists is False

    def test__delete__returns_false_when_not_found(self):
        result = self.entity_service.delete(namespace=self.namespace, cache_id=Random_Guid())

        assert result.success is True
        assert result.deleted is False