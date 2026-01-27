# ═══════════════════════════════════════════════════════════════════════════════
# Test__FLeT__Html__Execute__Service - Tests for FLeT HTML execution service
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                       import TestCase

from mgraph_ai_service_cache_client.client.cache_service.register_cache_service import register_cache_service__in_memory
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client import Html_Cache__Client
from osbot_utils.testing.__                                                                         import __
from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type                      import Enum__Cache__Data_Type
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Namespace                       import Html_Cache__Namespace
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid                               import Random_Guid
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Create__Request              import Schema__Entity__Create__Request
from mgraph_ai_service_html_graph.schemas.flet.html.Schema__FLeT__Html__From__Cache__Request        import Schema__FLeT__Html__From__Cache__Request
from mgraph_ai_service_html_graph.schemas.flet.html.Schema__FLeT__Html__From__Cache__Response       import Schema__FLeT__Html__From__Cache__Response
from mgraph_ai_service_html_graph.schemas.flet.html.Schema__FLeT__Html__To__Cache__Request          import Schema__FLeT__Html__To__Cache__Request
from mgraph_ai_service_html_graph.schemas.flet.html.Schema__FLeT__Html__To__Cache__Response         import Schema__FLeT__Html__To__Cache__Response
from mgraph_ai_service_html_graph.service.cache.Cache__Entity__Service                              import Cache__Entity__Service
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.FLeT__Html__Execute__Service           import FLeT__Html__Execute__Service


class test_FLeT__Html__Execute__Service(TestCase):

    @classmethod
    def setUpClass(cls):                                                          # Shared test objects
        cls.cache_service_client = register_cache_service__in_memory(return_client=True)
        cls.html_cache_client    = Html_Cache__Client()
        cls.entity_service       = Cache__Entity__Service      (html_cache_client=cls.html_cache_client)
        cls.execute_service      = FLeT__Html__Execute__Service(html_cache_client=cls.html_cache_client)
        cls.namespace            = 'test-flet-execute-service'
        cls.test_html            = '<html><body><h1>Test Content</h1></body></html>'

    def setUp(self):                                                              # Per-test setup
        self.cache_key = f'test/execute/{Random_Guid()}'

        create_request    = Schema__Entity__Create__Request(cache_key=self.cache_key)
        create_result     = self.entity_service.create     (namespace=self.namespace, request=create_request)
        self.cache_id     = create_result.cache_id

    # ═══════════════════════════════════════════════════════════════════════════
    # execute_to_cache Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__execute_to_cache__empty_html_returns_failure(self):
        request = Schema__FLeT__Html__To__Cache__Request(html='')

        result = self.execute_service.execute_to_cache(namespace=self.namespace, cache_id=self.cache_id, request=request)

        assert type(result)   is Schema__FLeT__Html__To__Cache__Response
        assert result.success is False

    def test__execute_to_cache__entity_not_found_raises(self):
        request = Schema__FLeT__Html__To__Cache__Request(html=self.test_html)

        with self.assertRaises(ValueError) as context:
            self.execute_service.execute_to_cache(namespace=self.namespace, cache_id=Random_Guid(), request=request)

        assert 'Entity not found' in str(context.exception)

    def test__execute_to_cache__success(self):
        request = Schema__FLeT__Html__To__Cache__Request(html=self.test_html)

        result = self.execute_service.execute_to_cache(namespace=self.namespace, cache_id=self.cache_id, request=request)

        assert result.success      is True
        assert result.cache_id     == self.cache_id
        assert result.char_count   == len(self.test_html)
        assert result.flow_saved   is True
        assert result.data_key     == 'html'
        assert result.data_file_id == 'raw'


    def test__execute_to_cache__with_custom_data_key(self):
        request = Schema__FLeT__Html__To__Cache__Request(html=self.test_html, data_key='custom/path', data_file_id='content')

        result = self.execute_service.execute_to_cache(namespace=self.namespace, cache_id=self.cache_id, request=request)

        assert result.success      is True
        assert result.data_key     == 'custom/path'
        assert result.data_file_id == 'content'

    def test__execute_to_cache__stores_html_retrievable(self):
        request = Schema__FLeT__Html__To__Cache__Request(html=self.test_html)
        self.execute_service.execute_to_cache(namespace=self.namespace, cache_id=self.cache_id, request=request)

        from_request = Schema__FLeT__Html__From__Cache__Request()
        from_result  = self.execute_service.execute_from_cache(namespace=self.namespace, cache_id=self.cache_id, request=from_request)

        assert from_result.success is True
        assert from_result.html    == self.test_html

    # ═══════════════════════════════════════════════════════════════════════════
    # execute_from_cache Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__execute_from_cache__entity_not_found_raises(self):
        request = Schema__FLeT__Html__From__Cache__Request()

        with self.assertRaises(ValueError) as context:
            self.execute_service.execute_from_cache(namespace=self.namespace, cache_id=Random_Guid(), request=request)

        assert 'Entity not found' in str(context.exception)

    def test__execute_from_cache__not_found_in_cache(self):
        request = Schema__FLeT__Html__From__Cache__Request(data_key='nonexistent', data_file_id='missing')

        result = self.execute_service.execute_from_cache(namespace=self.namespace, cache_id=self.cache_id, request=request)

        assert type(result)      is Schema__FLeT__Html__From__Cache__Response
        assert result.success    is True
        assert result.found      is False
        assert result.html       == ''
        assert result.char_count == 0

    def test__execute_from_cache__success(self):
        to_request = Schema__FLeT__Html__To__Cache__Request(html=self.test_html)
        self.execute_service.execute_to_cache(namespace=self.namespace, cache_id=self.cache_id, request=to_request)

        from_request = Schema__FLeT__Html__From__Cache__Request()

        result = self.execute_service.execute_from_cache(namespace=self.namespace, cache_id=self.cache_id, request=from_request)

        assert result.success    is True
        assert result.cache_id   == self.cache_id
        assert result.html       == self.test_html
        assert result.found      is True
        assert result.char_count == len(self.test_html)
        assert result.flow_saved is True

    def test__execute_from_cache__with_custom_data_key(self):
        html         = self.test_html
        data_key     = 'custom/path'
        data_file_id = 'content'
        to_request       = Schema__FLeT__Html__To__Cache__Request  (html         = html          ,
                                                                    data_key     = data_key      ,
                                                                    data_file_id = data_file_id  )
        result__to_cache = self.execute_service.execute_to_cache   (namespace    = self.namespace,
                                                                    cache_id     = self.cache_id ,
                                                                    request      = to_request    )
        from_request     = Schema__FLeT__Html__From__Cache__Request(data_key     = data_key      ,
                                                                    data_file_id = data_file_id  )

        result__from_cache = self.execute_service.execute_from_cache(namespace = self.namespace,
                                                                     cache_id  = self.cache_id,
                                                                     request   = from_request)

        assert result__to_cache  .obj()  == __(success      = True          ,
                                               cache_id     = self.cache_id ,
                                               char_count   = len(html)     ,
                                               data_key     = data_key      ,
                                               data_file_id = data_file_id  ,
                                               flow_saved   = True          )
        assert result__from_cache.obj()  == __(success      = True          ,
                                               cache_id     = self.cache_id ,
                                               html         = html          ,
                                               found        = True          ,
                                               char_count   = 47            ,
                                               flow_saved   = True          )

        assert result__from_cache.success is True
        assert result__from_cache.found   is True                      # BUG
        assert result__from_cache.html    == self.test_html            # BUG

        exists = self.html_cache_client.data__exists(namespace    = self.namespace,
                                                     cache_id     = self.cache_id,
                                                     data_key     = data_key,
                                                     data_file_id = data_file_id,
                                                     data_type    = Enum__Cache__Data_Type.STRING)
        assert exists is True

        with Html_Cache__Namespace(html_cache_client= self.html_cache_client, namespace = self.namespace) as cache_namespace:
            with cache_namespace.entity(cache_id = self.cache_id ) as entity:
                assert entity.exists()              is True
                assert entity.data__files__paths() == [f'test-flet-execute-service/data/key-based/{self.cache_key}/root/data/{data_key}/{data_file_id}.txt'                        ,
                                                       f'test-flet-execute-service/data/key-based/{self.cache_key}/root/data/flows/html-to-cache/flow-data.json'  ,
                                                       f'test-flet-execute-service/data/key-based/{self.cache_key}/root/data/flows/html-from-cache/flow-data.json']


    def test__execute_roundtrip__preserves_html_content(self):
        complex_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test Page</title>
</head>
<body>
    <h1>Hello World</h1>
    <p>Special chars: &amp; &lt; &gt; "quotes"</p>
    <script>console.log("test");</script>
</body>
</html>'''

        to_request = Schema__FLeT__Html__To__Cache__Request(html=complex_html)
        self.execute_service.execute_to_cache(namespace=self.namespace, cache_id=self.cache_id, request=to_request)

        from_request = Schema__FLeT__Html__From__Cache__Request()
        result = self.execute_service.execute_from_cache(namespace=self.namespace, cache_id=self.cache_id, request=from_request)

        assert result.html == complex_html                                        # Content preserved exactly
