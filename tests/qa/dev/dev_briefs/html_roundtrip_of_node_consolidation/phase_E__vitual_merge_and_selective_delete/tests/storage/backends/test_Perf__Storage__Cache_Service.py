# ═══════════════════════════════════════════════════════════════════════════════
# test_Perf__Storage__Cache_Service - Tests for cache service storage backend
# Uses in-memory cache service for fast, real API testing
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                               import TestCase
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.utils.Misc                                                                 import is_guid
from osbot_utils.utils.Objects                                                              import base_types
from phase_e.storage.base.Perf__Storage__Base                                               import Perf__Storage__Base
from phase_e.storage.backends.Perf__Storage__Cache_Service                                  import Perf__Storage__Cache_Service
from phase_e.storage.cache_service.Cache_Service__Client                                    import Cache_Service__Client
from phase_e.storage.schemas.Schema__Perf__Storage__Config                                  import Schema__Perf__Storage__Config
from phase_e.storage.enums.Enum__Storage_Mode                                               import Enum__Storage_Mode
from tests.Phase_E__Fast_API__Test_Objs                                                     import client_cache_service


class test_Perf__Storage__Cache_Service(TestCase):

    @classmethod
    def setUpClass(cls):                                                                    # Shared setup - in-memory cache
        cls.cache_namespace = 'test_namespace'
        cls.session_name    = 'test_session'
        cls.target_name     = 'test_target'
        cls.config          = Schema__Perf__Storage__Config(storage_mode    = Enum__Storage_Mode.CACHE_SERVICE,
                                                            cache_namespace = cls.cache_namespace             )

        cls.cache_client, cls.cache_service = client_cache_service()                        # In-memory cache service
        cls.cache_client_wrapper            = Cache_Service__Client(cache_client=cls.cache_client)
        cls.perf_cache_service              = Perf__Storage__Cache_Service(config       = cls.config              ,
                                                                           client       = cls.cache_client_wrapper,
                                                                           session_name = cls.session_name        ,
                                                                           target_name  = cls.target_name         )

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                 # Test auto-initialization
        with self.perf_cache_service as _:
            assert type(_)       is Perf__Storage__Cache_Service
            assert base_types(_) == [Perf__Storage__Base, Type_Safe, object]
            assert _.config      == self.config
            assert _.client      == self.cache_client_wrapper

    def test__init____session_target(self):                                                 # Test session/target set
        with self.perf_cache_service as _:
            assert _.session_name == 'test_session'
            assert _.target_name  == 'test_target'

    # ═══════════════════════════════════════════════════════════════════════════
    # Cache Key/Hash Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_cache_key(self):                                                               # Test cache key generation
        with self.perf_cache_service as _:
            cache_key = _.cache_key()
            assert cache_key == f'sessions/{self.session_name}/targets/{self.target_name}'

    def test_cache_hash(self):                                                              # Test cache hash generation
        with self.perf_cache_service as _:
            cache_hash = _.cache_hash()
            assert cache_hash is not None
            assert len(cache_hash) == 16                                                    # SHA-256 truncated to 16

    # ═══════════════════════════════════════════════════════════════════════════
    # Ensure Entry Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_ensure_entry__creates_new(self):                                               # Test ensure_entry creates entry
        cache_key = f'sessions/{self.session_name}/targets/{self.target_name}'

        with self.perf_cache_service as _:
            assert _.cache_key() == cache_key

            cache_id = _.ensure_entry()

            assert is_guid(cache_id) is True
            assert _.client.find_entry_by_key(cache_key=cache_key) == cache_id              # Entry now findable

    def test_ensure_entry__finds_existing(self):                                            # Test ensure_entry finds existing
        with self.perf_cache_service as _:
            cache_id_1 = _.ensure_entry()
            cache_id_2 = _.ensure_entry()

            assert cache_id_1 == cache_id_2                                                 # Same cache ID returned

    # ═══════════════════════════════════════════════════════════════════════════
    # Parse Key Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_parse_key__with_path(self):                                                    # Test parse_key with directory
        with self.perf_cache_service as _:
            data_key, file_id = _.parse_key('results/test.json')

            assert data_key == 'results'
            assert file_id  == 'test.json'

    def test_parse_key__without_path(self):                                                 # Test parse_key no directory
        with self.perf_cache_service as _:
            data_key, file_id = _.parse_key('simple.json')

            assert data_key == ''
            assert file_id  == 'simple.json'

    def test_parse_key__nested_path(self):                                                  # Test parse_key nested path
        with self.perf_cache_service as _:
            data_key, file_id = _.parse_key('results/detailed/analysis.json')

            assert data_key == 'results/detailed'
            assert file_id  == 'analysis.json'

    # ═══════════════════════════════════════════════════════════════════════════
    # Save/Load JSON Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_save(self):                                                                    # Test save JSON data
        with self.perf_cache_service as _:
            result = _.save('results/data.json', {'key': 'value', 'count': 42})

            assert result is True

    def test_load(self):                                                                    # Test load JSON data
        with self.perf_cache_service as _:
            test_data = {'loaded': 'data', 'numbers': [1, 2, 3]}
            _.save('results/load_test.json', test_data)

            loaded = _.load('results/load_test.json')

            assert loaded == test_data

    def test_load__not_found(self):                                                         # Test load returns None
        with self.perf_cache_service as _:
            result = _.load('nonexistent/missing.json')

            assert result is None

    # ═══════════════════════════════════════════════════════════════════════════
    # Save/Load String Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_save_string(self):                                                             # Test save string content
        with self.perf_cache_service as _:
            result = _.save_string('results/output.txt', 'Hello from cache service!')

            assert result is True

    def test_load_string(self):                                                             # Test load string content
        with self.perf_cache_service as _:
            content = '# Report\n\nThis is the report content.'
            _.save_string('reports/report.md', content)

            loaded = _.load_string('reports/report.md')

            assert loaded == content

    def test_load_string__not_found(self):                                                  # Test load_string returns None
        with self.perf_cache_service as _:
            result = _.load_string('nonexistent/missing.txt')

            assert result == ''

    # ═══════════════════════════════════════════════════════════════════════════
    # Exists/Delete Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_exists__true(self):                                                            # Test exists returns True
        with self.perf_cache_service as _:
            _.save('results/exists_test.json', {'test': True})

            assert _.exists('results/exists_test.json') is True

    def test_exists__false(self):                                                           # Test exists returns False
        with self.perf_cache_service as _:
            assert _.exists('nonexistent/file.json') is False

    def test_delete(self):                                                                  # Test delete removes data
        with self.perf_cache_service as _:
            _.save_string('results/to_delete.txt', 'Delete me')

            assert _.exists('results/to_delete.txt'        ) is True

            assert _.delete__string('results/to_delete.txt') is True

            assert _.exists('results/to_delete.txt'         ) is False

    # ═══════════════════════════════════════════════════════════════════════════
    # List Keys Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_list_keys(self):                                                               # Test list_keys returns empty
        with self.perf_cache_service as _:
            result = _.list_keys()
            assert result == []                                                             # TODO: implement via refs API

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_integration__full_workflow(self):                                              # Test complete workflow
        with self.perf_cache_service as _:
            # Save JSON
            _.save('results/metrics.json', {'latency_ms': 42, 'throughput': 1000})

            # Save string
            _.save_string('results/summary.txt', 'Performance test completed successfully')

            # Save report
            _.save_string('reports/analysis.md', '# Analysis\n\nAll tests passed.')

            # Verify all exist
            assert _.exists('results/metrics.json')   is True
            assert _.exists('results/summary.txt')    is True
            assert _.exists('reports/analysis.md')    is True

            # Load and verify
            metrics = _.load('results/metrics.json')
            assert metrics['latency_ms'] == 42

            summary = _.load_string('results/summary.txt')
            assert 'completed successfully' in summary

            report = _.load_string('reports/analysis.md')
            assert '# Analysis' in report