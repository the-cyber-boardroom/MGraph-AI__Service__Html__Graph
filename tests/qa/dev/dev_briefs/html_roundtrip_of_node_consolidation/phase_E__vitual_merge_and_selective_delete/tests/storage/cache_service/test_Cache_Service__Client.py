# ═══════════════════════════════════════════════════════════════════════════════
# test_Cache_Service__Client - Tests for cache service client wrapper
# Uses in-memory cache service for fast, real API testing
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                               import TestCase

from mgraph_ai_service_cache_client.schemas.cache.data.Schema__Cache__Data__Store__Response import Schema__Cache__Data__Store__Response
from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type import Enum__Cache__Data_Type

from osbot_utils.helpers.cache.Cache__Hash__Generator                                       import Cache__Hash__Generator
from osbot_utils.testing.__ import __, __SKIP__
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                          import Cache_Id
from osbot_utils.utils.Misc                                                                 import is_guid
from osbot_utils.utils.Objects                                                              import base_types
from mgraph_ai_service_cache_client.client.client_contract.Cache__Service__Fast_API__Client import Cache__Service__Fast_API__Client
from phase_e.storage.cache_service.Cache_Service__Client                                    import Cache_Service__Client
from phase_e.storage.safe_str.Safe_Str__Data_Key                                            import Safe_Str__Data_Key
from phase_e.storage.safe_str.Safe_Str__Data_File_Id                                        import Safe_Str__Data_File_Id
from phase_e.storage.schemas.Schema__Perf__Storage__Config                                  import Schema__Perf__Storage__Config
from phase_e.storage.schemas.Schema__Perf__Entry                                            import Schema__Perf__Entry
from phase_e.storage.enums.Enum__Storage_Mode                                               import Enum__Storage_Mode
from tests.Phase_E__Fast_API__Test_Objs import client_cache_service


class test_Cache_Service__Client(TestCase):

    @classmethod
    def setUpClass(cls):                                                                    # Shared setup - in-memory cache
        cls.cache_namespace                     = 'test_namespace'
        cls.config                              = Schema__Perf__Storage__Config(storage_mode    = Enum__Storage_Mode.CACHE_SERVICE,
                                                                                cache_namespace = cls.cache_namespace             )
        cls.cache_client, cls.cache_service     = client_cache_service()                    # In-memory cache service
        cls.client                              = Cache_Service__Client(config       = cls.config      ,
                                                                        cache_client = cls.cache_client)

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                 # Test auto-initialization
        with self.client as _:
            assert type(_)               is Cache_Service__Client
            assert base_types(_)         == [Type_Safe, object]
            assert _.config              == self.config
            assert _.cache_client        == self.cache_client
            assert type(_.hash_generator) is Cache__Hash__Generator

    def test__init____config(self):                                                         # Test config attributes
        with self.client as _:
            assert _.config.storage_mode    == Enum__Storage_Mode.CACHE_SERVICE
            assert _.config.cache_namespace == 'test_namespace'

    def test__init____cache_client(self):                                                   # Test cache client is connected
        with self.client as _:
            assert type(_.cache_client) is Cache__Service__Fast_API__Client

    # ═══════════════════════════════════════════════════════════════════════════
    # Store Entry Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_store_entry(self):                                                             # Test store_entry creates entry
        cache_key  = 'sessions/store_test/targets/default'
        perf_entry = Schema__Perf__Entry(session_name = 'store_test',
                                         target_name  = 'default'   ,
                                         cache_key    = cache_key   )

        with self.client as _:
            result = _.store_entry(cache_key       = cache_key                           ,
                                   file_id         = Safe_Str__Data_File_Id('perf-entry'),
                                   json_field_path = 'cache_key'                         ,
                                   perf_entry      = perf_entry                          )

            assert result.cache_id          is not None
            assert result.cache_hash        is not None
            assert is_guid(result.cache_id) is True
            assert result.cache_hash        == 'f850dd9eec32fadf'                           # value is deterministic

    def test_store_entry__same_key_returns_same_id(self):                                   # Test idempotent storage
        cache_key  = 'sessions/idempotent_test/targets/default'
        perf_entry = Schema__Perf__Entry(session_name = 'idempotent_test',
                                         target_name  = 'default'        ,
                                         cache_key    = cache_key        )

        with self.client as _:
            result1 = _.store_entry(cache_key       = cache_key                           ,
                                    file_id         = Safe_Str__Data_File_Id('perf-entry'),
                                    json_field_path = 'cache_key'                         ,
                                    perf_entry      = perf_entry                          )

            result2 = _.store_entry(cache_key       = cache_key                           ,
                                    file_id         = Safe_Str__Data_File_Id('perf-entry'),
                                    json_field_path = 'cache_key'                         ,
                                    perf_entry      = perf_entry                          )

            assert result1.cache_hash == result2.cache_hash                                 # Same hash

    # ═══════════════════════════════════════════════════════════════════════════
    # Retrieve Entry Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_retrieve_entry(self):                                                          # Test retrieve entry by ID
        cache_key  = 'sessions/retrieve_test/targets/default'
        perf_entry = Schema__Perf__Entry(session_name = 'retrieve_test',
                                         target_name  = 'default'      ,
                                         cache_key    = cache_key      )

        with self.client as _:
            store_result = _.store_entry(cache_key       = cache_key                           ,
                                         file_id         = Safe_Str__Data_File_Id('perf-entry'),
                                         json_field_path = 'cache_key'                         ,
                                         perf_entry      = perf_entry                          )

            retrieved = _.retrieve_entry(cache_id=store_result.cache_id)

            assert retrieved is not None
            assert retrieved['session_name'] == 'retrieve_test'
            assert retrieved['target_name']  == 'default'
            assert retrieved['cache_key']    == cache_key

    def test_retrieve_entry__not_found(self):                                               # Test retrieve returns None
        with self.client as _:
            result = _.retrieve_entry(cache_id=Cache_Id('00000000-0000-0000-0000-000000000000'))
            assert result is None

    # ═══════════════════════════════════════════════════════════════════════════
    # Hash Operations Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_hash_exists__true(self):                                                       # Test hash_exists returns True
        cache_key  = 'sessions/hash_exists_test/targets/default'
        perf_entry = Schema__Perf__Entry(session_name = 'hash_exists_test',
                                         target_name  = 'default'         ,
                                         cache_key    = cache_key         )

        with self.client as _:
            store_result = _.store_entry(cache_key       = cache_key                           ,
                                         file_id         = Safe_Str__Data_File_Id('perf-entry'),
                                         json_field_path = 'cache_key'                         ,
                                         perf_entry      = perf_entry                          )

            result = _.hash_exists(cache_hash=store_result.cache_hash)

            assert result['exists']     is True
            assert result['cache_hash'] == store_result.cache_hash
            assert result['namespace']  == self.cache_namespace

    def test_hash_exists__false(self):                                                      # Test hash_exists returns False
        with self.client as _:
            result = _.hash_exists(cache_hash='0000000000000000')

            assert result['exists'] is False

    # ═══════════════════════════════════════════════════════════════════════════
    # Find Entry By Key Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_find_entry_by_key(self):                                                       # Test find by semantic key
        cache_key  = 'sessions/find_test/targets/default'
        perf_entry = Schema__Perf__Entry(session_name = 'find_test',
                                         target_name  = 'default'  ,
                                         cache_key    = cache_key  )

        with self.client as _:
            store_result = _.store_entry(cache_key       = cache_key                           ,
                                         file_id         = Safe_Str__Data_File_Id('perf-entry'),
                                         json_field_path = 'cache_key'                         ,
                                         perf_entry      = perf_entry                          )

            found_id = _.find_entry_by_key(cache_key=cache_key)

            assert found_id == store_result.cache_id

    def test_find_entry_by_key__not_found(self):                                            # Test find returns None
        with self.client as _:
            result = _.find_entry_by_key(cache_key='nonexistent/path/here')
            assert result is None

    # ═══════════════════════════════════════════════════════════════════════════
    # Child Data Operations Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_store_child_string(self):                                                      # Test store child string
        cache_key  = 'sessions/child_string_test/targets/default'
        perf_entry = Schema__Perf__Entry(session_name = 'child_string_test',
                                         target_name  = 'default'          ,
                                         cache_key    = cache_key          )

        with self.client as _:
            store_result = _.store_entry(cache_key       = cache_key                           ,
                                         file_id         = Safe_Str__Data_File_Id('perf-entry'),
                                         json_field_path = 'cache_key'                         ,
                                         perf_entry      = perf_entry                          )

            result = _.store_child_string(cache_id     = store_result.cache_id           ,
                                          data_key     = Safe_Str__Data_Key('results')   ,
                                          data_file_id = Safe_Str__Data_File_Id('output.txt'),
                                          content      = 'Hello World from cache service')

            assert type(result) is Schema__Cache__Data__Store__Response
            assert result.obj() == __( cache_id           = store_result.cache_id,
                                       data_files_created = ['test_namespace/data/key-based/sessions/child_string_test/targets/default/perf-entry/data/results/output_txt.txt'],
                                       data_key     ='results',
                                       data_type    ='string',
                                       extension    ='txt',
                                       file_id      ='output_txt',
                                       file_size    =30,
                                       namespace    = 'test_namespace',
                                       timestamp    =__SKIP__)

    def test_store_child_json(self):                                                        # Test store child JSON
        cache_key  = 'sessions/child_json_test/targets/default'
        perf_entry = Schema__Perf__Entry(session_name = 'child_json_test',
                                         target_name  = 'default'        ,
                                         cache_key    = cache_key        )

        with self.client as _:
            store_result = _.store_entry(cache_key       = cache_key                           ,
                                         file_id         = Safe_Str__Data_File_Id('perf-entry'),
                                         json_field_path = 'cache_key'                         ,
                                         perf_entry      = perf_entry                          )

            result = _.store_child_json(cache_id     = store_result.cache_id              ,
                                        data_key     = Safe_Str__Data_Key('results')      ,
                                        data_file_id = Safe_Str__Data_File_Id('data.json'),
                                        data         = {'key': 'value', 'count': 42}      )

            assert type(result) is Schema__Cache__Data__Store__Response
            assert result.obj() == __(cache_id=store_result.cache_id,
                                     data_files_created=['test_namespace/data/key-based/sessions/child_json_test/targets/default/perf-entry/data/results/data_json.json'],
                                     data_key='results',
                                     data_type='json',
                                     extension='json',
                                     file_id='data_json',
                                     file_size=39,
                                     namespace='test_namespace',
                                     timestamp=__SKIP__)

    def test_retrieve_child_string(self):                                                   # Test retrieve child string
        cache_key  = 'sessions/retrieve_child_str/targets/default'
        perf_entry = Schema__Perf__Entry(session_name = 'retrieve_child_str',
                                         target_name  = 'default'           ,
                                         cache_key    = cache_key           )

        with self.client as _:
            store_result = _.store_entry(cache_key       = cache_key                           ,
                                         file_id         = Safe_Str__Data_File_Id('perf-entry'),
                                         json_field_path = 'cache_key'                         ,
                                         perf_entry      = perf_entry                          )

            content = 'Test content for retrieval'
            _.store_child_string(cache_id     = store_result.cache_id                ,
                                 data_key     = Safe_Str__Data_Key('results')        ,
                                 data_file_id = Safe_Str__Data_File_Id('retrieve.txt'),
                                 content      = content                              )

            retrieved = _.retrieve_child_string(cache_id     = store_result.cache_id                ,
                                                data_key     = Safe_Str__Data_Key('results')        ,
                                                data_file_id = Safe_Str__Data_File_Id('retrieve.txt'))

            assert retrieved == content

    def test_retrieve_child_string__not_found(self):                                        # Test retrieve returns None
        cache_key  = 'sessions/retrieve_child_none/targets/default'
        perf_entry = Schema__Perf__Entry(session_name = 'retrieve_child_none',
                                         target_name  = 'default'            ,
                                         cache_key    = cache_key            )

        with self.client as _:
            store_result = _.store_entry(cache_key       = cache_key                           ,
                                         file_id         = Safe_Str__Data_File_Id('perf-entry'),
                                         json_field_path = 'cache_key'                         ,
                                         perf_entry      = perf_entry                          )

            result = _.retrieve_child_string(cache_id     = store_result.cache_id               ,
                                             data_key     = Safe_Str__Data_Key('results')       ,
                                             data_file_id = Safe_Str__Data_File_Id('missing.txt'))

            assert result == ''

    def test_retrieve_child_json(self):                                                     # Test retrieve child JSON
        cache_key  = 'sessions/retrieve_child_json/targets/default'
        perf_entry = Schema__Perf__Entry(session_name = 'retrieve_child_json',
                                         target_name  = 'default'            ,
                                         cache_key    = cache_key            )

        with self.client as _:
            store_result = _.store_entry(cache_key       = cache_key                           ,
                                         file_id         = Safe_Str__Data_File_Id('perf-entry'),
                                         json_field_path = 'cache_key'                         ,
                                         perf_entry      = perf_entry                          )

            test_data = {'loaded': 'data', 'numbers': [1, 2, 3]}
            _.store_child_json(cache_id     = store_result.cache_id              ,
                               data_key     = Safe_Str__Data_Key('results')      ,
                               data_file_id = Safe_Str__Data_File_Id('load.json'),
                               data         = test_data                          )

            retrieved = _.retrieve_child_json(cache_id     = store_result.cache_id              ,
                                              data_key     = Safe_Str__Data_Key('results')      ,
                                              data_file_id = Safe_Str__Data_File_Id('load.json'))

            assert retrieved == test_data

    def test_delete_child(self):                                                            # Test delete child data
        cache_key  = 'sessions/delete_child_test/targets/default'
        perf_entry = Schema__Perf__Entry(session_name = 'delete_child_test',
                                         target_name  = 'default'          ,
                                         cache_key    = cache_key          )

        with self.client as _:
            store_result = _.store_entry(cache_key       = cache_key                           ,
                                         file_id         = Safe_Str__Data_File_Id('perf-entry'),
                                         json_field_path = 'cache_key'                         ,
                                         perf_entry      = perf_entry                          )

            _.store_child_string(cache_id     = store_result.cache_id                  ,
                                 data_key     = Safe_Str__Data_Key('results')          ,
                                 data_file_id = Safe_Str__Data_File_Id('to_delete.txt'),
                                 content      = 'Delete me'                            )

            # Verify it exists
            before = _.retrieve_child_string(cache_id     = store_result.cache_id                  ,
                                             data_key     = Safe_Str__Data_Key('results')          ,
                                             data_file_id = Safe_Str__Data_File_Id('to_delete.txt'))
            assert before == 'Delete me'

            # Delete it
            result = _.delete_child(cache_id     = store_result.cache_id                  ,
                                    data_key     = Safe_Str__Data_Key('results')          ,
                                    data_file_id = Safe_Str__Data_File_Id('to_delete.txt'),
                                    data_type    = Enum__Cache__Data_Type.STRING           )
            assert result is True

            # Verify it's gone
            after = _.retrieve_child_string(cache_id     = store_result.cache_id                  ,
                                            data_key     = Safe_Str__Data_Key('results')          ,
                                            data_file_id = Safe_Str__Data_File_Id('to_delete.txt'))
            assert after == ''

    # ═══════════════════════════════════════════════════════════════════════════
    # Health Check Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_health_check(self):                                                            # Test health check
        with self.client as _:
            result = _.health_check()
            assert result is True