# # ═══════════════════════════════════════════════════════════════════════════════
# # test_Perf__Storage__Memory - Tests for in-memory storage backend
# # ═══════════════════════════════════════════════════════════════════════════════
#
# from unittest                                                                   import TestCase
# from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
# from phase_e.storage.base.Perf__Storage__Base                                   import Perf__Storage__Base
# from phase_e.storage.backends.Perf__Storage__Memory                             import Perf__Storage__Memory
# from phase_e.storage.safe_str.Safe_Str__Session_Name                            import Safe_Str__Session_Name
# from phase_e.storage.safe_str.Safe_Str__Target_Name                             import Safe_Str__Target_Name
#
#
# class test_Perf__Storage__Memory(TestCase):
#
#     @classmethod
#     def setUpClass(cls):                                                        # Shared setup
#         cls.storage = Perf__Storage__Memory()
#         cls.storage.set_context('test_session', 'test_target')
#
#     def setUp(self):                                                            # Clear data before each test
#         self.storage.clear_context()
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Initialization Tests
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     def test__init__(self):                                                     # Test auto-initialization
#         with Perf__Storage__Memory() as _:
#             assert type(_)               is Perf__Storage__Memory
#             assert type(_.data)          is dict
#             assert _.data                == {}
#             assert issubclass(type(_), Perf__Storage__Base)
#             assert issubclass(type(_), Type_Safe)
#
#     def test__init____with_context(self):                                       # Test context initialization
#         with Perf__Storage__Memory() as _:
#             _.set_context('session_a', 'target_b')
#
#             assert type(_.session_name) is Safe_Str__Session_Name
#             assert type(_.target_name)  is Safe_Str__Target_Name
#             assert _.session_name       == 'session_a'
#             assert _.target_name        == 'target_b'
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Path Helper Tests
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     def test_context_key(self):                                                 # Test context key generation
#         with self.storage as _:
#             result = _.context_key()
#             assert result == 'test_session/test_target'
#
#     def test_full_key(self):                                                    # Test full key generation
#         with self.storage as _:
#             result = _.full_key('results/test.json')
#             assert result == 'test_session/test_target/results/test.json'
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Save/Load JSON Tests
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     def test_save(self):                                                        # Test JSON save
#         with self.storage as _:
#             result = _.save('results/test.json', {'value': 42})
#
#             assert result is True
#             assert _.exists('results/test.json') is True
#
#     def test_load(self):                                                        # Test JSON load
#         with self.storage as _:
#             _.save('results/load_test.json', {'key': 'value', 'count': 100})
#             data = _.load('results/load_test.json')
#
#             assert data                == {'key': 'value', 'count': 100}
#             assert type(data)          is dict
#
#     def test_load__not_found(self):                                             # Test load returns None for missing
#         with self.storage as _:
#             result = _.load('nonexistent/file.json')
#             assert result is None
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Save/Load String Tests
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     def test_save_string(self):                                                 # Test string save
#         with self.storage as _:
#             result = _.save_string('results/test.txt', 'Hello World')
#
#             assert result is True
#             assert _.exists('results/test.txt') is True
#
#     def test_load_string(self):                                                 # Test string load
#         with self.storage as _:
#             _.save_string('reports/report.md', '# Report\n\nContent here')
#             content = _.load_string('reports/report.md')
#
#             assert content == '# Report\n\nContent here'
#             assert type(content) is str
#
#     def test_load_string__not_found(self):                                      # Test load_string returns None
#         with self.storage as _:
#             result = _.load_string('nonexistent/file.txt')
#             assert result is None
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Exists/Delete Tests
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     def test_exists__true(self):                                                # Test exists returns True
#         with self.storage as _:
#             _.save('results/exists_test.json', {})
#             assert _.exists('results/exists_test.json') is True
#
#     def test_exists__false(self):                                               # Test exists returns False
#         with self.storage as _:
#             assert _.exists('nonexistent/file.json') is False
#
#     def test_delete(self):                                                      # Test delete removes key
#         with self.storage as _:
#             _.save('results/delete_test.json', {'temp': True})
#
#             assert _.exists('results/delete_test.json') is True
#             result = _.delete('results/delete_test.json')
#             assert result is True
#             assert _.exists('results/delete_test.json') is False
#
#     def test_delete__not_found(self):                                           # Test delete returns False
#         with self.storage as _:
#             result = _.delete('nonexistent/file.json')
#             assert result is False
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # List Keys Tests
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     def test_list_keys(self):                                                   # Test list all keys
#         with self.storage as _:
#             _.save('results/a.json', {})
#             _.save('results/b.json', {})
#             _.save('reports/c.md'  , {})
#
#             keys = _.list_keys()
#
#             assert 'results/a.json' in keys
#             assert 'results/b.json' in keys
#             assert 'reports/c.md'   in keys
#             assert len(keys)        == 3
#
#     def test_list_keys__with_prefix(self):                                      # Test list keys with prefix filter
#         with self.storage as _:
#             _.save('results/a.json', {})
#             _.save('results/b.json', {})
#             _.save('reports/c.md'  , {})
#
#             result_keys = _.list_keys('results/')
#
#             assert 'results/a.json' in result_keys
#             assert 'results/b.json' in result_keys
#             assert 'reports/c.md'   not in result_keys
#             assert len(result_keys) == 2
#
#     def test_list_keys__empty(self):                                            # Test list keys when empty
#         with self.storage as _:
#             keys = _.list_keys()
#             assert keys == []
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Memory-Specific Tests
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     def test_clear(self):                                                       # Test clear all data
#         with Perf__Storage__Memory() as _:
#             _.set_context('session_1', 'target_1')
#             _.save('test.json', {'a': 1})
#             _.set_context('session_2', 'target_2')
#             _.save('test.json', {'b': 2})
#
#             assert len(_.data) == 2
#             _.clear()
#             assert len(_.data) == 0
#
#     def test_clear_context(self):                                               # Test clear only current context
#         with Perf__Storage__Memory() as _:
#             _.set_context('session_1', 'target_1')
#             _.save('test.json', {'a': 1})
#             _.set_context('session_2', 'target_2')
#             _.save('test.json', {'b': 2})
#
#             assert len(_.data) == 2
#             _.clear_context()                                                   # Clears session_2/target_2 only
#             assert len(_.data) == 1
#
#             _.set_context('session_1', 'target_1')
#             assert _.load('test.json') == {'a': 1}                              # session_1 data still exists
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Context Isolation Tests
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     def test_context_isolation(self):                                           # Test contexts are isolated
#         with Perf__Storage__Memory() as _:
#             _.set_context('session_a', 'target_x')
#             _.save('data.json', {'context': 'a-x'})
#
#             _.set_context('session_b', 'target_y')
#             _.save('data.json', {'context': 'b-y'})
#
#             _.set_context('session_a', 'target_x')
#             assert _.load('data.json') == {'context': 'a-x'}
#
#             _.set_context('session_b', 'target_y')
#             assert _.load('data.json') == {'context': 'b-y'}
