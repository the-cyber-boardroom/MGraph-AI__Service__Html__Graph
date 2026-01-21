# ═══════════════════════════════════════════════════════════════════════════════
# test_Html_Cache__Session - Tests for URL fetching session
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                          import TestCase
from osbot_utils.testing.Temp_Folder                                   import Temp_Folder
from osbot_utils.testing.Temp_Web_Server                               import Temp_Web_Server
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url import Safe_Str__Url
from phase_e.url_fetch.Html_Cache__Session                             import Html_Cache__Session
from phase_e.url_fetch.Html_Cache__Session_Factory                     import Html_Cache__Session_Factory
from phase_e.url_fetch.Html_Cache__Storage_Factory                     import Html_Cache__Storage_Factory
from phase_e.storage.cache_service.Cache_Service__Client               import Cache_Service__Client
from phase_e.storage.schemas.Schema__Perf__Storage__Config             import Schema__Perf__Storage__Config
from phase_e.storage.safe_str.Safe_Str__Session_Name                   import Safe_Str__Session_Name
from tests.Phase_E__Fast_API__Test_Objs                                import client_cache_service


class test_Html_Cache__Session(TestCase):

    @classmethod
    def setUpClass(cls):                                               # Setup cache service and web server
        # In-memory cache service
        cls.cache_client, cls.cache_service = client_cache_service()
        cls.cache_client_wrapper = Cache_Service__Client(cache_client=cls.cache_client)
        cls.config = Schema__Perf__Storage__Config(cache_namespace='test-session')
        
        # Setup temp web server
        cls.temp_folder = Temp_Folder()
        cls.temp_folder.__enter__()
        cls.temp_folder.add_file('page1.html', HTML_PAGE_1)
        cls.temp_folder.add_file('page2.html', HTML_PAGE_2)
        cls.temp_folder.add_file('page3.html', HTML_PAGE_3)
        
        cls.server = Temp_Web_Server(root_folder=cls.temp_folder.path())
        cls.server.__enter__()
        
        # Create session factory
        cls.factory = Html_Cache__Session_Factory(
            cache_client   = cls.cache_client_wrapper,
            storage_config = cls.config
        )

    @classmethod
    def tearDownClass(cls):                                            # Cleanup
        cls.server.__exit__(None, None, None)
        cls.temp_folder.__exit__(None, None, None)

    # ═══════════════════════════════════════════════════════════════════════════
    # Session Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                            # Test session initialization
        session = self.factory.create_session_with_name('init-test')
        
        with session as _:
            assert type(_)          is Html_Cache__Session
            assert _.session_name   == 'init-test'
            assert _.url_stats      is not None
            assert _._fetcher       is not None

    def test_context_manager(self):                                    # Test context manager
        with self.factory.create_session_with_name('ctx-test') as session:
            assert session is not None
            assert session._targets is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # URL to Target Conversion Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__url_to_target__simple(self):                             # Test URL to target conversion
        session = self.factory.create_session_with_name('target-test')
        url     = Safe_Str__Url('https://example.com/page')
        target  = session._url_to_target(url)
        
        assert str(target) == 'example-com-page'

    def test__url_to_target__with_path(self):                          # Test URL with path
        session = self.factory.create_session_with_name('target-test')
        url     = Safe_Str__Url('https://example.com/a/b/c')
        target  = session._url_to_target(url)
        
        assert str(target) == 'example-com-a-b-c'

    def test__url_to_target__lowercase(self):                          # Test lowercase conversion
        session = self.factory.create_session_with_name('target-test')
        url     = Safe_Str__Url('https://EXAMPLE.COM/PAGE')
        target  = session._url_to_target(url)
        
        assert str(target) == 'example-com-page'

    # ═══════════════════════════════════════════════════════════════════════════
    # HTML Fetch Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_html_from_url__basic(self):                           # Test basic HTML fetch
        with self.factory.create_session_with_name('html-test') as session:
            url  = Safe_Str__Url(self.server.url('page1.html'))
            html = session.get_html_from_url(url)
            
            assert html is not None
            assert '<h1>Welcome to Page 1</h1>' in html

    def test_get_html_from_url__different_pages(self):                 # Test different pages
        with self.factory.create_session_with_name('multi-page-test') as session:
            url1 = Safe_Str__Url(self.server.url('page1.html'))
            url2 = Safe_Str__Url(self.server.url('page2.html'))
            
            html1 = session.get_html_from_url(url1)
            html2 = session.get_html_from_url(url2)
            
            assert 'Page 1' in html1
            assert 'Page 2' in html2

    def test_get_html_from_url__cached_second_time(self):              # Test cached access
        with self.factory.create_session_with_name('cached-html-test') as session:
            url = Safe_Str__Url(self.server.url('page2.html'))
            
            # First fetch - network
            session.get_html_from_url(url)
            first_misses = session.url_stats.l0_misses
            
            # Reset stats
            session.url_stats.l0_hits   = 0
            session.url_stats.l0_misses = 0
            
            # Second fetch - should use cache
            html = session.get_html_from_url(url)
            
            assert html is not None
            assert session.url_stats.l0_hits >= 1                      # Cache hit

    # ═══════════════════════════════════════════════════════════════════════════
    # Batch Fetch Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_batch_fetch_urls__multiple(self):                         # Test batch fetching
        with self.factory.create_session_with_name('batch-test') as session:
            urls = [
                self.server.url('page1.html'),
                self.server.url('page2.html'),
                self.server.url('page3.html')
            ]
            
            results = session.batch_fetch_urls(urls)
            
            assert results['fetched'] + results['cached'] == 3
            assert results['failed'] == 0
            assert len(results['html']) == 3

    def test_batch_fetch_urls__with_invalid(self):                     # Test batch with invalid URL
        with self.factory.create_session_with_name('batch-invalid-test') as session:
            urls = [
                self.server.url('page1.html'),
                self.server.url('nonexistent.html'),                   # 404
            ]
            
            results = session.batch_fetch_urls(urls)
            
            assert results['fetched'] + results['cached'] == 1         # Only 1 succeeded
            assert results['failed'] == 1                              # 1 failed

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_stats(self):                                          # Test stats retrieval
        with self.factory.create_session_with_name('stats-test') as session:
            url = Safe_Str__Url(self.server.url('page1.html'))
            session.get_html_from_url(url)
            
            stats = session.get_stats()
            
            assert stats is not None

    def test_reset_stats(self):                                        # Test stats reset
        with self.factory.create_session_with_name('reset-stats-test') as session:
            url = Safe_Str__Url(self.server.url('page1.html'))
            session.get_html_from_url(url)
            
            # Should have some stats
            assert session.url_stats.l0_misses > 0 or session.url_stats.l0_hits > 0
            
            # Reset
            session.reset_stats()
            
            # Stats should be zero
            assert session.url_stats.l0_misses == 0
            assert session.url_stats.l0_hits == 0





# Test HTML content
HTML_PAGE_1 = '''<!DOCTYPE html>
<html>
<head><title>Page 1</title></head>
<body>
<h1>Welcome to Page 1</h1>
<p>This is the first test page.</p>
<a href="/page2.html">Go to Page 2</a>
</body>
</html>'''

HTML_PAGE_2 = '''<!DOCTYPE html>
<html>
<head><title>Page 2</title></head>
<body>
<h1>Welcome to Page 2</h1>
<p>This is the second test page.</p>
<ul>
<li>Item 1</li>
<li>Item 2</li>
</ul>
</body>
</html>'''

HTML_PAGE_3 = '''<!DOCTYPE html>
<html>
<head><title>Page 3</title></head>
<body>
<div id="content">
<h1>Page 3 Content</h1>
<span class="highlight">Important text</span>
</div>
</body>
</html>'''
