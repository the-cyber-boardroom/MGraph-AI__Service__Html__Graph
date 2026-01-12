# ═══════════════════════════════════════════════════════════════════════════════
# test_Html_Cache__Layer__Url - Tests for L0 URL caching layer
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                   import TestCase
from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type  import Enum__Cache__Data_Type
from osbot_utils.testing.Temp_Folder                                            import Temp_Folder
from osbot_utils.testing.Temp_Web_Server                                        import Temp_Web_Server
from osbot_utils.testing.__ import __, __SKIP__, __LESS_THAN__
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.utils.Objects                                                  import base_types
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url        import Safe_Str__Url
from phase_e.url_fetch.Html_Fetcher                                             import Html_Fetcher
from phase_e.url_fetch.Html_Cache__Layer__Url                                   import Html_Cache__Layer__Url
from phase_e.url_fetch.schemas.Schema__Html_Cache__L0__Url_Metadata             import Schema__Html_Cache__L0__Url_Metadata
from phase_e.url_fetch.schemas.Schema__Html_Fetcher__Config                     import Schema__Html_Fetcher__Config
from phase_e.url_fetch.schemas.Schema__Url_Fetch__Stats                         import Schema__Url_Fetch__Stats
from phase_e.storage.backends.Perf__Storage__Cache_Service                      import Perf__Storage__Cache_Service
from phase_e.storage.cache_service.Cache_Service__Client                        import Cache_Service__Client
from phase_e.storage.schemas.Schema__Perf__Storage__Config                      import Schema__Perf__Storage__Config
from tests.Phase_E__Fast_API__Test_Objs                                         import client_cache_service


# Test HTML content
HTML_SIMPLE = '''<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body><h1>Hello World</h1></body>
</html>'''

HTML_DIFFERENT = '''<!DOCTYPE html>
<html>
<head><title>Different Page</title></head>
<body><h1>Different Content</h1></body>
</html>'''


class test_Html_Cache__Layer__Url(TestCase):

    @classmethod
    def setUpClass(cls):                                               # Setup cache service and web server
        # In-memory cache service
        cls.cache_client, cls.cache_service = client_cache_service()
        cls.cache_client_wrapper = Cache_Service__Client(cache_client=cls.cache_client)
        cls.config = Schema__Perf__Storage__Config(cache_namespace='test-l0-layer')
        
        # Create storage backend
        cls.storage = Perf__Storage__Cache_Service(config       = cls.config              ,
                                                   client       = cls.cache_client_wrapper,
                                                   session_name = 'test-session'          ,
                                                   target_name  = 'test-target'           )
        
        # Setup temp web server
        cls.temp_folder = Temp_Folder()
        cls.temp_folder.__enter__()
        cls.temp_folder.add_file('index.html'    , HTML_SIMPLE)
        cls.temp_folder.add_file('different.html', HTML_DIFFERENT)
        
        cls.server = Temp_Web_Server(root_folder=cls.temp_folder.path())
        cls.server.__enter__()
        
        # Create fetcher and stats
        cls.fetcher = Html_Fetcher(config=Schema__Html_Fetcher__Config())
        cls.stats   = Schema__Url_Fetch__Stats()
        
        # Create L0 layer
        cls.layer = Html_Cache__Layer__Url(storage = cls.storage,
                                           stats   = cls.stats  ,
                                           fetcher = cls.fetcher)
        
        # Create entry and get cache_id
        cls.cache_id = cls.storage.create_file__perf_entry()

    @classmethod
    def tearDownClass(cls):                                            # Cleanup
        cls.server.__exit__(None, None, None)
        cls.temp_folder.__exit__(None, None, None)

    def setUp(self):                                                   # Reset stats before each test
        self.stats.l0_hits             = 0
        self.stats.l0_misses           = 0
        self.stats.l0_conditional_hits = 0
        self.stats.network_requests    = 0
        self.stats.network_failures    = 0

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                            # Test initialization
        with self.layer as _:
            assert type(_)       is Html_Cache__Layer__Url
            assert base_types(_) == [Type_Safe, object]
            assert _.layer_name  == 'L0'
            assert _.storage     is not None
            assert _.fetcher     is not None
            assert _.stats       is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # Key Generation Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_key_metadata(self):                                       # Test metadata key
        key = self.layer.key_metadata()
        assert key == 'L0/url-metadata.json'

    def test_key_html(self):                                           # Test HTML key
        key = self.layer.key_html()
        assert key == 'L0/html-ref.json'

    # ═══════════════════════════════════════════════════════════════════════════
    # Fetch and Cache Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_html__first_fetch(self):                              # Test first fetch (cache miss)
        with self.layer as _:
            _.delete_html    (cache_id = self.cache_id)
            _.delete_metadata(cache_id = self.cache_id)
            self.stats.l0_misses        = 0
            self.stats.network_requests = 0

            url  = f'http://127.0.0.1:{self.server.port}/index.html'

            html = _.get_html(cache_id=self.cache_id, url=url)

            assert html is not None
            assert '<h1>Hello World</h1>' in html
            assert self.stats.l0_misses        == 1                        # Cache miss
            assert self.stats.network_requests == 1
            assert html                        == HTML_SIMPLE

            metadata__loaded = _.load_metadata(cache_id=self.cache_id)
            html__loaded     = _._load_html   (cache_id=self.cache_id)


            assert _.exists(cache_id=self.cache_id) is True
            assert _.key_html()                     == 'L0/html-ref.json'
            assert _.key_metadata()                 == 'L0/url-metadata.json'
            assert type(metadata__loaded)           == Schema__Html_Cache__L0__Url_Metadata
            assert html__loaded                     == HTML_SIMPLE
            assert metadata__loaded.obj()           == __(url            = url               ,
                                                          normalized_url = url               ,
                                                          final_url      = url               ,
                                                          status_code    = 200               ,
                                                          content_type   = ''                ,
                                                          content_length = 102               ,
                                                          etag           =''                 ,
                                                          last_modified  = __SKIP__          ,
                                                          cache_control  = ''                ,
                                                          fetched_at     = __SKIP__          ,
                                                          fetch_duration = __LESS_THAN__(20) ,
                                                          content_hash   = '200fd358b9e7bdac')


        with self.layer.storage as _:                                   # check data in storage
            data_folder = _.data_folder()
            file__html_ref          = 'L0/html-ref_json'
            file__url_metadata      = 'L0/url-metadata_json'
            data_file__html_ref     = _.data_file(data_type=Enum__Cache__Data_Type.JSON, key_data=file__html_ref    )
            data_file__url_metadata = _.data_file(data_type=Enum__Cache__Data_Type.JSON, key_data=file__url_metadata)
            assert data_folder               == 'test-l0-layer/data/key-based/sessions/test-session/targets/test-target/perf-entry/data'
            assert data_file__html_ref       == 'test-l0-layer/data/key-based/sessions/test-session/targets/test-target/perf-entry/data/L0/html-ref_json.json'
            assert data_file__html_ref       == f'{data_folder}/{file__html_ref}.json'
            assert data_file__url_metadata   == f'{data_folder}/{file__url_metadata}.json'

            assert data_file__html_ref     in _.namespace__all_files()
            assert data_file__url_metadata in _.namespace__all_files()





    def test_get_html__cached_fetch(self):                             # Test cached fetch (cache hit)
        url = Safe_Str__Url(self.server.url('index.html'))
        
        # First fetch
        self.layer.get_html(cache_id=self.cache_id, url=url)
        
        # Reset stats
        self.stats.l0_hits   = 0
        self.stats.l0_misses = 0
        
        # Second fetch - should hit cache
        html = self.layer.get_html(cache_id=self.cache_id, url=url)
        
        assert html is not None
        assert '<h1>Hello World</h1>' in html
        assert self.stats.l0_hits     == 1                                  # Cache hit
        assert self.stats.l0_misses   == 0                                  # No miss

    def test_get_html__force_refresh(self):                            # Test force refresh
        url = self.server.url('index.html')
        
        # First fetch
        self.layer.get_html(cache_id=self.cache_id, url=url)
        
        # Reset stats
        self.stats.l0_hits           = 0
        self.stats.l0_misses         = 0
        self.stats.network_requests  = 0
        
        # Force refresh - should fetch from network
        html = self.layer.get_html(cache_id      = self.cache_id,
                                   url           = url           ,
                                   force_refresh = True          )
        
        assert html is not None
        assert self.stats.l0_misses == 1

        assert self.stats.obj() == __(l0_hits             = 0,
                                      l0_misses           = 1,
                                      l0_conditional_hits = 0,
                                      network_requests    = 1,
                                      network_failures    = 0,
                                      network_retries     = 0,
                                      total_fetch_time_ms = 0,
                                      total_bytes_fetched = 0)

        assert self.layer._load_html     (cache_id=self.cache_id) == HTML_SIMPLE
        assert self.layer.delete_html    (cache_id=self.cache_id) is True
        assert self.layer.delete_html    (cache_id=self.cache_id) is False
        assert self.layer.delete_metadata(cache_id=self.cache_id) is True
        assert self.layer.delete_metadata(cache_id=self.cache_id) is False
        assert self.layer._load_html     (cache_id=self.cache_id) == ''

    # ═══════════════════════════════════════════════════════════════════════════
    # Metadata Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_load_metadata__after_fetch(self):                         # Test metadata saved
        url = Safe_Str__Url(self.server.url('index.html'))
        
        # Fetch to populate cache
        self.layer.get_html(cache_id=self.cache_id, url=url)
        
        # Load metadata
        metadata = self.layer.load_metadata(cache_id=self.cache_id)
        assert type(metadata) is Schema__Html_Cache__L0__Url_Metadata
        assert url            == f'http://127.0.0.1:{self.server.port}/index.html'
        assert metadata.obj() == __(url=url,
                                    normalized_url=url,
                                    final_url=url,
                                    status_code=200,
                                    content_type='',
                                    content_length=102,
                                    etag='',
                                    last_modified=__SKIP__,
                                    cache_control='',
                                    fetched_at=__SKIP__,
                                    fetch_duration=__SKIP__,
                                    content_hash='200fd358b9e7bdac')


    def test_exists__before_fetch(self):                               # Test exists before fetch
        # Create new storage for clean test
        new_storage = Perf__Storage__Cache_Service(config       = self.config,
                                                   client       = self.cache_client_wrapper,
                                                   session_name = 'test-session'    ,
                                                   target_name  = 'new-target'      )
        new_cache_id = new_storage.create_file__perf_entry()
        
        layer = Html_Cache__Layer__Url(storage = new_storage               ,
                                       stats   = Schema__Url_Fetch__Stats(),
                                       fetcher = self.fetcher              )
        
        # Should not exist yet
        exists = layer.exists(cache_id=new_cache_id)
        assert exists is False

    def test_exists__after_fetch(self):                                # Test exists after fetch
        url = Safe_Str__Url(self.server.url('index.html'))
        
        # Fetch to populate cache
        self.layer.get_html(cache_id=self.cache_id, url=url)
        
        # Should exist now
        exists = self.layer.exists(cache_id=self.cache_id)
        assert exists is True

    # ═══════════════════════════════════════════════════════════════════════════
    # URL Normalization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__normalize_url__basic(self):                              # Test basic URL normalization
        normalized = self.layer._normalize_url('https://Example.COM/Path/')
        assert normalized == 'https://example.com/path'

    def test__normalize_url__removes_trailing_slash(self):             # Test trailing slash removed
        normalized = self.layer._normalize_url('https://example.com/')
        assert normalized == 'https://example.com/'                    # Root keeps slash

    def test__normalize_url__preserves_path(self):                     # Test path preserved
        normalized = self.layer._normalize_url('https://example.com/a/b/c')
        assert normalized == 'https://example.com/a/b/c'

    # ═══════════════════════════════════════════════════════════════════════════
    # Content Hash Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__content_hash__consistent(self):                          # Test hash is consistent
        content = 'Test content'
        hash1   = self.layer._content_hash(content)
        hash2   = self.layer._content_hash(content)
        
        assert hash1 == hash2
        assert len(hash1) == 16                                        # 16 hex chars

    def test__content_hash__different_for_different_content(self):     # Test different content different hash
        hash1 = self.layer._content_hash('Content A')
        hash2 = self.layer._content_hash('Content B')
        
        assert hash1 != hash2

    # ═══════════════════════════════════════════════════════════════════════════
    # Error Handling Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_html__not_found(self):                                # Test 404 handling
        url  = Safe_Str__Url(self.server.url('nonexistent.html'))
        html = self.layer.get_html(cache_id=self.cache_id, url=url)
        
        assert html == ''                                              # Empty on error
        assert self.stats.network_failures == 1
