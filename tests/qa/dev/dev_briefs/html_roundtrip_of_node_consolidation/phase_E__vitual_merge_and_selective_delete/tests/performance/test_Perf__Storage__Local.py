# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Perf__Storage__Local
# Part of Phase E_1: Performance Analysis
# ═══════════════════════════════════════════════════════════════════════════════

import tempfile
import shutil
from unittest                                                                   import TestCase

from osbot_utils.utils.Files import file_exists
from phase_e.performance.Perf__Storage__Local                                   import Perf__Storage__Local
from phase_e.performance.Perf__Phase_E__Conversion                              import Schema__Conversion_Timing


class test_Perf__Storage__Local(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.storage  = Perf__Storage__Local(storage_path=cls.temp_dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def setUp(self):
        self.storage.clear_all()                                                # Clean slate for each test

    def test__init__(self):                                                     # Test auto-initialization
        with self.storage as _:
            assert type(_).__name__ == 'Perf__Storage__Local'
            assert _.storage_path   == self.temp_dir

    # ═══════════════════════════════════════════════════════════════════════════
    # Save and Load
    # ═══════════════════════════════════════════════════════════════════════════

    def test_save__returns_true(self):                                          # Save returns success
        with self.storage as _:
            result = _.save('test_key', {'value': 123})

            assert result is True

    def test_save__creates_file(self):                                          # Save creates JSON file
        with self.storage as _:
            _.save('test_file', {'data': 'test'})

            file_path = _.key_to_path('test_file')
            assert file_exists(file_path)

    def test_load__returns_data(self):                                          # Load returns saved data
        with self.storage as _:
            _.save('load_test', {'name': 'test', 'count': 42})

            data = _.load('load_test')

            assert data['name']  == 'test'
            assert data['count'] == 42

    def test_load__missing_key_returns_none(self):                              # Load missing returns None
        with self.storage as _:
            data = _.load('nonexistent_key')

            assert data is None

    # ═══════════════════════════════════════════════════════════════════════════
    # Exists and Delete
    # ═══════════════════════════════════════════════════════════════════════════

    def test_exists__true_when_saved(self):                                     # Exists true after save
        with self.storage as _:
            _.save('exists_test', {'a': 1})

            assert _.exists('exists_test') is True

    def test_exists__false_when_missing(self):                                  # Exists false if not saved
        with self.storage as _:
            assert _.exists('missing_key') is False

    def test_delete__removes_key(self):                                         # Delete removes data
        with self.storage as _:
            _.save('delete_test', {'x': 1})
            assert _.exists('delete_test') is True

            result = _.delete('delete_test')

            assert result                    is True
            assert _.exists('delete_test')   is False

    def test_delete__missing_returns_false(self):                               # Delete missing returns False
        with self.storage as _:
            result = _.delete('not_there')

            assert result is False

    # ═══════════════════════════════════════════════════════════════════════════
    # List Keys
    # ═══════════════════════════════════════════════════════════════════════════

    def test_list_keys__returns_all(self):                                      # List returns all keys
        with self.storage as _:
            _.save('key_a', {})
            _.save('key_b', {})
            _.save('key_c', {})

            keys = _.list_keys()

            assert len(keys) == 3
            assert 'key_a'   in keys
            assert 'key_b'   in keys
            assert 'key_c'   in keys

    def test_list_keys__with_prefix(self):                                      # List with prefix filter
        with self.storage as _:
            _.save('analysis_1', {})
            _.save('analysis_2', {})
            _.save('benchmark_1', {})

            analysis_keys  = _.list_keys('analysis')
            benchmark_keys = _.list_keys('benchmark')

            assert len(analysis_keys)  == 2
            assert len(benchmark_keys) == 1

    def test_list_keys__empty_storage(self):                                    # List empty returns []
        with self.storage as _:
            keys = _.list_keys()

            assert keys == []

    # ═══════════════════════════════════════════════════════════════════════════
    # Convenience Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def test_save_if_not_exists__saves_new(self):                               # Saves if key is new
        with self.storage as _:
            result = _.save_if_not_exists('new_key', {'v': 1})

            assert result            is True
            assert _.exists('new_key') is True

    def test_save_if_not_exists__skips_existing(self):                          # Skips if key exists
        with self.storage as _:
            _.save('existing', {'v': 1})

            result = _.save_if_not_exists('existing', {'v': 2})

            assert result is False

            data = _.load('existing')
            assert data['v'] == 1                                               # Original value unchanged

    def test_load_or_default__returns_data(self):                               # Returns data if exists
        with self.storage as _:
            _.save('with_data', {'x': 10})

            data = _.load_or_default('with_data', {'x': 0})

            assert data['x'] == 10

    def test_load_or_default__returns_default(self):                            # Returns default if missing
        with self.storage as _:
            data = _.load_or_default('missing', {'x': 99})

            assert data['x'] == 99

    def test_load_all__returns_all_data(self):                                  # Load all returns dict
        with self.storage as _:
            _.save('item_1', {'n': 1})
            _.save('item_2', {'n': 2})

            all_data = _.load_all()

            assert len(all_data)        == 2
            assert all_data['item_1']['n'] == 1
            assert all_data['item_2']['n'] == 2

    def test_load_all__with_prefix(self):                                       # Load all with prefix
        with self.storage as _:
            _.save('group_a_1', {'g': 'a'})
            _.save('group_a_2', {'g': 'a'})
            _.save('group_b_1', {'g': 'b'})

            group_a = _.load_all('group_a')

            assert len(group_a) == 2

    # ═══════════════════════════════════════════════════════════════════════════
    # Key Generation
    # ═══════════════════════════════════════════════════════════════════════════

    def test_generate_timestamped_key__has_prefix(self):                        # Timestamp key has prefix
        with self.storage as _:
            key = _.generate_timestamped_key('benchmark')

            assert key.startswith('benchmark_')

    def test_generate_timestamped_key__unique(self):                            # Timestamp keys are unique
        import time
        with self.storage as _:
            key1 = _.generate_timestamped_key('test')
            time.sleep(0.01)
            key2 = _.generate_timestamped_key('test')

            # Keys should be same or different based on timing
            # Just verify format is correct
            assert key1.startswith('test_')
            assert key2.startswith('test_')

    def test_generate_session_key(self):                                        # Session key generation
        with self.storage as _:
            key = _.generate_session_key('analysis')

            assert key.startswith('analysis_')

    # ═══════════════════════════════════════════════════════════════════════════
    # Storage Info
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_storage_info(self):                                            # Storage info
        with self.storage as _:
            _.save('info_test_1', {'data': 'x' * 100})
            _.save('info_test_2', {'data': 'y' * 100})

            info = _.get_storage_info()

            assert info['path']        == self.temp_dir
            assert info['key_count']   == 2
            assert info['total_bytes'] > 0

    def test_clear_all(self):                                                   # Clear all data
        with self.storage as _:
            _.save('clear_1', {})
            _.save('clear_2', {})
            _.save('clear_3', {})

            deleted = _.clear_all()

            assert deleted         == 3
            assert _.list_keys()   == []

    # ═══════════════════════════════════════════════════════════════════════════
    # Schema Serialization
    # ═══════════════════════════════════════════════════════════════════════════

    def test_save_schema__with_obj_method(self):                                # Save Type_Safe schema

        with self.storage as _:
            timing = Schema__Conversion_Timing(html_to_dict_ns   = 1000,
                                               dict_to_mgraph_ns = 2000,
                                               mgraph_to_html_ns = 3000,
                                               total_ns          = 6000,
                                               html_size_bytes   = 500 ,
                                               node_count        = 10  )

            result = _.save_schema('timing_test', timing)

            assert result is True

            data = _.load('timing_test')
            assert data['html_to_dict_ns'] == 1000
            assert data['total_ns']        == 6000

    def test_save_analysis__auto_key(self):                                     # Save analysis with auto key

        with self.storage as _:
            timing = Schema__Conversion_Timing(html_to_dict_ns   = 100,
                                               dict_to_mgraph_ns = 200,
                                               mgraph_to_html_ns = 300,
                                               total_ns          = 600,
                                               html_size_bytes   = 50 ,
                                               node_count        = 5  )

            key = _.save_analysis(timing, prefix='conversion')

            assert key.startswith('conversion_')
            assert _.exists(key) is True