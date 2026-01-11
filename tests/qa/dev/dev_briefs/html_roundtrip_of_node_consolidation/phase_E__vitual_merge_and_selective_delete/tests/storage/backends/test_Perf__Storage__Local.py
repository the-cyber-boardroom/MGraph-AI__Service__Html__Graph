# ═══════════════════════════════════════════════════════════════════════════════
# test_Perf__Storage__Local - Tests for local disk storage backend
# ═══════════════════════════════════════════════════════════════════════════════

import os
import tempfile
import shutil
from unittest                                                                   import TestCase
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.utils.Files                                                    import file_exists, folder_exists
from phase_e.storage.base.Perf__Storage__Base                                   import Perf__Storage__Base
from phase_e.storage.backends.Perf__Storage__Local                              import Perf__Storage__Local
from phase_e.storage.safe_str.Safe_Str__Session_Name                            import Safe_Str__Session_Name
from phase_e.storage.safe_str.Safe_Str__Target_Name                             import Safe_Str__Target_Name


class test_Perf__Storage__Local(TestCase):
    
    @classmethod
    def setUpClass(cls):                                                        # Create temp directory for tests
        cls.temp_dir = tempfile.mkdtemp(prefix='perf_storage_test_')
        cls.storage  = Perf__Storage__Local(storage_path=cls.temp_dir)
        cls.storage.set_context('test_session', 'test_target')
    
    @classmethod
    def tearDownClass(cls):                                                     # Cleanup temp directory
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)
    
    def tearDown(self):                                                         # Clean context folder after each test
        context_path = self.storage.context_path()
        if folder_exists(context_path):
            shutil.rmtree(context_path)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════
    
    def test__init__(self):                                                     # Test auto-initialization
        with Perf__Storage__Local() as _:
            assert type(_)           is Perf__Storage__Local
            assert _.storage_path    == './perf_results'                        # Default path
            assert issubclass(type(_), Perf__Storage__Base)
            assert issubclass(type(_), Type_Safe)
    
    def test__init____with_storage_path(self):                                  # Test custom storage path
        with Perf__Storage__Local(storage_path='/tmp/custom_path') as _:
            assert _.storage_path == '/tmp/custom_path'
    
    def test__init____with_context(self):                                       # Test context initialization
        with Perf__Storage__Local() as _:
            _.set_context('my_session', 'my_target')
            
            assert type(_.session_name) is Safe_Str__Session_Name
            assert type(_.target_name)  is Safe_Str__Target_Name
            assert _.session_name       == 'my_session'
            assert _.target_name        == 'my_target'
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Path Helper Tests
    # ═══════════════════════════════════════════════════════════════════════════
    
    def test_context_path(self):                                                # Test context path generation
        with self.storage as _:
            result = _.context_path()
            expected = f"{self.temp_dir}/sessions/test_session/targets/test_target"
            assert result == expected
    
    def test_full_path(self):                                                   # Test full path generation
        with self.storage as _:
            result = _.full_path('results/test.json')
            expected = f"{self.temp_dir}/sessions/test_session/targets/test_target/results/test.json"
            assert result == expected
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Save/Load JSON Tests
    # ═══════════════════════════════════════════════════════════════════════════
    
    def test_save(self):                                                        # Test JSON save creates file
        with self.storage as _:
            result = _.save('results/test.json', {'value': 42, 'name': 'test'})
            
            assert result is True
            assert _.exists('results/test.json') is True
            assert file_exists(_.full_path('results/test.json')) is True
    
    def test_load(self):                                                        # Test JSON load reads file
        with self.storage as _:
            _.save('results/load_test.json', {'key': 'value', 'count': 100})
            data = _.load('results/load_test.json')
            
            assert data       == {'key': 'value', 'count': 100}
            assert type(data) is dict
    
    def test_load__not_found(self):                                             # Test load returns None for missing
        with self.storage as _:
            result = _.load('nonexistent/file.json')
            assert result is None
    
    def test_save__nested_directories(self):                                    # Test save creates nested dirs
        with self.storage as _:
            result = _.save('deep/nested/path/data.json', {'deep': True})
            
            assert result is True
            assert _.exists('deep/nested/path/data.json') is True
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Save/Load String Tests
    # ═══════════════════════════════════════════════════════════════════════════
    
    def test_save_string(self):                                                 # Test string save
        with self.storage as _:
            result = _.save_string('results/test.txt', 'Hello World')
            
            assert result is True
            assert _.exists('results/test.txt') is True
    
    def test_load_string(self):                                                 # Test string load
        with self.storage as _:
            content = '# Report\n\nThis is content with unicode: café ☕'
            _.save_string('reports/report.md', content)
            loaded = _.load_string('reports/report.md')
            
            assert loaded       == content
            assert type(loaded) is str
    
    def test_load_string__not_found(self):                                      # Test load_string returns None
        with self.storage as _:
            result = _.load_string('nonexistent/file.txt')
            assert result is None
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Exists/Delete Tests
    # ═══════════════════════════════════════════════════════════════════════════
    
    def test_exists__true(self):                                                # Test exists returns True
        with self.storage as _:
            _.save('results/exists_test.json', {})
            assert _.exists('results/exists_test.json') is True
    
    def test_exists__false(self):                                               # Test exists returns False
        with self.storage as _:
            assert _.exists('nonexistent/file.json') is False
    
    def test_delete(self):                                                      # Test delete removes file
        with self.storage as _:
            _.save('results/delete_test.json', {'temp': True})
            full_path = _.full_path('results/delete_test.json')
            
            assert file_exists(full_path) is True
            result = _.delete('results/delete_test.json')
            assert result is True
            assert file_exists(full_path) is False
    
    def test_delete__not_found(self):                                           # Test delete returns False
        with self.storage as _:
            result = _.delete('nonexistent/file.json')
            assert result is False
    
    # ═══════════════════════════════════════════════════════════════════════════
    # List Keys Tests
    # ═══════════════════════════════════════════════════════════════════════════
    
    def test_list_keys(self):                                                   # Test list all keys
        with self.storage as _:
            _.save('results/a.json', {})
            _.save('results/b.json', {})
            _.save_string('reports/c.md', '# Report')
            
            keys = _.list_keys()
            
            assert 'results/a.json' in keys
            assert 'results/b.json' in keys
            assert 'reports/c.md'   in keys
            assert len(keys)        == 3
    
    def test_list_keys__with_prefix(self):                                      # Test list keys with prefix
        with self.storage as _:
            _.save('results/a.json', {})
            _.save('results/b.json', {})
            _.save_string('reports/c.md', '# Report')
            
            result_keys = _.list_keys('results/')
            
            assert 'results/a.json' in result_keys
            assert 'results/b.json' in result_keys
            assert len(result_keys) == 2
    
    def test_list_keys__empty(self):                                            # Test list keys when empty
        with self.storage as _:
            keys = _.list_keys()
            assert keys == []
    
    def test_list_keys__nested(self):                                           # Test list keys with nested paths
        with self.storage as _:
            _.save('results/quick/a.json', {})
            _.save('results/detailed/b.json', {})
            _.save('results/c.json', {})
            
            keys = _.list_keys()
            
            assert 'results/quick/a.json'    in keys
            assert 'results/detailed/b.json' in keys
            assert 'results/c.json'          in keys
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Context Isolation Tests
    # ═══════════════════════════════════════════════════════════════════════════
    
    def test_context_isolation(self):                                           # Test contexts are isolated
        with Perf__Storage__Local(storage_path=self.temp_dir) as _:
            _.set_context('session_a', 'target_x')
            _.save('data.json', {'context': 'a-x'})
            
            _.set_context('session_b', 'target_y')
            _.save('data.json', {'context': 'b-y'})
            
            _.set_context('session_a', 'target_x')
            assert _.load('data.json') == {'context': 'a-x'}
            
            _.set_context('session_b', 'target_y')
            assert _.load('data.json') == {'context': 'b-y'}
            
            # Cleanup
            shutil.rmtree(f"{self.temp_dir}/sessions/session_a", ignore_errors=True)
            shutil.rmtree(f"{self.temp_dir}/sessions/session_b", ignore_errors=True)
