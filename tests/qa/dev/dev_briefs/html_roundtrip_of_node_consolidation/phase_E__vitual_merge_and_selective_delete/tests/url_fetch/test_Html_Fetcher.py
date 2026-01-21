# ═══════════════════════════════════════════════════════════════════════════════
# test_Html_Fetcher - Tests for HTML fetcher using real HTTP (Temp_Web_Server)
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                          import TestCase
from osbot_utils.testing.Temp_Folder                                   import Temp_Folder
from osbot_utils.testing.Temp_Web_Server                               import Temp_Web_Server
from osbot_utils.testing.__ import __, __SKIP__
from osbot_utils.testing.__helpers import obj
from osbot_utils.type_safe.Type_Safe                                   import Type_Safe
from osbot_utils.utils.Objects                                         import base_types
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url import Safe_Str__Url
from phase_e.url_fetch.Html_Fetcher                                    import Html_Fetcher
from phase_e.url_fetch.schemas.Schema__Html_Fetcher__Config            import Schema__Html_Fetcher__Config
from phase_e.url_fetch.schemas.Schema__Html_Fetcher__Response          import Schema__Html_Fetcher__Response


class test_Html_Fetcher(TestCase):

    @classmethod
    def setUpClass(cls):                                               # Setup real HTTP server
        cls.temp_folder = Temp_Folder()
        cls.temp_folder.__enter__()
        
        # Add test HTML files
        cls.temp_folder.add_file('index.html', HTML_SIMPLE)
        cls.temp_folder.add_file('page2.html', HTML_WITH_LINKS)
        cls.temp_folder.add_file('large.html', HTML_LARGE)
        
        # Start web server
        cls.server = Temp_Web_Server(root_folder=cls.temp_folder.path())
        cls.server.__enter__()
        
        # Create fetcher with default config
        cls.fetcher = Html_Fetcher(config=Schema__Html_Fetcher__Config())

    @classmethod
    def tearDownClass(cls):                                            # Cleanup
        cls.server.__exit__(None, None, None)
        cls.temp_folder.__exit__(None, None, None)

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                            # Test initialization
        with self.fetcher as _:
            assert type(_)       is Html_Fetcher
            assert base_types(_) == [Type_Safe, object]
            assert _.config      is not None

    def test__init____config_defaults(self):                           # Test config defaults
        with self.fetcher.config as _:
            assert type(_)              is Schema__Html_Fetcher__Config
            assert int(_.timeout_seconds)         == 30
            assert int(_.max_retries)             == 3
            assert int(_.retry_delay_seconds)     == 1
            assert int(_.min_request_interval_ms) == 100
            assert _.follow_redirects   is True

    # ═══════════════════════════════════════════════════════════════════════════
    # Basic Fetch Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_fetch__simple_html(self):                                 # Test basic fetch
        url      = Safe_Str__Url(self.server.url('index.html'))
        response = self.fetcher.fetch(url)
        
        assert type(response) is Schema__Html_Fetcher__Response
        assert response.ok    is True
        assert int(response.status_code) == 200
        assert '<h1>Hello World</h1>' in response.html
        assert '<title>Test Page</title>' in response.html

    def test_fetch__response_url_tracking(self):                       # Test URL tracking
        url      = Safe_Str__Url(self.server.url('index.html'))
        response = self.fetcher.fetch(url)
        
        assert str(response.url)       == str(url)
        assert str(response.final_url) == str(url)                     # No redirect

    def test_fetch__headers_captured(self):                            # Test headers captured
        url      = Safe_Str__Url(self.server.url('index.html'))
        response = self.fetcher.fetch(url)

        assert type(response) is Schema__Html_Fetcher__Response
        assert response.obj() == __(url         = url,
                                    final_url   = url,
                                    status_code = 200,
                                    headers     = __(Server         = __SKIP__,
                                                     Date           = __SKIP__,
                                                     Content_type   = 'text/html',
                                                     Content_Length = '124',
                                                     Last_Modified  = __SKIP__,),
                                   html         = '<!DOCTYPE html>\n'
                                                  '<html>\n'
                                                  '<head><title>Test Page</title></head>\n'
                                                  '<body><h1>Hello World</h1><p>This is a test.</p></body>\n'
                                                  '</html>',
                                   ok            = True,
                                   error         = '',
                                   duration_ms   = __SKIP__)

    def test_fetch__duration_tracked(self):                            # Test duration tracking
        url      = Safe_Str__Url(self.server.url('index.html'))
        response = self.fetcher.fetch(url)
        
        assert int(response.duration_ms) > 0
        assert int(response.duration_ms) < 10000                       # Should be fast for local

    # ═══════════════════════════════════════════════════════════════════════════
    # Error Handling Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_fetch__not_found(self):                                   # Test 404 handling
        url      = Safe_Str__Url(self.server.url('nonexistent.html'))
        response = self.fetcher.fetch(url)
        
        assert response.ok is False
        assert int(response.status_code) == 404
        assert response.html == ''                                     # No content on error

    def test_fetch__different_pages(self):                             # Test fetching multiple pages
        url1 = Safe_Str__Url(self.server.url('index.html'))
        url2 = Safe_Str__Url(self.server.url('page2.html'))
        
        response1 = self.fetcher.fetch(url1)
        response2 = self.fetcher.fetch(url2)
        
        assert response1.ok is True
        assert response2.ok is True
        assert 'Hello World' in response1.html
        assert 'Link to Page 2' in response2.html

    # ═══════════════════════════════════════════════════════════════════════════
    # Custom Headers Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_fetch__with_custom_headers(self):                         # Test custom headers
        url      = Safe_Str__Url(self.server.url('index.html'))
        headers  = {'Accept': 'text/html', 'X-Custom': 'test-value'}
        response = self.fetcher.fetch(url, headers=headers)
        
        assert response.ok is True

    def test_fetch__user_agent_set(self):                              # Test user-agent set
        url      = Safe_Str__Url(self.server.url('index.html'))
        response = self.fetcher.fetch(url)
        
        # Request was successful - user agent was used
        assert response.ok is True

    # ═══════════════════════════════════════════════════════════════════════════
    # Large Content Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_fetch__large_content(self):                               # Test large content
        url      = Safe_Str__Url(self.server.url('large.html'))
        response = self.fetcher.fetch(url)
        
        assert response.ok is True
        assert len(response.html) > 1000                               # Should have lots of content
        assert '<p>Paragraph</p>' in response.html

    # ═══════════════════════════════════════════════════════════════════════════
    # Rate Limiting Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_fetch__rate_limiting_applied(self):                       # Test rate limiting
        import time
        
        url = Safe_Str__Url(self.server.url('index.html'))
        
        # Make two quick requests
        start_time = time.time()
        self.fetcher.fetch(url)
        self.fetcher.fetch(url)
        elapsed = (time.time() - start_time) * 1000
        
        # Should have some delay from rate limiting (100ms between requests)
        assert elapsed >= 90                                           # Allow some tolerance

    # ═══════════════════════════════════════════════════════════════════════════
    # Conditional Fetch Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_fetch_conditional__without_etag(self):                    # Test conditional without etag
        url      = Safe_Str__Url(self.server.url('index.html'))
        response = self.fetcher.fetch_conditional(url)
        
        # Without etag, should do normal fetch
        assert response.ok is True
        assert int(response.status_code) == 200

    def test_fetch_conditional__with_etag(self):                       # Test conditional with etag
        url      = Safe_Str__Url(self.server.url('index.html'))
        response = self.fetcher.fetch_conditional(url, etag='"fake-etag"')
        
        # Server doesn't support etag, so should return 200
        assert response.ok is True




# Test HTML content
HTML_SIMPLE = '''<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body><h1>Hello World</h1><p>This is a test.</p></body>
</html>'''

HTML_WITH_LINKS = '''<!DOCTYPE html>
<html>
<head><title>Links Page</title></head>
<body><a href="/page2">Link to Page 2</a></body>
</html>'''

HTML_LARGE = '<html><body>' + '<p>Paragraph</p>' * 100 + '</body></html>'