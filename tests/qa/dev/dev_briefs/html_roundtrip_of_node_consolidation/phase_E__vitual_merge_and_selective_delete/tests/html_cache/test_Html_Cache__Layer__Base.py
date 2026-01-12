# ═══════════════════════════════════════════════════════════════════════════════
# Test: Html_Cache__Layer__Base
# Tests the base class functionality for all cache layers
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                           import TestCase
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                      import Cache_Id
from osbot_utils.utils.Objects                                                          import base_classes
from phase_e.html_cache.Html_Cache__Layer__Base                                         import Html_Cache__Layer__Base
from phase_e.html_cache.schemas.Schema__Html_Cache                                      import Schema__Html_Cache__Config, Schema__Html_Cache__Stats
from phase_e.storage.backends.Perf__Storage__Cache_Service                              import Perf__Storage__Cache_Service
from phase_e.storage.base.Perf__Storage__Base                                           import Perf__Storage__Base
from phase_e.storage.cache_service.Cache_Service__Client                                import Cache_Service__Client
from phase_e.storage.enums.Enum__Storage_Mode                                           import Enum__Storage_Mode
from phase_e.storage.schemas.Schema__Perf__Storage__Config                              import Schema__Perf__Storage__Config
from tests.Phase_E__Fast_API__Test_Objs                                                 import client_cache_service


class test_Html_Cache__Layer__Base(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.session_name    = 'test-html-cache'
        cls.target_name     = 'layer-base'
        cls.cache_namespace = 'pytest'
        cls.config          = Schema__Perf__Storage__Config(storage_mode    = Enum__Storage_Mode.CACHE_SERVICE,
                                                            cache_namespace = cls.cache_namespace)

        cls.cache_client, cls.cache_service = client_cache_service()
        cls.cache_client_wrapper            = Cache_Service__Client(cache_client=cls.cache_client)

        cls.storage       = Perf__Storage__Cache_Service(config       = cls.config              ,
                                                         client       = cls.cache_client_wrapper,
                                                         session_name = cls.session_name        ,
                                                         target_name  = cls.target_name         )
        cls.stats         = Schema__Html_Cache__Stats()
        cls.layer         = Html_Cache__Layer__Base(storage    = cls.storage   ,
                                                    stats      = cls.stats     ,
                                                    layer_name = 'TEST'        )
        cls.cache_id      = cls.storage.create_file__perf_entry()

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                     # Test base class initialization
        with Html_Cache__Layer__Base() as _:
            assert type(_)            is Html_Cache__Layer__Base
            assert base_classes(_)    == [Type_Safe, object]
            assert type(_.storage)    is Perf__Storage__Base
            assert _.layer_name       == ''                     # Empty by default

    def test__init____with_storage(self):                       # Test initialization with storage
        with self.layer as _:
            assert type(_)         is Html_Cache__Layer__Base
            assert type(_.storage) is Perf__Storage__Cache_Service
            assert _.layer_name    == 'TEST'

    # ═══════════════════════════════════════════════════════════════════════════
    # Key Generation Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_key_data(self):                                    # Test data key generation
        assert self.layer.key_data() == 'TEST/data'

    def test_key_metadata(self):                                # Test metadata key generation
        assert self.layer.key_metadata() == 'TEST/metadata'

    def test_key_data__different_layer_names(self):             # Verify different layers have different keys
        layer_l1 = Html_Cache__Layer__Base(layer_name='L1')
        layer_l2 = Html_Cache__Layer__Base(layer_name='L2')
        layer_l3 = Html_Cache__Layer__Base(layer_name='L3')

        assert layer_l1.key_data() == 'L1/data'
        assert layer_l2.key_data() == 'L2/data'
        assert layer_l3.key_data() == 'L3/data'

    # ═══════════════════════════════════════════════════════════════════════════
    # Content Hash Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_content_hash(self):                                # Test hash generation
        hash_1 = self.layer.content_hash('test content')

        assert type(hash_1)  is str
        assert len(hash_1 )  == 16                              # Truncated to 16 chars
        assert hash_1        == '6ae8a75555209fd6'              # deterministic value

    def test_content_hash__consistency(self):                   # Same content produces same hash
        content = 'Hello World'
        hash_1  = self.layer.content_hash(content)
        hash_2  = self.layer.content_hash(content)

        assert hash_1 == hash_2
        assert hash_1 == 'a591a6d40bf42040'

    def test_content_hash__different_content(self):             # Different content produces different hash
        hash_1 = self.layer.content_hash('content A')
        hash_2 = self.layer.content_hash('content B')

        assert hash_1 != hash_2

    def test_content_hash__empty_string(self):                  # Empty string has valid hash
        hash_empty = self.layer.content_hash('')

        assert type(hash_empty) is str
        assert len(hash_empty)  == 16
        assert hash_empty       == 'e3b0c44298fc1c14'

    def test_content_hash__unicode(self):                       # Unicode content hashes correctly
        hash_unicode = self.layer.content_hash('こんにちは世界')

        assert type(hash_unicode) is str
        assert len(hash_unicode)  == 16
        assert hash_unicode       == 'c6a304536826fb57'

    # ═══════════════════════════════════════════════════════════════════════════
    # Timestamp Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_timestamp(self):                                   # Test timestamp generation
        ts = self.layer.timestamp()

        assert type(ts) is float
        assert ts > 0

    # ═══════════════════════════════════════════════════════════════════════════
    # Metadata Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_save_metadata(self):                               # Test metadata save
        metadata = {'key': 'value', 'count': 42}
        result   = self.layer.save_metadata(cache_id = self.cache_id,
                                            metadata = metadata)

        assert result is True

    def test_load_metadata(self):                               # Test metadata round-trip
        metadata = {'key': 'value', 'count': 42}
        self.layer.save_metadata(cache_id = self.cache_id,
                                 metadata = metadata)

        loaded = self.layer.load_metadata(cache_id=self.cache_id)

        assert loaded == metadata

    def test_load_metadata__not_found(self):                    # Returns None when not found
        fake_cache_id = Cache_Id()  # Random ID that doesn't exist
        loaded = self.layer.load_metadata(cache_id=fake_cache_id)

        assert loaded is None

    def test_save_metadata__overwrite(self):                    # Overwriting metadata works
        self.layer.save_metadata(cache_id = self.cache_id,
                                 metadata = {'version': 1})
        self.layer.save_metadata(cache_id = self.cache_id,
                                 metadata = {'version': 2})

        loaded = self.layer.load_metadata(cache_id=self.cache_id)

        assert loaded == {'version': 2}