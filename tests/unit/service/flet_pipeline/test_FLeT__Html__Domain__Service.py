# ═══════════════════════════════════════════════════════════════════════════════
# Test__FLeT__Html__Domain__Service - Tests for domain-level HTML service
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                       import TestCase
from mgraph_ai_service_cache_client.client.cache_client.Cache__Service__Client                      import Cache__Service__Client
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                   import fast_api__service__registry
from mgraph_ai_service_cache_client.client.cache_service.register_cache_service                     import register_cache_service__in_memory
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Load__Hash__Request             import Schema__Html__Load__Hash__Request
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Load__Id__Request               import Schema__Html__Load__Id__Request
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Load__Response                  import Schema__Html__Load__Response
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Load__Url__Request              import Schema__Html__Load__Url__Request
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Store__Key__Request             import Schema__Html__Store__Key__Request
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Store__Raw__Request             import Schema__Html__Store__Raw__Request
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Store__Response                 import Schema__Html__Store__Response
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Store__Url__Request             import Schema__Html__Store__Url__Request
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                          import Html_Cache__Client
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Namespace                       import Html_Cache__Namespace
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.FLeT__Html__Domain__Service            import FLeT__Html__Domain__Service
from osbot_utils.testing.Stderr                                                                     import Stderr
from osbot_utils.testing.Temp_Folder                                                                import Temp_Folder
from osbot_utils.testing.Temp_Web_Server                                                            import Temp_Web_Server
from osbot_utils.testing.__                                                                         import __, __SKIP__
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid                               import Random_Guid
from osbot_utils.utils.Http                                                                         import GET


class test_FLeT__Html__Domain__Service(TestCase):

    @classmethod
    def setUpClass(cls):                                                          # Shared test objects
        cls.cache_service_client = register_cache_service__in_memory(return_client=True)
        cls.service_config       = fast_api__service__registry.config(Cache__Service__Client)
        cls.cache_service        = cls.service_config.fast_api.cache_service
        cls.html_cache_client    = Html_Cache__Client()
        cls.domain_service       = FLeT__Html__Domain__Service(html_cache_client=cls.html_cache_client)
        cls.namespace            = 'test-flet-domain-service'
        cls.test_html            = '<html><body><h1>Test Domain Content</h1></body></html>'

    def setUp(self):                                                              # Per-test setup
        self.cache_key  = f'test/domain/{Random_Guid()}'
        self.cache_hash = self.html_cache_client.hash_generator.from_string(self.cache_key)

    # ═══════════════════════════════════════════════════════════════════════════
    # store_raw Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__store_raw__empty_html_returns_failure(self):
        request = Schema__Html__Store__Raw__Request(html='')

        result = self.domain_service.store_raw(namespace=self.namespace, request=request)

        assert type(result)   is Schema__Html__Store__Response
        assert result.success is False

    def test__store_raw__success(self):
        html       = self.test_html
        html_hash  = self.cache_service.hash__from_string(html)
        cache_key  = f'html/raw/{html_hash}'
        cache_hash = self.cache_service.hash__from_string(cache_key)
        char_count = len(html)
        request    = Schema__Html__Store__Raw__Request(html=html)

        result = self.domain_service.store_raw(namespace=self.namespace, request=request)

        assert result.success        is True
        assert result.cache_id       != ''
        assert result.cache_key      == cache_key  == 'html/raw/ab6ffe5a553d343d'
        assert result.cache_hash     == cache_hash == 'fe156312edd6eeca'
        assert result.char_count     == char_count == 54

        assert result.obj()          == __(success     = True      ,
                                           cache_id    = __SKIP__  ,
                                           cache_key   = cache_key ,
                                           cache_hash  = cache_hash,
                                           char_count  = char_count,
                                           final_url   = ''        )

    def test__store_raw__same_content_returns_same_entity(self):
        request = Schema__Html__Store__Raw__Request(html=self.test_html)

        result_1 = self.domain_service.store_raw(namespace=self.namespace, request=request)
        result_2 = self.domain_service.store_raw(namespace=self.namespace, request=request)

        assert result_1.cache_id  == result_2.cache_id                             # Same content = same entity
        assert result_1.cache_key == result_2.cache_key

    def test__store_raw__different_content_creates_different_entities(self):
        request_1 = Schema__Html__Store__Raw__Request(html='<html>Content 1</html>')
        request_2 = Schema__Html__Store__Raw__Request(html='<html>Content 2</html>')

        result_1 = self.domain_service.store_raw(namespace=self.namespace, request=request_1)
        result_2 = self.domain_service.store_raw(namespace=self.namespace, request=request_2)

        assert result_1.cache_id != result_2.cache_id                             # Different entities

    # ═══════════════════════════════════════════════════════════════════════════
    # store_with_key Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__store_with_key__empty_html_returns_failure(self):
        request = Schema__Html__Store__Key__Request(html='')

        result = self.domain_service.store_with_key(namespace=self.namespace, cache_key=self.cache_key, request=request)

        assert result.success is False

    def test__store_with_key__empty_key_returns_failure(self):
        request = Schema__Html__Store__Key__Request(html=self.test_html)

        result = self.domain_service.store_with_key(namespace=self.namespace, cache_key='', request=request)

        assert result.success is False

    def test__store_with_key__success(self):
        request = Schema__Html__Store__Key__Request(html=self.test_html)

        result = self.domain_service.store_with_key(namespace=self.namespace, cache_key=self.cache_key, request=request)

        assert result.success    is True
        assert result.cache_id   != ''
        assert result.cache_key  == self.cache_key
        assert result.char_count == len(self.test_html)

    def test__store_with_key__creates_entity_first_time(self):
        request = Schema__Html__Store__Key__Request(html=self.test_html)
        result = self.domain_service.store_with_key(namespace=self.namespace, cache_key=self.cache_key, request=request)
        assert result.success        is True

    def test__store_with_key__uses_existing_entity(self):
        request = Schema__Html__Store__Key__Request(html=self.test_html)

        result_1 = self.domain_service.store_with_key(namespace=self.namespace, cache_key=self.cache_key, request=request)
        result_2 = self.domain_service.store_with_key(namespace=self.namespace, cache_key=self.cache_key, request=request)

        assert result_1.cache_id == result_2.cache_id

    # ═══════════════════════════════════════════════════════════════════════════
    # load_by_id Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__load_by_id__empty_id_returns_failure(self):
        request = Schema__Html__Load__Id__Request(cache_id='')

        result = self.domain_service.load_by_id(namespace=self.namespace, request=request)

        assert type(result)   is Schema__Html__Load__Response
        assert result.success is False

    def test__load_by_id__success(self):
        store_request = Schema__Html__Store__Key__Request(html=self.test_html)
        store_result  = self.domain_service.store_with_key(namespace=self.namespace, cache_key=self.cache_key, request=store_request)

        load_request = Schema__Html__Load__Id__Request(cache_id=store_result.cache_id)

        result = self.domain_service.load_by_id(namespace=self.namespace, request=load_request)

        assert result.success    is True
        assert result.cache_id   == store_result.cache_id
        assert result.html       == self.test_html
        assert result.found      is True
        assert result.char_count == len(self.test_html)

    # ═══════════════════════════════════════════════════════════════════════════
    # load_by_hash Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__load_by_hash__empty_hash_returns_failure(self):
        request = Schema__Html__Load__Hash__Request(cache_hash='')

        result = self.domain_service.load_by_hash(namespace=self.namespace, request=request)

        assert result.success is False

    def test__load_by_hash__not_found(self):
        request = Schema__Html__Load__Hash__Request(cache_hash='aaaaa12345')

        result = self.domain_service.load_by_hash(namespace=self.namespace, request=request)

        assert result.success is True
        assert result.found   is False
        assert result.obj()   == __(success=True,
                                    cache_id='',
                                    cache_key='',
                                    html='',
                                    found=False,
                                    char_count=0)


    # ═══════════════════════════════════════════════════════════════════════════
    # load_by_key Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__load_by_key__empty_key_returns_failure(self):
        result = self.domain_service.load_by_key(namespace=self.namespace, cache_key='')

        assert result.success is False

    def test__load_by_key__not_found(self):
        result = self.domain_service.load_by_key(namespace=self.namespace, cache_key='aaaaa12345')

        assert result.success is True
        assert result.found   is False

    def test__load_by_key__success(self):
        store_request = Schema__Html__Store__Key__Request(html=self.test_html)
        self.domain_service.store_with_key(namespace=self.namespace, cache_key=self.cache_key, request=store_request)

        result = self.domain_service.load_by_key(namespace=self.namespace, cache_key=self.cache_key)

        assert result.success   is True
        assert result.found     is True
        assert result.cache_key == self.cache_key
        assert result.html      == self.test_html

    # ═══════════════════════════════════════════════════════════════════════════
    # load_by_url Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__load_by_url__empty_url_returns_failure(self):
        request = Schema__Html__Load__Url__Request(url='')

        result = self.domain_service.load_by_url(namespace=self.namespace, request=request)

        assert result.success is False

    def test__load_by_url__not_found(self):
        request = Schema__Html__Load__Url__Request(url=f'https://example.com/{Random_Guid()}')

        result = self.domain_service.load_by_url(namespace=self.namespace, request=request)

        assert result.success is True
        assert result.found   is False

    def test__load_by_url__success_when_stored_with_url_as_key(self):
        random_guid    = Random_Guid()
        url            = f'https://example.com/page/{random_guid}'
        cache_key      = self.domain_service.url_to_cache_key.cache_key(url)
        store_request  = Schema__Html__Store__Key__Request(html=self.test_html)
        store_response = self.domain_service.store_with_key(namespace=self.namespace, cache_key=cache_key, request=store_request)
        cache_id       = store_response.cache_id

        load_request = Schema__Html__Load__Url__Request(url=url)

        result = self.domain_service.load_by_url(namespace=self.namespace, request=load_request)

        assert result.success   is True
        assert result.found     is True
        assert result.html      == self.test_html
        assert result.cache_key == cache_key
        assert cache_key        == f'example.com/page/{random_guid}'

    # ═══════════════════════════════════════════════════════════════════════════
    # store_from_url Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_store_from_url(self):
        with Stderr():                  # to su
            with Temp_Folder() as temp_folder:
                with Temp_Web_Server(root_folder=temp_folder.full_path) as _:
                    file_path  = 'an-path/with-an-file.html'
                    file_url   = f'http://127.0.0.1:{_.port}/{file_path}'
                    cache_key  = f'127.0.0.1_{_.port}/{file_path}'
                    cache_hash = self.cache_service.hash__from_string(cache_key)

                    _.add_file(file_path, self.test_html)

                    request = Schema__Html__Store__Url__Request(url=file_url)
                    result  = self.domain_service.store_from_url(namespace=self.namespace, request=request)
                    cache_id = result.cache_id

                    assert _.url(file_path) == file_url
                    assert GET(file_url)     == self.test_html
                    assert result.cache_key  == f'127.0.0.1_{_.port}/an-path/with-an-file.html'
                    assert result.cache_key  == cache_key
                    assert result.cache_key  == self.domain_service.url_to_cache_key.cache_key(file_url)
                    assert result.final_url  == f'http://127.0.0.1:{_.port}/an-path/with-an-file.html'
                    assert result.cache_hash == cache_hash
                    assert result.cache_hash == self.cache_service.hash__from_string(cache_key)
                    assert result.obj()      == __(success=True,
                                                   cache_id   = cache_id  ,
                                                   cache_key  = cache_key ,
                                                   cache_hash = cache_hash,
                                                   char_count = 54        ,
                                                   final_url  = file_url )

        with Html_Cache__Namespace(html_cache_client = self.html_cache_client,
                                   namespace         = self.namespace) as cache_namespace:
            with cache_namespace.entity(cache_id=cache_id) as cache_entity:
                assert cache_entity.entry__json()        == {'cache_key': cache_key }
                assert cache_entity.data__files__paths() == [f'test-flet-domain-service/data/key-based/{cache_key}/root/data/html/raw.txt',
                                                             f'test-flet-domain-service/data/key-based/{cache_key}/root/data/flows/html-to-cache/flow-data.json'] != []
                assert cache_entity.cache__hash()        == cache_hash





    # ═══════════════════════════════════════════════════════════════════════════
    # Roundtrip Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__store_and_load_roundtrip__preserves_content(self):
        complex_html = '''<!DOCTYPE html>
<html>
<head><title>Complex Test</title></head>
<body>
    <h1>Title</h1>
    <p>Paragraph with special chars: &amp; &lt; &gt;</p>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
    </ul>
</body>
</html>'''

        store_request = Schema__Html__Store__Key__Request(html=complex_html)
        store_result  = self.domain_service.store_with_key(namespace=self.namespace, cache_key=self.cache_key, request=store_request)
        load_result   = self.domain_service.load_by_key   (namespace=self.namespace, cache_key=self.cache_key)

        cache_id      = load_result.cache_id
        assert load_result.html   == complex_html                                   # Content preserved
        assert store_result.obj() == __(success    = True           ,
                                        cache_id   = cache_id       ,
                                        cache_key  = self.cache_key ,
                                        cache_hash = self.cache_hash,
                                        char_count = 229            ,
                                        final_url  = ''             )
        assert load_result.obj()  == __(success    =True            ,
                                        cache_id   = cache_id       ,
                                        cache_key  = self.cache_key ,
                                        html       = complex_html   ,
                                        found      = True           ,
                                        char_count = 229            )

    def test__store_raw_and_load_by_id__roundtrip(self):
        request = Schema__Html__Store__Raw__Request(html=self.test_html)

        store_result = self.domain_service.store_raw(namespace=self.namespace, request=request)

        load_request = Schema__Html__Load__Id__Request(cache_id=store_result.cache_id)
        load_result  = self.domain_service.load_by_id(namespace=self.namespace, request=load_request)

        assert load_result.success is True
        assert load_result.html    == self.test_html

    # ═══════════════════════════════════════════════════════════════════════════
    # Service Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__creates_services_from_cache_client(self):
        service = FLeT__Html__Domain__Service(html_cache_client=self.html_cache_client)

        assert service.html_cache_client is self.html_cache_client
        assert service.entity_service  is not None
        assert service.execute_service is not None
        assert service.url_fetcher     is not None
        assert service.hash_generator  is not None
