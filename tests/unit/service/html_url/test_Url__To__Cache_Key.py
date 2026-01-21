# ═══════════════════════════════════════════════════════════════════════════════
# test_Url__To__Cache_Key - Tests for URL to cache_key conversion
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                       import TestCase
from mgraph_ai_service_html_graph.schemas.flet.url.Schema__Url__Cache_Key__Config   import Schema__Url__Cache_Key__Config
from mgraph_ai_service_html_graph.service.html_url.Url__To__Cache_Key               import Url__To__Cache_Key
from osbot_utils.helpers.cache.Cache__Hash__Generator                               import Cache__Hash__Generator
from osbot_utils.testing.__                                                         import __


class test_Url__To__Cache_Key(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.converter      = Url__To__Cache_Key()
        cls.hash_generator = Cache__Hash__Generator()

    # ═══════════════════════════════════════════════════════════════════════════
    # test setup
    # ═══════════════════════════════════════════════════════════════════════════

    def test__setUpClass(self):
        assert type(self.converter)        is Url__To__Cache_Key
        assert type(self.converter.config) is Schema__Url__Cache_Key__Config
        assert self.converter.config.obj() == __(include_query_params = False,
                                                 sort_query_params    = True ,
                                                 query_params_as_hash = True ,
                                                 hash_length          = 12   ,
                                                 include_params       = None ,
                                                 exclude_params       = None )

    # ═══════════════════════════════════════════════════════════════════════════
    # cache_key - basic URLs
    # ═══════════════════════════════════════════════════════════════════════════

    def test__cache_key__homepage(self):
        result = self.converter.cache_key("https://example.com")
        assert result == "example.com/index"

    def test__cache_key__homepage_with_trailing_slash(self):
        result = self.converter.cache_key("https://example.com/")
        assert result == "example.com/index"

    def test__cache_key__simple_path(self):
        result = self.converter.cache_key("https://example.com/about")
        assert result == "example.com/about"

    def test__cache_key__nested_path(self):
        result = self.converter.cache_key("https://example.com/blog/posts/my-article")
        assert result == "example.com/blog/posts/my-article"

    def test__cache_key__with_subdomain(self):
        result = self.converter.cache_key("https://docs.example.com/guide")
        assert result == "docs.example.com/guide"

    def test__cache_key__with_port(self):
        result = self.converter.cache_key("https://example.com:8080/api")
        assert result == "example.com_8080/api"

    def test__cache_key__with_file_extension(self):
        result = self.converter.cache_key("https://example.com/docs/readme.html")
        assert result == "example.com/docs/readme.html"

    def test__cache_key__ignores_query_by_default(self):
        result = self.converter.cache_key("https://example.com/search?q=test&page=1")
        assert result == "example.com/search"

    def test__cache_key__ignores_fragment(self):
        result = self.converter.cache_key("https://example.com/page#section")
        assert result == "example.com/page"

    # ═══════════════════════════════════════════════════════════════════════════
    # sanitize_path
    # ═══════════════════════════════════════════════════════════════════════════

    def test__sanitize_path__empty(self):
        result = self.converter.sanitize_path("")
        assert result == "index"

    def test__sanitize_path__root(self):
        result = self.converter.sanitize_path("/")
        assert result == "index"

    def test__sanitize_path__simple(self):
        result = self.converter.sanitize_path("/about")
        assert result == "about"

    def test__sanitize_path__special_characters(self):
        result = self.converter.sanitize_path("/path with spaces & symbols!")
        assert result == "path-with-spaces-symbols"

    def test__sanitize_path__consecutive_hyphens(self):
        result = self.converter.sanitize_path("/path---with---hyphens")
        assert result == "path-with-hyphens"

    def test__sanitize_path__preserves_dots(self):
        result = self.converter.sanitize_path("/file.txt")
        assert result == "file.txt"

    def test__sanitize_path__preserves_underscores(self):
        result = self.converter.sanitize_path("/my_file_name")
        assert result == "my_file_name"

    # ═══════════════════════════════════════════════════════════════════════════
    # cache_key - with query params enabled
    # ═══════════════════════════════════════════════════════════════════════════

    def test__cache_key__with_query_params_enabled(self):
        converter = Url__To__Cache_Key(config=Schema__Url__Cache_Key__Config(include_query_params=True))

        result = converter.cache_key("https://example.com/search?q=test")

        assert result.startswith("example.com/search/q-")
        assert len(result.split("/q-")[1]) == 12                                    # hash_length default

    def test__cache_key__query_params_sorted(self):
        converter = Url__To__Cache_Key(config=Schema__Url__Cache_Key__Config(include_query_params=True))

        result_1 = converter.cache_key("https://example.com/search?a=1&b=2")
        result_2 = converter.cache_key("https://example.com/search?b=2&a=1")

        assert result_1 == result_2                                                 # Same hash regardless of order

    def test__cache_key__query_params_not_sorted(self):
        converter = Url__To__Cache_Key(config=Schema__Url__Cache_Key__Config(include_query_params = True ,
                                                                             sort_query_params    = False))

        result_1 = converter.cache_key("https://example.com/search?a=1&b=2")
        result_2 = converter.cache_key("https://example.com/search?b=2&a=1")

        assert result_1 != result_2                                                 # Different hash when not sorted

    def test__cache_key__custom_hash_length(self):
        converter = Url__To__Cache_Key(config=Schema__Url__Cache_Key__Config(include_query_params = True,
                                                                             hash_length          = 8   ))

        result = converter.cache_key("https://example.com/search?q=test")

        assert len(result.split("/q-")[1]) == 8

    def test__cache_key__query_params_inline(self):
        converter = Url__To__Cache_Key(config=Schema__Url__Cache_Key__Config(include_query_params = True ,
                                                                             query_params_as_hash = False))

        result = converter.cache_key("https://example.com/search?q=test")

        assert result == "example.com/search/q-test"

    # ═══════════════════════════════════════════════════════════════════════════
    # cache_key - include/exclude params
    # ═══════════════════════════════════════════════════════════════════════════

    def test__cache_key__exclude_params(self):
        converter = Url__To__Cache_Key(config=Schema__Url__Cache_Key__Config(include_query_params = True                             ,
                                                                             exclude_params       = ['utm_source', 'utm_medium', 'fbclid']))

        result_clean = converter.cache_key("https://example.com/page?id=123")
        result_dirty = converter.cache_key("https://example.com/page?id=123&utm_source=google&fbclid=abc")

        assert result_clean == result_dirty                                         # Tracking params excluded

    def test__cache_key__include_params(self):
        converter = Url__To__Cache_Key(config=Schema__Url__Cache_Key__Config(include_query_params = True        ,
                                                                             include_params       = ['id', 'v'] ))

        result_1 = converter.cache_key("https://example.com/api?id=123&v=2&extra=ignored")
        result_2 = converter.cache_key("https://example.com/api?id=123&v=2&other=also_ignored")

        assert result_1 == result_2                                                 # Only id and v matter

    def test__cache_key__include_params_empty_result(self):
        converter = Url__To__Cache_Key(config=Schema__Url__Cache_Key__Config(include_query_params = True  ,
                                                                             include_params       = ['id'] ))

        result = converter.cache_key("https://example.com/page?foo=bar&baz=qux")

        assert result == "example.com/page"                             # No matching params, no query part

    # ═══════════════════════════════════════════════════════════════════════════
    # process_query
    # ═══════════════════════════════════════════════════════════════════════════

    def test__process_query__empty(self):
        result = self.converter.process_query("")
        assert result == ""

    def test__process_query__single_param(self):
        converter = Url__To__Cache_Key(config=Schema__Url__Cache_Key__Config(include_query_params = True ,
                                                                             query_params_as_hash = False))
        result = converter.process_query("key=value")
        assert result == "key-value"

    # ═══════════════════════════════════════════════════════════════════════════
    # real-world URLs
    # ═══════════════════════════════════════════════════════════════════════════

    def test__cache_key__google_search(self):
        converter = Url__To__Cache_Key(config=Schema__Url__Cache_Key__Config(include_query_params = True ,
                                                                             include_params       = ['q'] ))

        result = converter.cache_key("https://www.google.com/search?q=python+tutorial&sourceid=chrome&ie=UTF-8")

        assert result.startswith("www.google.com/search/q-")

    def test__cache_key__youtube_video(self):
        converter = Url__To__Cache_Key(config=Schema__Url__Cache_Key__Config(include_query_params = True ,
                                                                             include_params       = ['v'] ))

        result = converter.cache_key("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf")

        assert result.startswith("www.youtube.com/watch/q-")

    def test__cache_key__github_file(self):
        result = self.converter.cache_key("https://github.com/owasp-dep-scan/dep-scan/blob/master/README.md")

        assert result == "github.com/owasp-dep-scan/dep-scan/blob/master/README.md"

    def test__cache_key__aws_docs(self):
        result = self.converter.cache_key("https://docs.aws.amazon.com/lambda/latest/dg/welcome.html")

        assert result == "docs.aws.amazon.com/lambda/latest/dg/welcome.html"