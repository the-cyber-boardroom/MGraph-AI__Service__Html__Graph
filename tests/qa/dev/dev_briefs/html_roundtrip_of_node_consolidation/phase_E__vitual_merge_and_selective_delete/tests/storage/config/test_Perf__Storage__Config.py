# ═══════════════════════════════════════════════════════════════════════════════
# test_Perf__Storage__Config - Tests for storage configuration manager
# ═══════════════════════════════════════════════════════════════════════════════

import os
from unittest                                                                   import TestCase
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from phase_e.storage.config.Perf__Storage__Config                               import Perf__Storage__Config
from phase_e.storage.schemas.Schema__Perf__Storage__Config                      import Schema__Perf__Storage__Config
from phase_e.storage.enums.Enum__Storage_Mode                                   import Enum__Storage_Mode


class test_Perf__Storage__Config(TestCase):
    
    def setUp(self):                                                            # Clear env vars before each test
        self.env_vars = ['PERF_STORAGE_MODE'      ,
                         'PERF_CACHE_NAMESPACE'   ,
                         'PERF_LOCAL_STORAGE_PATH']
        self.saved_env = {}
        for var in self.env_vars:
            self.saved_env[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]
    
    def tearDown(self):                                                         # Restore env vars after each test
        for var, value in self.saved_env.items():
            if value is None:
                if var in os.environ:
                    del os.environ[var]
            else:
                os.environ[var] = value
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════
    
    def test__init__(self):                                                     # Test auto-initialization
        with Perf__Storage__Config() as _:
            assert type(_) is Perf__Storage__Config
            assert issubclass(type(_), Type_Safe)
    
    def test_setup__defaults(self):                                             # Test setup with default values
        with Perf__Storage__Config() as _:
            _.setup()
            
            assert type(_.config)              is Schema__Perf__Storage__Config
            assert _.config.storage_mode       == Enum__Storage_Mode.LOCAL
            assert _.config.cache_namespace    == 'perf-results'
            assert _.config.local_storage_path == './perf_results'
    
    def test_setup__returns_self(self):                                         # Test setup returns self
        with Perf__Storage__Config() as _:
            result = _.setup()
            assert result is _
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Environment Variable Tests
    # ═══════════════════════════════════════════════════════════════════════════
    
    def test_setup__env_storage_mode_local(self):                               # Test env var: storage mode local
        os.environ['PERF_STORAGE_MODE'] = 'local'
        
        with Perf__Storage__Config() as _:
            _.setup()
            assert _.config.storage_mode == Enum__Storage_Mode.LOCAL
    
    def test_setup__env_storage_mode_memory(self):                              # Test env var: storage mode memory
        os.environ['PERF_STORAGE_MODE'] = 'memory'
        
        with Perf__Storage__Config() as _:
            _.setup()
            assert _.config.storage_mode == Enum__Storage_Mode.MEMORY
    
    def test_setup__env_storage_mode_cache_service(self):                       # Test env var: cache_service mode
        os.environ['PERF_STORAGE_MODE'] = 'cache_service'
        
        with Perf__Storage__Config() as _:
            _.setup()
            assert _.config.storage_mode == Enum__Storage_Mode.CACHE_SERVICE
    
    def test_setup__env_storage_mode_invalid(self):                             # Test env var: invalid mode
        os.environ['PERF_STORAGE_MODE'] = 'invalid_mode'
        
        with Perf__Storage__Config() as _:
            _.setup()
            assert _.config.storage_mode == Enum__Storage_Mode.LOCAL            # Falls back to LOCAL
    
    def test_setup__env_cache_namespace(self):                                  # Test env var: cache namespace
        os.environ['PERF_CACHE_NAMESPACE'] = 'custom-namespace'
        
        with Perf__Storage__Config() as _:
            _.setup()
            assert _.config.cache_namespace == 'custom-namespace'
    
    def test_setup__env_local_storage_path(self):                               # Test env var: local storage path
        os.environ['PERF_LOCAL_STORAGE_PATH'] = '/custom/path'
        
        with Perf__Storage__Config() as _:
            _.setup()
            assert _.config.local_storage_path == '/custom/path'
    
    def test_setup__all_env_vars(self):                                         # Test all env vars together
        os.environ['PERF_STORAGE_MODE']       = 'cache_service'
        os.environ['PERF_CACHE_NAMESPACE']    = 'production'
        os.environ['PERF_LOCAL_STORAGE_PATH'] = '/var/data/perf'
        
        with Perf__Storage__Config() as _:
            _.setup()
            
            assert _.config.storage_mode       == Enum__Storage_Mode.CACHE_SERVICE
            assert _.config.cache_namespace    == 'production'
            assert _.config.local_storage_path == '/var/data/perf'
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Config Schema Tests
    # ═══════════════════════════════════════════════════════════════════════════
    
    def test_config_schema_type(self):                                          # Test config attribute type
        with Perf__Storage__Config() as _:
            _.setup()
            assert type(_.config) is Schema__Perf__Storage__Config
    
    def test_config_schema_serializable(self):                                  # Test config is serializable
        with Perf__Storage__Config() as _:
            _.setup()
            json_data = _.config.json()
            
            assert type(json_data)         is dict
            assert 'storage_mode'          in json_data
            assert 'cache_namespace'       in json_data
            assert 'local_storage_path'    in json_data