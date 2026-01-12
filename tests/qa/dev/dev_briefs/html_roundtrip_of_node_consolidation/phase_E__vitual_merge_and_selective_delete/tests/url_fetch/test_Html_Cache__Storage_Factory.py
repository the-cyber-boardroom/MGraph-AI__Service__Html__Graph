from unittest                                                           import TestCase
from osbot_utils.testing.__                                             import __, __SKIP__
from osbot_utils.utils.Misc                                             import list_set
from phase_e.storage.backends.Perf__Storage__Cache_Service              import Perf__Storage__Cache_Service
from phase_e.storage.cache_service.Cache_Service__Client                import Cache_Service__Client
from phase_e.storage.schemas.Schema__Perf__Storage__Config              import Schema__Perf__Storage__Config
from phase_e.storage.safe_str.Safe_Str__Session_Name                    import Safe_Str__Session_Name
from phase_e.url_fetch.Html_Cache__Storage_Factory                      import Html_Cache__Storage_Factory
from tests.Phase_E__Fast_API__Test_Objs                                 import client_cache_service


class test_Html_Cache__Storage_Factory(TestCase):

    @classmethod
    def setUpClass(cls):                                               # Setup cache service
        cls.cache_client, cls.cache_service = client_cache_service()
        cls.cache_client_wrapper = Cache_Service__Client(cache_client=cls.cache_client)
        cls.config = Schema__Perf__Storage__Config(cache_namespace='test-storage-factory')

    def test__init__(self):                                            # Test factory initialization
        factory = Html_Cache__Storage_Factory(config       = self.config,
                                              cache_client = self.cache_client_wrapper,
                                              session_name = Safe_Str__Session_Name('test-session'))

        assert factory is not None
        assert factory.session_name == 'test-session'

    def test_create_for_layer(self):                                   # Test layer storage creation
        from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id
        from phase_e.storage.safe_str.Safe_Str__Target_Name import Safe_Str__Target_Name

        factory = Html_Cache__Storage_Factory(
            config       = self.config,
            cache_client = self.cache_client_wrapper,
            session_name = Safe_Str__Session_Name('test-session')
        )

        storage = factory.create_for_layer(
            layer_name  = Safe_Str__Id('L0'),
            target_name = Safe_Str__Target_Name('test-target')
        )

        assert storage is not None

    def test_create_all_layers(self):                                  # Test all layers creation
        from phase_e.storage.safe_str.Safe_Str__Target_Name import Safe_Str__Target_Name

        factory = Html_Cache__Storage_Factory(config       = self.config                         ,
                                              cache_client = self.cache_client_wrapper           ,
                                              session_name = Safe_Str__Session_Name('test-session'))

        layers = factory.create_all_layers(Safe_Str__Target_Name('test-target'))

        assert list_set(layers) == ['L0', 'L1', 'L2', 'L3']

        assert type(layers['L0']) == Perf__Storage__Cache_Service
        assert layers['L0'].obj() == __(session_name='test-session',
                                        target_name='test-target',
                                        file_id='perf-entry',
                                        config=__(storage_mode='local',
                                                  cache_namespace='test-storage-factory',
                                                  local_storage_path='./perf_results'),
                                        client=__(config=__(storage_mode='local',
                                                            cache_namespace='test-storage-factory',
                                                            local_storage_path='./perf_results'),
                                                  cache_client=__(config=__(base_url=None,
                                                                            api_key=None,
                                                                            api_key_header=None,
                                                                            mode='in_memory',
                                                                            fast_api_app='FastAPI',
                                                                            timeout=30,
                                                                            service_name='Cache__Service__Fast_API',
                                                                            service_version=__SKIP__)),
                                                  hash_generator=__(config=__(algorithm='sha256', length=16))))