# ═══════════════════════════════════════════════════════════════════════════════
# test_FLeT__Html__From__Cache - Tests for HTML from cache FLeT
# Tests retrieving HTML from cache by hash, URL, or key
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                                                      import TestCase
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.FLeT__Html__To__Cache                           import FLeT__Html__To__Cache
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Save__Output import Schema__Html_To_Cache__Save__Output
from osbot_utils.testing.__ import __, __SKIP__
from osbot_utils.type_safe.Type_Safe                                                                                               import Type_Safe
from osbot_utils.utils.Objects                                                                                                     import base_types
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace                                             import Safe_Str__Namespace
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Cache_Hash                                           import Safe_Str__Cache_Hash
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                                                 import Cache_Id
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.base.Html_FLeT__Base                                                  import Html_FLeT__Base
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                                                           import create_html_cache_client
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.FLeT__Html__From__Cache                       import FLeT__Html__From__Cache
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.schemas.Schema__Html_From_Cache__Load__Input  import Schema__Html_From_Cache__Load__Input
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.schemas.Schema__Html_From_Cache__Save__Output import Schema__Html_From_Cache__Save__Output


class test_FLeT__Html__From__Cache(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cache_client, cls.cache_service = create_html_cache_client()
        cls.namespace    = 'test-html-from-cache'
        cls.sample_html  = '<html><body><p>Cached content for retrieval</p></body></html>'

        # Store HTML first so we have something to retrieve
        cls.store_result = FLeT__Html__To__Cache.from_html(html        = cls.sample_html  ,
                                                           cache_client= cls.cache_client ,
                                                           namespace   = cls.namespace    )
        cls.stored_cache_id  = cls.store_result.cache_id
        cls.stored_html_hash = cls.store_result.html_hash

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__setUpClass(self):
        with self.store_result as _:
            cache_id         = self.stored_cache_id
            namespace        = self.namespace
            stored_file      =  self.cache_client.cache_client.retrieve().retrieve__cache_id      (cache_id = cache_id, namespace = namespace )
            stored_file_refs =  self.cache_client.cache_client.retrieve().retrieve__cache_id__refs(cache_id = cache_id, namespace = namespace )
            html_hash        = self.cache_client.hash_generator.from_string(self.sample_html)
            cache_hash       = '0d5d33c4f7d1f3ff'    # todo: how is this calculated?
            file_id          = 'html-content'        # todo: how is this calculated?

            cache_id_sharded   = f"{cache_id[0:2]}/{cache_id[2:4]}/{cache_id}"
            cache_hash_sharded = f"{cache_hash[0:2]}/{cache_hash[2:4]}/{cache_hash}"
            file_folder        = f'{namespace}/data/key-based/{html_hash}'


            assert type(_)                is Schema__Html_To_Cache__Save__Output
            assert html_hash              == '1cda567bc533ce45'
            assert _.obj()                == __(success    = True      ,
                                                cache_id   = cache_id  ,
                                                html_hash  = html_hash ,
                                                cache_key  = html_hash ,
                                                namespace  = namespace ,
                                                from_cache = False     ,
                                                data_key   = ''        )
            assert _.html_hash            == html_hash
            assert stored_file.obj()      == __(data      = __(html             = self.sample_html       ,
                                                               cache_hash       = html_hash              ,
                                                               char_count       = len(self.sample_html)) ,
                                                metadata  = __(cache_id         = cache_id               ,
                                                               cache_hash       = cache_hash             ,
                                                               cache_key        = html_hash              ,
                                                               file_id          = file_id                ,
                                                               namespace        = namespace              ,
                                                               strategy         = 'key_based'            ,
                                                               stored_at        = __SKIP__               ,
                                                               file_type        = 'json'                 ,
                                                               content_encoding = None                   ,
                                                               content_size     = 0                      ),
                                                data_type = 'json')


            assert stored_file_refs.obj() == __(all_paths  = __(data    = [ f'{file_folder}/html-content.json'                   ,
                                                                            f'{file_folder}/html-content.json.config'            ,
                                                                            f'{file_folder}/html-content.json.metadata'          ],
                                                                by_hash = [ f'{namespace}/refs/by-hash/{cache_hash_sharded}.json'],
                                                                by_id   = [ f'{namespace}/refs/by-id/{cache_id_sharded}.json'    ]),
                                                cache_id    = cache_id,
                                                cache_hash = cache_hash,
                                                file_type  = 'json',
                                                namespace  = namespace ,
                                                file_paths = __(content_files = [f'{file_folder}/html-content.json'],
                                                                data_folders  = [f'{file_folder}/html-content/data']),
                                                strategy    ='key_based',
                                                timestamp   = __SKIP__)

    def test__init__(self):
        with FLeT__Html__From__Cache() as _:
            assert type(_)        is FLeT__Html__From__Cache
            assert base_types(_)  == [Html_FLeT__Base, Type_Safe, object]
            assert _.cache_client is None
            assert _.config       is None

    def test__init____with_cache_client(self):
        with FLeT__Html__From__Cache(cache_client=self.cache_client) as _:
            assert _.cache_client is self.cache_client

    def test__init____actions_wired(self):
        with FLeT__Html__From__Cache() as _:
            assert _.load      is not None
            assert _.extract   is not None
            assert _.transform is not None
            assert _.save      is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # Setup Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_setup(self):
        with FLeT__Html__From__Cache() as _:
            result = _.setup()

            assert result        is _
            assert _.config      is not None
            assert _.config.name == 'html-from-cache'
            assert 'cache'       in _.config.description.lower()
            assert type(result)  is FLeT__Html__From__Cache
            assert result.obj()  == __(cache_client=None,
                                       config=__(name='html-from-cache',
                                                 description='Retrieve HTML from cache by hash, URL, or key',
                                                 schema__input=None,
                                                 schema__output=None),
                                       document=None,
                                       flow=None,
                                       output=None,
                                       load='action__html_from_cache__load',
                                       extract='action__html_from_cache__extract',
                                       transform='action__html_from_cache__transform',
                                       save='action__html_from_cache__save')

    def test_setup__returns_self(self):
        flet = FLeT__Html__From__Cache().setup()
        assert type(flet)       is FLeT__Html__From__Cache
        assert flet.config.name == 'html-from-cache'

    # ═══════════════════════════════════════════════════════════════════════════
    # Execute Tests (without cache client)
    # ═══════════════════════════════════════════════════════════════════════════

    def test_execute__without_cache_client(self):
        flet       = FLeT__Html__From__Cache().setup()
        input_data = Schema__Html_From_Cache__Load__Input(namespace = Safe_Str__Namespace(self.namespace),
                                                          html_hash = self.stored_html_hash              )

        result = flet.execute(input_data)

        assert type(result)   is Schema__Html_From_Cache__Save__Output
        assert result.success is False                                               # No cache client = can't retrieve
        assert result.found   is False

    # ═══════════════════════════════════════════════════════════════════════════
    # Execute Tests (with cache client) - By Hash
    # ═══════════════════════════════════════════════════════════════════════════

    def test_execute__by_hash(self):
        flet       = FLeT__Html__From__Cache(cache_client=self.cache_client).setup()
        input_data = Schema__Html_From_Cache__Load__Input(namespace = Safe_Str__Namespace(self.namespace),
                                                          html_hash = self.stored_html_hash              )

        result = flet.execute(input_data)

        assert type(result)       is Schema__Html_From_Cache__Save__Output
        assert result.success     is True
        assert result.found       is True
        assert str(result.html)   == self.sample_html
        assert result.html_hash   == self.stored_html_hash

    def test_execute__by_hash__not_found(self):
        flet       = FLeT__Html__From__Cache(cache_client=self.cache_client).setup()
        input_data = Schema__Html_From_Cache__Load__Input(namespace = Safe_Str__Namespace(self.namespace)        ,
                                                          html_hash = Safe_Str__Cache_Hash('aaaaa12345'))

        result = flet.execute(input_data)

        assert result.success is False
        assert result.found   is False
        assert str(result.html) == ''

    # ═══════════════════════════════════════════════════════════════════════════
    # Execute Tests (with cache client) - By Cache ID
    # ═══════════════════════════════════════════════════════════════════════════

    def test_execute__by_cache_id(self):
        flet       = FLeT__Html__From__Cache(cache_client=self.cache_client).setup()
        input_data = Schema__Html_From_Cache__Load__Input(namespace = Safe_Str__Namespace(self.namespace),
                                                          cache_id  = self.stored_cache_id               )

        result = flet.execute(input_data)

        assert result.success   is True
        assert result.found     is True
        assert str(result.html) == self.sample_html

    # ═══════════════════════════════════════════════════════════════════════════
    # Convenience Method Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_by_hash__class_method(self):
        result = FLeT__Html__From__Cache.by_hash(html_hash   = self.stored_html_hash,
                                                 cache_client= self.cache_client    ,
                                                 namespace   = self.namespace       )
        assert type(result)     is Schema__Html_From_Cache__Save__Output
        assert result.obj()     == __(success   = False ,
                                      cache_id  = ''    ,
                                      html_hash =''     ,
                                      html      = ''    ,
                                      found     = False ,
                                      data_key  = ''    )

        assert result.success   is True
        assert result.found     is True
        assert str(result.html) == self.sample_html

    def test_by_cache_id__classmethod(self):
        result = FLeT__Html__From__Cache.by_cache_id(cache_id    = str(self.stored_cache_id),
                                                     cache_client= self.cache_client        ,
                                                     namespace   = self.namespace           )

        assert result.success   is True
        assert result.found     is True

    # ═══════════════════════════════════════════════════════════════════════════
    # Round-Trip Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_round_trip__store_and_retrieve(self):
        unique_html = '<div>Round trip test unique content 12345</div>'

        # Store
        store_result = FLeT__Html__To__Cache.from_html(html        = unique_html      ,
                                                       cache_client= self.cache_client,
                                                       namespace   = self.namespace   )

        assert store_result.success is True

        # Retrieve by hash
        retrieve_result = FLeT__Html__From__Cache.by_hash(html_hash   = str(store_result.html_hash),
                                                          cache_client= self.cache_client          ,
                                                          namespace   = self.namespace             )

        assert retrieve_result.success   is True
        assert retrieve_result.found     is True
        assert str(retrieve_result.html) == unique_html

    def test_round_trip__multiple_store_same_content(self):
        same_html = '<p>Same content multiple times</p>'

        # Store twice
        result1 = FLeT__Html__To__Cache.from_html(html=same_html, cache_client=self.cache_client, namespace=self.namespace)
        result2 = FLeT__Html__To__Cache.from_html(html=same_html, cache_client=self.cache_client, namespace=self.namespace)

        # Same hash, second from cache
        assert result1.html_hash  == result2.html_hash
        assert result1.from_cache is False
        assert result2.from_cache is True

        # Retrieve once
        retrieve = FLeT__Html__From__Cache.by_hash(html_hash   = str(result1.html_hash),
                                                   cache_client= self.cache_client     ,
                                                   namespace   = self.namespace        )

        assert retrieve.found       is True
        assert str(retrieve.html)   == same_html

    # ═══════════════════════════════════════════════════════════════════════════
    # Observability Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_observability__after_execute(self):
        flet       = FLeT__Html__From__Cache(cache_client=self.cache_client).setup()
        input_data = Schema__Html_From_Cache__Load__Input(namespace = Safe_Str__Namespace(self.namespace),
                                                          html_hash = self.stored_html_hash              )

        flet.execute(input_data)

        assert flet.flow   is not None
        assert flet.output is not None
        assert type(flet.durations()) is dict


class test_FLeT__Html__From__Cache__Schemas(TestCase):

    def test_Schema__Html_From_Cache__Load__Input(self):
        schema = Schema__Html_From_Cache__Load__Input(namespace = Safe_Str__Namespace('test-ns')      ,
                                                      cache_id  = Cache_Id('cache-123')               ,
                                                      html_hash = Safe_Str__Cache_Hash('hash-abc')    ,
                                                      url       = 'https://example.com'               )

        assert str(schema.namespace) == 'test-ns'
        assert str(schema.cache_id)  == 'cache-123'
        assert str(schema.html_hash) == 'hash-abc'
        assert schema.url            == 'https://example.com'

    def test_Schema__Html_From_Cache__Save__Output(self):
        schema = Schema__Html_From_Cache__Save__Output(success   = True               ,
                                                       html      = '<p>test</p>'      ,
                                                       html_hash = 'hash-xyz'         ,
                                                       found     = True               )

        assert schema.success       is True
        assert schema.found         is True
        assert str(schema.html)     == '<p>test</p>'
