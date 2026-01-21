from unittest                                                          import TestCase
from osbot_utils.type_safe.Type_Safe                                   import Type_Safe
from osbot_utils.utils.Objects                                         import base_types
from phase_e.url_fetch.Html_Cache__Session                             import Html_Cache__Session
from phase_e.url_fetch.Html_Cache__Session_Factory                     import Html_Cache__Session_Factory
from phase_e.storage.cache_service.Cache_Service__Client               import Cache_Service__Client
from phase_e.storage.schemas.Schema__Perf__Storage__Config             import Schema__Perf__Storage__Config
from phase_e.storage.safe_str.Safe_Str__Session_Name                   import Safe_Str__Session_Name
from tests.Phase_E__Fast_API__Test_Objs                                import client_cache_service


class test_Html_Cache__Session_Factory(TestCase):

    @classmethod
    def setUpClass(cls):                                               # Setup cache service
        cls.cache_client, cls.cache_service = client_cache_service()
        cls.cache_client_wrapper = Cache_Service__Client(cache_client=cls.cache_client)
        cls.config = Schema__Perf__Storage__Config(cache_namespace='test-session-factory')

        cls.factory = Html_Cache__Session_Factory(
            cache_client   = cls.cache_client_wrapper,
            storage_config = cls.config
        )

    def test__init__(self):                                            # Test factory initialization
        with self.factory as _:
            assert type(_)       is Html_Cache__Session_Factory
            assert base_types(_) == [Type_Safe, object]
            assert _.cache_client is not None

    def test_create_session(self):                                     # Test session creation
        session = self.factory.create_session(Safe_Str__Session_Name('test-001'))

        assert type(session) is Html_Cache__Session
        assert session.session_name == 'test-001'
        assert session._fetcher is not None
        assert session._targets is not None

    def test_create_session_with_name(self):                           # Test convenience method
        session = self.factory.create_session_with_name('test-002')

        assert type(session) is Html_Cache__Session
        assert session.session_name == 'test-002'