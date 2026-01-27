# ═══════════════════════════════════════════════════════════════════════════════
# test_Html_Cache__Client - Tests for cache service client wrapper
# Uses in-memory cache service via FastAPI test client for real behavior testing
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                   import TestCase
from mgraph_ai_service_cache_client.client.cache_service.register_cache_service                 import register_cache_service__in_memory
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__Cache_Hash    import Safe_Str__Cache__File__Cache_Hash
from mgraph_ai_service_cache_client.schemas.cache.Schema__Cache__Store__Response                import Schema__Cache__Store__Response
from mgraph_ai_service_cache_client.schemas.cache.data.Schema__Cache__Data__Store__Response     import Schema__Cache__Data__Store__Response
from mgraph_ai_service_cache_client.schemas.cache.data.Schema__Cache__Data__List__Response      import Schema__Cache__Data__List__Response
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                      import Html_Cache__Client
from mgraph_ai_service_html_graph.service.cache_storage.schemas.Schema__Html_Cache__Entry       import Schema__Html_Cache__Entry
from osbot_utils.testing.__                                                                     import __
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.utils.Objects                                                                  import base_types
from osbot_utils.utils.Misc                                                                     import is_guid
from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type                  import Enum__Cache__Data_Type


class test_Html_Cache__Client(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup - in-memory cache
        cls.cache_service_client = register_cache_service__in_memory(return_client=True)
        cls.html_cache_client    = Html_Cache__Client()
        cls.namespace            = 'test-namespace'

    def _create_parent_entry(self, cache_key: str) -> str:                       # Helper to create parent entry, returns cache_id
        entry    = Schema__Html_Cache__Entry(cache_key=cache_key)
        response = self.html_cache_client.entry__store(namespace       = self.namespace,
                                                       cache_key       = cache_key     ,
                                                       file_id         = 'html-entry'  ,
                                                       entry           = entry         )
        return response.cache_id

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test auto-initialization
        with self.html_cache_client as _:
            assert type(_)              is Html_Cache__Client
            assert base_types(_)        == [Type_Safe, object]
            assert _.cache_client       is not None
            assert _.hash_generator     is not None
            assert _.obj()              == __(cache_client    = __(),
                                               hash_generator = __(config=__(algorithm = 'sha256' ,
                                                                             length    = 16       )))

    # ═══════════════════════════════════════════════════════════════════════════
    # health_check Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_health_check(self):                                                 # Test health check returns True
        with self.html_cache_client as _:
            result = _.health_check()
            assert result is True

    # ═══════════════════════════════════════════════════════════════════════════
    # entry__store Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_entry__store(self):                                                 # Test storing entry
        with self.html_cache_client as _:
            entry    = Schema__Html_Cache__Entry(cache_key='test/entry-store')
            response = _.entry__store(namespace       = self.namespace       ,
                                      cache_key       = 'test/entry-store'   ,
                                      file_id         = 'html-entry'         ,
                                      entry           = entry                )

            assert type(response)      is Schema__Cache__Store__Response
            assert response.cache_id   is not None
            assert is_guid(response.cache_id) is True
            assert response.namespace  == self.namespace

    # ═══════════════════════════════════════════════════════════════════════════
    # entry__retrieve Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_entry__retrieve(self):                                              # Test retrieving entry
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/entry-retrieve')

            result = _.entry__retrieve(namespace = self.namespace,
                                       cache_id  = cache_id      )

            assert result                is not None
            assert type(result)          is dict
            assert result['cache_key']   == 'test/entry-retrieve'

    def test_entry__retrieve__not_found(self):                                   # Test returns None for missing
        with self.html_cache_client as _:
            from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id import Cache_Id
            result = _.entry__retrieve(namespace = self.namespace,
                                       cache_id  = Cache_Id()    )

            assert result is None

    # ═══════════════════════════════════════════════════════════════════════════
    # entry__exists Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_entry__exists__true(self):                                          # Test exists returns True
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/entry-exists-true')

            result = _.entry__exists(namespace = self.namespace,
                                     cache_id  = cache_id      )

            assert result is True

    def test_entry__exists__false(self):                                         # Test exists returns False
        with self.html_cache_client as _:
            from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id import Cache_Id
            result = _.entry__exists(namespace = self.namespace,
                                     cache_id  = Cache_Id()    )

            assert result is False

    # ═══════════════════════════════════════════════════════════════════════════
    # entry__exists_by_hash Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_entry__exists_by_hash__true(self):                                  # Test exists by hash returns True
        with self.html_cache_client as _:
            cache_key  = 'test/entry-exists-hash-true'
            cache_id   = self._create_parent_entry(cache_key)
            cache_hash = _.hash_generator.from_string(cache_key)

            result = _.entry__exists_by_hash(namespace  = self.namespace,
                                             cache_hash = cache_hash    )

            assert result is True

    def test_entry__exists_by_hash__false(self):                                 # Test exists by hash returns False
        with self.html_cache_client as _:
            result = _.entry__exists_by_hash(namespace  = self.namespace              ,
                                             cache_hash = 'c123456789')

            assert result is False

    # ═══════════════════════════════════════════════════════════════════════════
    # entry__update Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_entry__update(self):                                                # Test updating entry
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/entry-update')

            entry      = Schema__Html_Cache__Entry(cache_key='test/entry-update')
            entry.data = {'updated': True, 'value': 42}

            result = _.entry__update(namespace = self.namespace,
                                     cache_id  = cache_id      ,
                                     entry     = entry         )

            assert result is True

            # Verify update persisted
            retrieved = _.entry__retrieve(namespace = self.namespace,
                                          cache_id  = cache_id      )
            assert retrieved['data'] == {'updated': True, 'value': 42}

    def test_entry__update__not_found(self):                                     # Test update returns False for missing
        with self.html_cache_client as _:
            from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id import Cache_Id
            entry = Schema__Html_Cache__Entry(cache_key='test/missing')

            result = _.entry__update(namespace = self.namespace,
                                     cache_id  = Cache_Id()    ,
                                     entry     = entry         )

            assert result is False

    # ═══════════════════════════════════════════════════════════════════════════
    # entry__delete Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_entry__delete(self):                                                # Test deleting entry
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/entry-delete')

            result = _.entry__delete(namespace = self.namespace,
                                     cache_id  = cache_id      )

            assert result is True

            # Verify deleted
            assert _.entry__exists(namespace = self.namespace,
                                   cache_id  = cache_id      ) is False

    def test_entry__delete__idempotent(self):                                    # Test delete returns False second time
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/entry-delete-idem')

            first_delete  = _.entry__delete(namespace = self.namespace, cache_id = cache_id)
            second_delete = _.entry__delete(namespace = self.namespace, cache_id = cache_id)

            assert first_delete  is True
            assert second_delete is False

    # ═══════════════════════════════════════════════════════════════════════════
    # cache_id__from_key Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_cache_id__from_key(self):                                           # Test finding entry by key
        with self.html_cache_client as _:
            cache_key = 'test/cache-id-from-key'
            cache_id  = self._create_parent_entry(cache_key)

            result = _.cache_id__from_key(namespace = self.namespace,
                                          cache_key = cache_key     )

            assert result == cache_id

    def test_cache_id__from_key__not_found(self):                                # Test returns None for missing key
        with self.html_cache_client as _:
            result = _.cache_id__from_key(namespace = self.namespace     ,
                                          cache_key = 'nonexistent/key'  )

            assert result is None

    # ═══════════════════════════════════════════════════════════════════════════
    # data__store_string Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_data__store_string(self):                                           # Test storing string data
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/data-store-string')

            result = _.data__store_string(namespace    = self.namespace  ,
                                          cache_id     = cache_id        ,
                                          data_key     = 'raw-html'      ,
                                          data_file_id = 'source'        ,
                                          content      = '<html></html>' )

            assert type(result)      is Schema__Cache__Data__Store__Response
            assert result.cache_id   == cache_id
            assert result.data_type  == 'string'
            assert result.data_key   == 'raw-html'
            assert result.file_id    == 'source'

    # ═══════════════════════════════════════════════════════════════════════════
    # data__store_json Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_data__store_json(self):                                             # Test storing JSON data
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/data-store-json')

            result = _.data__store_json(namespace    = self.namespace       ,
                                        cache_id     = cache_id             ,
                                        data_key     = 'parsed'             ,
                                        data_file_id = 'dict'               ,
                                        data         = {'tag': 'html'}      )

            assert type(result)      is Schema__Cache__Data__Store__Response
            assert result.cache_id   == cache_id
            assert result.data_type  == 'json'
            assert result.data_key   == 'parsed'
            assert result.file_id    == 'dict'

    # ═══════════════════════════════════════════════════════════════════════════
    # data__retrieve_string Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_data__retrieve_string(self):                                        # Test retrieving string data
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/data-retrieve-string')
            content  = '<html><body>Test</body></html>'

            _.data__store_string(namespace    = self.namespace,
                                 cache_id     = cache_id      ,
                                 data_key     = 'layer'       ,
                                 data_file_id = 'content'     ,
                                 content      = content       )

            result = _.data__retrieve_string(namespace    = self.namespace,
                                             cache_id     = cache_id      ,
                                             data_key     = 'layer'       ,
                                             data_file_id = 'content'     )

            assert result == content

    def test_data__retrieve_string__not_found(self):                             # Test returns None for missing
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/data-retrieve-string-404')

            result = _.data__retrieve_string(namespace    = self.namespace,
                                             cache_id     = cache_id      ,
                                             data_key     = 'missing'     ,
                                             data_file_id = 'file'        )

            assert result is None

    # ═══════════════════════════════════════════════════════════════════════════
    # data__retrieve_json Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_data__retrieve_json(self):                                          # Test retrieving JSON data
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/data-retrieve-json')
            data     = {'tag': 'html', 'children': [{'tag': 'body'}]}

            _.data__store_json(namespace    = self.namespace,
                               cache_id     = cache_id      ,
                               data_key     = 'parsed'      ,
                               data_file_id = 'dict'        ,
                               data         = data          )

            result = _.data__retrieve_json(namespace    = self.namespace,
                                           cache_id     = cache_id      ,
                                           data_key     = 'parsed'      ,
                                           data_file_id = 'dict'        )

            assert result         == data
            assert result['tag']  == 'html'

    def test_data__retrieve_json__not_found(self):                               # Test returns None for missing
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/data-retrieve-json-404')

            result = _.data__retrieve_json(namespace    = self.namespace,
                                           cache_id     = cache_id      ,
                                           data_key     = 'missing'     ,
                                           data_file_id = 'file'        )

            assert result is None

    # ═══════════════════════════════════════════════════════════════════════════
    # data__exists Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_data__exists__true(self):                                           # Test exists returns True
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/data-exists-true')

            _.data__store_string(namespace    = self.namespace,
                                 cache_id     = cache_id      ,
                                 data_key     = 'layer'       ,
                                 data_file_id = 'data'        ,
                                 content      = 'test'        )

            result = _.data__exists(namespace    = self.namespace              ,
                                    cache_id     = cache_id                    ,
                                    data_key     = 'layer'                     ,
                                    data_file_id = 'data'                      ,
                                    data_type    = Enum__Cache__Data_Type.STRING)

            assert result is True

    def test_data__exists__false(self):                                          # Test exists returns False
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/data-exists-false')

            result = _.data__exists(namespace    = self.namespace              ,
                                    cache_id     = cache_id                    ,
                                    data_key     = 'nonexistent'               ,
                                    data_file_id = 'file'                      ,
                                    data_type    = Enum__Cache__Data_Type.STRING)

            assert result is False

    # ═══════════════════════════════════════════════════════════════════════════
    # data__list Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_data__list(self):                                                   # Test listing data files
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/data-list')

            _.data__store_string(namespace    = self.namespace,
                                 cache_id     = cache_id      ,
                                 data_key     = 'layer1'      ,
                                 data_file_id = 'file1'       ,
                                 content      = 'content1'    )

            _.data__store_json(namespace    = self.namespace,
                               cache_id     = cache_id      ,
                               data_key     = 'layer2'      ,
                               data_file_id = 'file2'       ,
                               data         = {'key': 'val'})

            result = _.data__list(namespace = self.namespace,
                                  cache_id  = cache_id      ,
                                  recursive = True          )

            assert type(result)       is Schema__Cache__Data__List__Response
            assert result.cache_id    == cache_id
            assert result.file_count  >= 2
            assert result.total_size  >  0

    def test_data__list__with_data_key(self):                                    # Test listing with key filter
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/data-list-key')

            _.data__store_string(namespace    = self.namespace,
                                 cache_id     = cache_id      ,
                                 data_key     = 'target'      ,
                                 data_file_id = 'file1'       ,
                                 content      = 'content1'    )

            _.data__store_string(namespace    = self.namespace,
                                 cache_id     = cache_id      ,
                                 data_key     = 'other'       ,
                                 data_file_id = 'file2'       ,
                                 content      = 'content2'    )

            result = _.data__list(namespace = self.namespace,
                                  cache_id  = cache_id      ,
                                  data_key  = 'target'      ,
                                  recursive = True          )

            assert result.file_count >= 1

    def test_data__list__empty(self):                                            # Test listing empty entry
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/data-list-empty')

            result = _.data__list(namespace = self.namespace,
                                  cache_id  = cache_id      ,
                                  recursive = True          )

            assert result.file_count == 0
            assert result.files      == []

    # ═══════════════════════════════════════════════════════════════════════════
    # data__update_string Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_data__update_string(self):                                          # Test updating string data
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/data-update-string')

            _.data__store_string(namespace    = self.namespace,
                                 cache_id     = cache_id      ,
                                 data_key     = 'layer'       ,
                                 data_file_id = 'content'     ,
                                 content      = 'original'    )

            result = _.data__update_string(namespace    = self.namespace,
                                           cache_id     = cache_id      ,
                                           data_key     = 'layer'       ,
                                           data_file_id = 'content'     ,
                                           content      = 'updated'     )

            assert result is True

            # Verify update persisted
            retrieved = _.data__retrieve_string(namespace    = self.namespace,
                                                cache_id     = cache_id      ,
                                                data_key     = 'layer'       ,
                                                data_file_id = 'content'     )
            assert retrieved == 'updated'

    def test_data__update_string__not_found(self):                               # Test update returns False for missing
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/data-update-string-404')

            result = _.data__update_string(namespace    = self.namespace,
                                           cache_id     = cache_id      ,
                                           data_key     = 'missing'     ,
                                           data_file_id = 'file'        ,
                                           content      = 'new'         )

            assert result is False

    # ═══════════════════════════════════════════════════════════════════════════
    # data__update_json Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_data__update_json(self):                                            # Test updating JSON data
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/data-update-json')

            _.data__store_json(namespace    = self.namespace   ,
                               cache_id     = cache_id         ,
                               data_key     = 'layer'          ,
                               data_file_id = 'data'           ,
                               data         = {'version': 1}   )

            result = _.data__update_json(namespace    = self.namespace   ,
                                         cache_id     = cache_id         ,
                                         data_key     = 'layer'          ,
                                         data_file_id = 'data'           ,
                                         data         = {'version': 2}   )

            assert result is True

            # Verify update persisted
            retrieved = _.data__retrieve_json(namespace    = self.namespace,
                                              cache_id     = cache_id      ,
                                              data_key     = 'layer'       ,
                                              data_file_id = 'data'        )
            assert retrieved == {'version': 2}

    def test_data__update_json__not_found(self):                                 # Test update returns False for missing
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/data-update-json-404')

            result = _.data__update_json(namespace    = self.namespace,
                                         cache_id     = cache_id      ,
                                         data_key     = 'missing'     ,
                                         data_file_id = 'file'        ,
                                         data         = {'key': 'val'})

            assert result is False

    # ═══════════════════════════════════════════════════════════════════════════
    # data__delete Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_data__delete(self):                                                 # Test deleting data file
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/data-delete')

            _.data__store_string(namespace    = self.namespace,
                                 cache_id     = cache_id      ,
                                 data_key     = 'to-delete'   ,
                                 data_file_id = 'file'        ,
                                 content      = 'delete me'   )

            # Verify exists
            assert _.data__exists(namespace    = self.namespace              ,
                                  cache_id     = cache_id                    ,
                                  data_key     = 'to-delete'                 ,
                                  data_file_id = 'file'                      ,
                                  data_type    = Enum__Cache__Data_Type.STRING) is True

            # Delete
            result = _.data__delete(namespace    = self.namespace              ,
                                    cache_id     = cache_id                    ,
                                    data_key     = 'to-delete'                 ,
                                    data_file_id = 'file'                      ,
                                    data_type    = Enum__Cache__Data_Type.STRING)

            assert result is True

            # Verify deleted
            assert _.data__exists(namespace    = self.namespace              ,
                                  cache_id     = cache_id                    ,
                                  data_key     = 'to-delete'                 ,
                                  data_file_id = 'file'                      ,
                                  data_type    = Enum__Cache__Data_Type.STRING) is False

    def test_data__delete__not_found(self):                                      # Test delete returns False for missing
        with self.html_cache_client as _:
            cache_id = self._create_parent_entry('test/data-delete-404')

            result = _.data__delete(namespace    = self.namespace              ,
                                    cache_id     = cache_id                    ,
                                    data_key     = 'nonexistent'               ,
                                    data_file_id = 'file'                      ,
                                    data_type    = Enum__Cache__Data_Type.STRING)

            assert result is False

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Test: Entry Lifecycle
    # ═══════════════════════════════════════════════════════════════════════════

    def test_entry_operations(self):                                             # Test complete entry lifecycle
        with self.html_cache_client as _:
            entry            = Schema__Html_Cache__Entry(cache_key='example.com/page-1')
            cache_key        = 'example.com/page-1'
            response         = _.entry__store(namespace       = self.namespace      ,
                                              cache_key       = 'example.com/page-1',
                                              file_id         = 'html-entry'        ,
                                              entry           = entry               )
            cache_id         = response.cache_id
            cache_hash       = Safe_Str__Cache__File__Cache_Hash(_.hash_generator.from_string(cache_key))
            cache_id__shared = f'{cache_id[0:2]}/{cache_id[2:4]}/{cache_id}'
            assert type(_)                    is Html_Cache__Client
            assert response                   is not None
            assert cache_id                   is not None
            assert is_guid(cache_id)          is True
            assert type(response)             == Schema__Cache__Store__Response
            assert response.cache_hash        == cache_hash
            assert response.obj()             == __(cache_id    = cache_id          ,
                                                    cache_hash  = '86957ee90c614202',
                                                    namespace   = 'test-namespace'  ,
                                                    paths       = __(data  = [  'test-namespace/data/key-based/example.com/page-1/html-entry.json',
                                                                                'test-namespace/data/key-based/example.com/page-1/html-entry.json.config',
                                                                                'test-namespace/data/key-based/example.com/page-1/html-entry.json.metadata'],
                                                                    by_hash = [ 'test-namespace/refs/by-hash/86/95/86957ee90c614202.json'],
                                                                    by_id   = [f'test-namespace/refs/by-id/{cache_id__shared}.json']),
                                                    size        = 39 )

            assert _.cache_id__from_key   (namespace = self.namespace, cache_key = cache_key  ) == cache_id
            assert _.entry__retrieve      (namespace = self.namespace, cache_id  = cache_id   ) == {'cache_key': 'example.com/page-1'}
            assert _.entry__exists_by_hash(namespace = self.namespace, cache_hash = cache_hash) is True
            assert _.entry__exists        (namespace = self.namespace, cache_id   = cache_id  ) is True
            entry.data = {'new': 'data', 'is': 42}
            assert _.entry__update        (namespace = self.namespace, cache_id   = cache_id  ,
                                           entry     = entry                                  ) is True
            assert _.entry__retrieve      (namespace = self.namespace, cache_id   = cache_id  ) == {'cache_key': 'example.com/page-1',
                                                                                                    'data'     : {'new': 'data', 'is': 42} }
            assert _.entry__delete        (namespace = self.namespace, cache_id   = cache_id  ) is True
            assert _.entry__delete        (namespace = self.namespace, cache_id   = cache_id  ) is False
            assert _.entry__exists_by_hash(namespace = self.namespace, cache_hash = cache_hash) is False
            assert _.entry__exists        (namespace = self.namespace, cache_id   = cache_id  ) is False
            assert _.entry__retrieve      (namespace = self.namespace, cache_id   = cache_id  ) is None
            assert _.cache_id__from_key   (namespace = self.namespace, cache_key = cache_key  ) is None
            assert _.entry__update        (namespace = self.namespace, cache_id   = cache_id  ,
                                           entry     = entry                                  ) is False

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Test: Data Lifecycle
    # ═══════════════════════════════════════════════════════════════════════════

    def test_data_operations(self):                                              # Test complete data file lifecycle
        with self.html_cache_client as _:
            entry     = Schema__Html_Cache__Entry(cache_key='example.com/data-test')            # Setup: Create parent entry
            response  = _.entry__store(namespace       = self.namespace            ,
                                       cache_key       = 'example.com/data-test'   ,
                                       file_id         = 'parent-entry'            ,
                                       entry           = entry                     )
            cache_id  = response.cache_id

            assert cache_id is not None

            # ═══════════════════════════════════════════════════════════════════
            # Store data files
            # ═══════════════════════════════════════════════════════════════════

            string_result = _.data__store_string(namespace    = self.namespace     ,
                                                 cache_id     = cache_id           ,
                                                 data_key     = 'layer-html'       ,
                                                 data_file_id = 'content'          ,
                                                 content      = '<html>test</html>')

            json_result   = _.data__store_json(namespace    = self.namespace    ,
                                               cache_id     = cache_id          ,
                                               data_key     = 'layer-metadata'  ,
                                               data_file_id = 'meta'            ,
                                               data         = {'title': 'Test'} )

            assert string_result                is not None
            assert string_result.cache_id       == cache_id
            assert string_result.data_type      == 'string'
            assert string_result.data_key       == 'layer-html'
            assert string_result.file_id        == 'content'

            assert json_result                  is not None
            assert json_result.cache_id         == cache_id
            assert json_result.data_type        == 'json'
            assert json_result.data_key         == 'layer-metadata'
            assert json_result.file_id          == 'meta'

            # ═══════════════════════════════════════════════════════════════════
            # Verify data files exist
            # ═══════════════════════════════════════════════════════════════════

            assert _.data__exists(namespace    = self.namespace              ,
                                  cache_id     = cache_id                    ,
                                  data_key     = 'layer-html'                ,
                                  data_file_id = 'content'                   ,
                                  data_type    = Enum__Cache__Data_Type.STRING) is True

            assert _.data__exists(namespace    = self.namespace            ,
                                  cache_id     = cache_id                  ,
                                  data_key     = 'layer-metadata'          ,
                                  data_file_id = 'meta'                    ,
                                  data_type    = Enum__Cache__Data_Type.JSON) is True

            assert _.data__exists(namespace    = self.namespace              ,
                                  cache_id     = cache_id                    ,
                                  data_key     = 'layer-html'                ,
                                  data_file_id = 'non-existent'              ,
                                  data_type    = Enum__Cache__Data_Type.STRING) is False

            # ═══════════════════════════════════════════════════════════════════
            # List data files
            # ═══════════════════════════════════════════════════════════════════

            list_result = _.data__list(namespace = self.namespace,
                                       cache_id  = cache_id      ,
                                       recursive = True          )

            assert list_result                  is not None
            assert list_result.cache_id         == cache_id
            assert list_result.file_count       >= 2
            assert list_result.total_size       >  0

            # List specific key path
            list_filtered = _.data__list(namespace = self.namespace,
                                         cache_id  = cache_id      ,
                                         data_key  = 'layer-html'  ,
                                         recursive = True          )

            assert list_filtered.file_count     >= 1

            # ═══════════════════════════════════════════════════════════════════
            # Retrieve data files
            # ═══════════════════════════════════════════════════════════════════

            assert _.data__retrieve_string(namespace    = self.namespace,
                                           cache_id     = cache_id      ,
                                           data_key     = 'layer-html'  ,
                                           data_file_id = 'content'     ) == '<html>test</html>'

            assert _.data__retrieve_json(namespace    = self.namespace  ,
                                         cache_id     = cache_id        ,
                                         data_key     = 'layer-metadata',
                                         data_file_id = 'meta'          ) == {'title': 'Test'}

            assert _.data__retrieve_string(namespace    = self.namespace,
                                           cache_id     = cache_id      ,
                                           data_key     = 'layer-html'  ,
                                           data_file_id = 'non-existent') is None

            # ═══════════════════════════════════════════════════════════════════
            # Update data files
            # ═══════════════════════════════════════════════════════════════════

            assert _.data__update_string(namespace    = self.namespace         ,
                                         cache_id     = cache_id               ,
                                         data_key     = 'layer-html'           ,
                                         data_file_id = 'content'              ,
                                         content      = '<html>updated</html>') is True

            assert _.data__update_json(namespace    = self.namespace         ,
                                       cache_id     = cache_id               ,
                                       data_key     = 'layer-metadata'       ,
                                       data_file_id = 'meta'                 ,
                                       data         = {'title': 'Updated'}   ) is True

            # Verify updates persisted
            assert _.data__retrieve_string(namespace    = self.namespace,
                                           cache_id     = cache_id      ,
                                           data_key     = 'layer-html'  ,
                                           data_file_id = 'content'     ) == '<html>updated</html>'

            assert _.data__retrieve_json(namespace    = self.namespace  ,
                                         cache_id     = cache_id        ,
                                         data_key     = 'layer-metadata',
                                         data_file_id = 'meta'          ) == {'title': 'Updated'}

            # Update non-existent file returns False
            assert _.data__update_string(namespace    = self.namespace  ,
                                         cache_id     = cache_id        ,
                                         data_key     = 'layer-html'    ,
                                         data_file_id = 'non-existent'  ,
                                         content      = 'should fail'   ) is False

            # ═══════════════════════════════════════════════════════════════════
            # Delete data files
            # ═══════════════════════════════════════════════════════════════════

            assert _.data__delete(namespace    = self.namespace              ,
                                  cache_id     = cache_id                    ,
                                  data_key     = 'layer-html'                ,
                                  data_file_id = 'content'                   ,
                                  data_type    = Enum__Cache__Data_Type.STRING) is True

            # Verify deletion
            assert _.data__exists(namespace    = self.namespace              ,
                                  cache_id     = cache_id                    ,
                                  data_key     = 'layer-html'                ,
                                  data_file_id = 'content'                   ,
                                  data_type    = Enum__Cache__Data_Type.STRING) is False

            assert _.data__retrieve_string(namespace    = self.namespace,
                                           cache_id     = cache_id      ,
                                           data_key     = 'layer-html'  ,
                                           data_file_id = 'content'     ) is None

            # Delete again returns False (idempotent)
            assert _.data__delete(namespace    = self.namespace              ,
                                  cache_id     = cache_id                    ,
                                  data_key     = 'layer-html'                ,
                                  data_file_id = 'content'                   ,
                                  data_type    = Enum__Cache__Data_Type.STRING) is False

            # Other data file still exists
            assert _.data__exists(namespace    = self.namespace            ,
                                  cache_id     = cache_id                  ,
                                  data_key     = 'layer-metadata'          ,
                                  data_file_id = 'meta'                    ,
                                  data_type    = Enum__Cache__Data_Type.JSON) is True

            # ═══════════════════════════════════════════════════════════════════
            # Cleanup parent entry
            # ═══════════════════════════════════════════════════════════════════

            assert _.entry__delete(namespace = self.namespace, cache_id = cache_id) is True
            assert _.entry__exists(namespace = self.namespace, cache_id = cache_id) is False