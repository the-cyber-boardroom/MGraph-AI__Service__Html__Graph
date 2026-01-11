# ═══════════════════════════════════════════════════════════════════════════════
# test_Perf__Storage__Factory - Tests for storage factory
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                               import TestCase
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from phase_e.storage.factory.Perf__Storage__Factory                                         import Perf__Storage__Factory
from phase_e.storage.base.Perf__Storage__Base                                               import Perf__Storage__Base
from phase_e.storage.backends.Perf__Storage__Local                                          import Perf__Storage__Local
from phase_e.storage.backends.Perf__Storage__Memory                                         import Perf__Storage__Memory
from phase_e.storage.backends.Perf__Storage__Cache_Service                                  import Perf__Storage__Cache_Service
from phase_e.storage.schemas.Schema__Perf__Storage__Config                                  import Schema__Perf__Storage__Config
from phase_e.storage.enums.Enum__Storage_Mode                                               import Enum__Storage_Mode
from tests.Phase_E__Fast_API__Test_Objs                                                     import client_cache_service


class test_Perf__Storage__Factory(TestCase):

    @classmethod
    def setUpClass(cls):                                                                    # Shared setup - in-memory cache
        cls.cache_client, cls.cache_service = client_cache_service()

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                 # Test auto-initialization
        config = Schema__Perf__Storage__Config()

        with Perf__Storage__Factory(config=config) as _:
            assert type(_)        is Perf__Storage__Factory
            assert type(_.config) is Schema__Perf__Storage__Config
            assert issubclass(type(_), Type_Safe)

    # ═══════════════════════════════════════════════════════════════════════════
    # Create Local Backend Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_create__local(self):                                                           # Test create LOCAL backend
        config = Schema__Perf__Storage__Config(storage_mode       = Enum__Storage_Mode.LOCAL,
                                               local_storage_path = '/tmp/test_storage'     )

        with Perf__Storage__Factory(config=config) as _:
            storage = _.create()

            assert type(storage)        is Perf__Storage__Local
            assert storage.storage_path == '/tmp/test_storage'
            assert issubclass(type(storage), Perf__Storage__Base)

    def test_create__local_default_path(self):                                              # Test create LOCAL with default
        config = Schema__Perf__Storage__Config(storage_mode=Enum__Storage_Mode.LOCAL)

        with Perf__Storage__Factory(config=config) as _:
            storage = _.create()

            assert type(storage)        is Perf__Storage__Local
            assert storage.storage_path == './perf_results'

    # ═══════════════════════════════════════════════════════════════════════════
    # Create Memory Backend Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_create__memory(self):                                                          # Test create MEMORY backend
        config = Schema__Perf__Storage__Config(storage_mode=Enum__Storage_Mode.MEMORY)

        with Perf__Storage__Factory(config=config) as _:
            storage = _.create()

            assert type(storage) is Perf__Storage__Memory
            assert storage.data  == {}
            assert issubclass(type(storage), Perf__Storage__Base)

    def test_create__memory_fresh_instance(self):                                           # Test memory creates fresh dict
        config = Schema__Perf__Storage__Config(storage_mode=Enum__Storage_Mode.MEMORY)

        with Perf__Storage__Factory(config=config) as _:
            storage1 = _.create()
            storage2 = _.create()

            storage1.data['test'] = 'value'

            assert 'test' not in storage2.data                                              # Each instance has own dict

    # ═══════════════════════════════════════════════════════════════════════════
    # Create Cache Service Backend Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_create__cache_service(self):                                                   # Test create CACHE_SERVICE backend
        config = Schema__Perf__Storage__Config(storage_mode    = Enum__Storage_Mode.CACHE_SERVICE,
                                               cache_namespace = 'test-ns'                       )

        with Perf__Storage__Factory(config       = config                ,
                                    cache_client = self.cache_client     ,
                                    session_name = 'factory_test_session',
                                    target_name  = 'factory_test_target' ) as _:
            storage = _.create()

            assert type(storage)      is Perf__Storage__Cache_Service
            assert storage.client     is not None
            assert storage.session_name == 'factory_test_session'
            assert storage.target_name  == 'factory_test_target'
            assert issubclass(type(storage), Perf__Storage__Base)

    # ═══════════════════════════════════════════════════════════════════════════
    # Factory Pattern Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_create__returns_base_type__local(self):                                        # Test LOCAL returns base type
        config = Schema__Perf__Storage__Config(storage_mode=Enum__Storage_Mode.LOCAL)

        with Perf__Storage__Factory(config=config) as _:
            storage = _.create()
            assert issubclass(type(storage), Perf__Storage__Base)

    def test_create__returns_base_type__memory(self):                                       # Test MEMORY returns base type
        config = Schema__Perf__Storage__Config(storage_mode=Enum__Storage_Mode.MEMORY)

        with Perf__Storage__Factory(config=config) as _:
            storage = _.create()
            assert issubclass(type(storage), Perf__Storage__Base)

    def test_create__returns_base_type__cache_service(self):                                # Test CACHE_SERVICE returns base
        config = Schema__Perf__Storage__Config(storage_mode=Enum__Storage_Mode.CACHE_SERVICE)

        with Perf__Storage__Factory(config       = config           ,
                                    cache_client = self.cache_client,
                                    session_name = 'base_type_test' ,
                                    target_name  = 'target'         ) as _:
            storage = _.create()
            assert issubclass(type(storage), Perf__Storage__Base)

    def test_create__all_have_save_load(self):                                              # Test all have save/load methods
        configs = [
            (Enum__Storage_Mode.LOCAL , {'storage_mode': Enum__Storage_Mode.LOCAL }),
            (Enum__Storage_Mode.MEMORY, {'storage_mode': Enum__Storage_Mode.MEMORY}),
        ]

        for mode, config_kwargs in configs:
            config = Schema__Perf__Storage__Config(**config_kwargs)

            with Perf__Storage__Factory(config=config) as factory:
                storage = factory.create()

                assert hasattr(storage, 'save')
                assert hasattr(storage, 'save_string')
                assert hasattr(storage, 'load')
                assert hasattr(storage, 'load_string')
                assert hasattr(storage, 'exists')
                assert hasattr(storage, 'delete')
                assert hasattr(storage, 'list_keys')

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_integration__memory_roundtrip(self):                                           # Test full roundtrip with memory
        config = Schema__Perf__Storage__Config(storage_mode=Enum__Storage_Mode.MEMORY)

        with Perf__Storage__Factory(config=config) as _:
            storage = _.create()
            storage.set_context('test_session', 'test_target')

            # Save and load JSON
            storage.save('data.json', {'key': 'value'})
            loaded = storage.load('data.json')
            assert loaded == {'key': 'value'}

            # Save and load string
            storage.save_string('output.txt', 'Hello World')
            content = storage.load_string('output.txt')
            assert content == 'Hello World'

            # Check exists
            assert storage.exists('data.json')    is True
            assert storage.exists('missing.json') is False

            # Delete
            assert storage.delete('data.json') is True
            assert storage.exists('data.json') is False

    def test_integration__cache_service_roundtrip(self):                                    # Test roundtrip with cache service
        config = Schema__Perf__Storage__Config(storage_mode    = Enum__Storage_Mode.CACHE_SERVICE,
                                               cache_namespace = 'integration_test'              )

        with Perf__Storage__Factory(config       = config                    ,
                                    cache_client = self.cache_client         ,
                                    session_name = 'integration_test_session',
                                    target_name  = 'integration_test_target' ) as _:
            storage = _.create()

            # Save and load JSON
            storage.save('data.json', {'integration': 'test'})
            loaded = storage.load('data.json')
            assert loaded == {'integration': 'test'}

            # Save and load string
            storage.save_string('output.txt', 'Integration test content')
            content = storage.load_string('output.txt')
            assert content == 'Integration test content'

            # Check exists
            assert storage.exists('data.json')    is True
            assert storage.exists('missing.json') is False