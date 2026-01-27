# ═══════════════════════════════════════════════════════════════════════════════
# test_FLeT__Html__To__Cache - Tests for HTML to cache FLeT
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                                                import TestCase
from mgraph_ai_service_cache_client.client.cache_client.Cache__Service__Client                                               import Cache__Service__Client
from mgraph_ai_service_cache_client.client.cache_service.register_cache_service                                              import register_cache_service__in_memory
from mgraph_ai_service_cache_client.client.client_entities.Cache__Entity                                                     import Cache__Entity
from mgraph_ai_service_cache_client.client.client_entities.Cache__Entity__Json_File                                          import Cache__Entity__Json_File
from mgraph_ai_service_cache_client.schemas.cache.store.Schema__Cache__Store__Metadata                                       import Schema__Cache__Store__Metadata
from mgraph_ai_service_cache_client.schemas.cache.Schema__Cache__Retrieve__Success                                           import Schema__Cache__Retrieve__Success
from mgraph_ai_service_cache_client.schemas.cache.file.Schema__Cache__File__Metadata                                         import Schema__Cache__File__Metadata
from mgraph_ai_service_cache_client.schemas.cache.file.Schema__Cache__File__Refs                                             import Schema__Cache__File__Refs
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                                                   import Html_Cache__Client
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__Cache_Key                                  import Safe_Str__Cache__File__Cache_Key
from mgraph_ai_service_html_graph.service.cache_storage.schemas.Schema__Html_Cache__Entry                                    import Schema__Html_Cache__Entry
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.base.Html_FLeT__Base                                            import Html_FLeT__Base
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.base.Html_FLeT__Flow                                            import Html_FLeT__Flow
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.Schema__FLeT__Execution__Result                         import Schema__FLeT__Execution__Result
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.FLeT__Html__To__Cache                     import FLeT__Html__To__Cache
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Input      import Schema__Html_To_Cache__Input, DEFAULT__HTML_TO_CACHE__DATA_KEY, DEFAULT__HTML_TO_CACHE__DATA_FILE_ID
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Output     import Schema__Html_To_Cache__Output
from osbot_utils.testing.__                                                                                                  import __, __SKIP__
from osbot_utils.testing.__helpers                                                                                           import obj
from osbot_utils.type_safe.Type_Safe                                                                                         import Type_Safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash                                           import safe_str_hash
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                                                    import Safe_Str__Html
from osbot_utils.utils.Json                                                                                                  import json_dumps
from osbot_utils.utils.Misc                                                                                                  import is_guid
from osbot_utils.utils.Objects                                                                                               import base_types


class test_FLeT__Html__To__Cache(TestCase):

    @classmethod
    def setUpClass(cls):                                                                  # Shared test objects
        cls.cache_service_client = register_cache_service__in_memory(return_client=True)
        cls.cache_client         = Html_Cache__Client()
        cls.cache_key            = 'test/entity'
        cls.file_id              = 'root'
        cls.json_field_path      = 'cache_hash'
        cls.namespace            = 'test-html-to-cache'
        cls.sample_html          = '<html><body><p>Test content</p></body></html>'
        cls.cache_id             = cls.create_test_entity()

    @classmethod
    def create_test_entity(cls):                                                          # Create entity for tests
        entry    = Schema__Html_Cache__Entry()
        response = cls.cache_client.entry__store(namespace       = cls.namespace        ,
                                                 cache_key       = cls.cache_key        ,
                                                 file_id         = cls.file_id          ,
                                                 entry           = entry                )
        return response.cache_id

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__create_test_entity(self):
        with self.cache_client as _:
            cache_id               = self.cache_id
            cache_key              = self.cache_key
            file_id                = self.file_id
            namespace              = self.namespace
            entry_data             = _.entry__retrieve       (cache_id = cache_id, namespace = namespace)
            cache__entry           = _.cache__entry          (cache_id = cache_id, namespace = namespace)
            cache__entry__refs     = _.cache__entry__refs    (cache_id = cache_id, namespace = namespace)
            cache__entry__metadata = _.cache__entry__metadata(cache_id = cache_id, namespace = namespace)
            file__folder           = f'{namespace}/data/key-based/{cache_key}'
            cache_hash             = _.hash_generator.from_string(cache_key)
            content_str            = json_dumps(entry_data,indent=2)            #  '{\n  "cache_key": "test/entity"\n}'
            content_bytes          = content_str.encode()                       #  b'{\n  "cache_key": "test/entity"\n}'
            content_hash           = safe_str_hash  (content_bytes)             # '8cdcee46a5'
            cache_id__shared       = f"{cache_id[0:2]}/{cache_id[2:4]}/{cache_id}"
            cache_hash__shared     = f"{cache_hash[0:2]}/{cache_hash[2:4]}/{cache_hash}"

            assert entry_data       == {'cache_key': 'test/entity'}
            assert content_str      == '{\n  "cache_key": "test/entity"\n}'
            assert content_bytes    == b'{\n  "cache_key": "test/entity"\n}'


            assert cache_key == 'test/entity' == Safe_Str__Cache__File__Cache_Key('test/entity')
            assert type(_)                is Html_Cache__Client
            assert type(_.cache_client)   is Cache__Service__Client
            assert is_guid(self.cache_id) is True
            assert entry_data             == {'cache_key': 'test/entity'}
            assert namespace              == 'test-html-to-cache'
            assert file_id                == 'root'
            assert cache_key              == 'test/entity'
            assert cache_hash             == '3fe62295e631cace'
            assert content_hash           == '8cdcee46a5'
            assert file__folder           == 'test-html-to-cache/data/key-based/test/entity'
            assert cache__entry.obj()           == __(data      = __(cache_key        = cache_key ),
                                                      metadata  = __(cache_id         = cache_id   ,
                                                                     cache_hash       = cache_hash ,
                                                                     cache_key        = cache_key  ,
                                                                     file_id          = file_id    ,
                                                                     namespace        = namespace  ,
                                                                     strategy         = 'key_based',
                                                                     stored_at        = __SKIP__   ,
                                                                     file_type        = 'json'     ,
                                                                     content_encoding = None       ,
                                                                     content_size     = 0          ),
                                                      data_type = 'json')
            assert cache__entry__refs.obj()     == __(all_paths=__(data     =[ f'{file__folder}/{file_id}.json',
                                                                               f'{file__folder}/{file_id}.json.config',
                                                                               f'{file__folder}/{file_id}.json.metadata'],
                                                                   by_hash  = [f'{namespace}/refs/by-hash/{cache_hash__shared}.json'],
                                                                   by_id    = [f'{namespace}/refs/by-id/{cache_id__shared}.json']),
                                                      cache_id   = cache_id     ,
                                                      cache_hash = cache_hash   ,
                                                      file_paths = __(content_files = [f'{file__folder}/{file_id}.json'],
                                                                      data_folders  = [f'{file__folder}/{file_id}/data']),
                                                      file_type  = 'json'       ,
                                                      namespace  = namespace    ,
                                                      strategy   = 'key_based'  ,
                                                      timestamp  = __SKIP__     )
            assert cache__entry__metadata.obj() == __(content__hash          = content_hash,
                                                      chain_hash            = None,
                                                      previous_version_path = None,
                                                      content__size         = 32,
                                                      tags                  = [],
                                                      timestamp             = __SKIP__,
                                                      data                  = __(cache_hash       = cache_hash  ,
                                                                                 cache_key        = cache_key   ,
                                                                                 cache_id         = cache_id    ,
                                                                                 content_encoding = None        ,
                                                                                 file_id          = file_id     ,
                                                                                 file_type        = 'json'      ,
                                                                                 json_field_path  = 'cache_key',
                                                                                 namespace        = namespace   ,
                                                                                 stored_at        = __SKIP__    ,
                                                                                 strategy         ='key_based'))

            assert type(cache__entry               ) is Schema__Cache__Retrieve__Success
            assert type(cache__entry__refs         ) is Schema__Cache__File__Refs
            assert type(cache__entry__metadata     ) is Schema__Cache__File__Metadata
            assert type(cache__entry__metadata.data) is Schema__Cache__Store__Metadata

    def test__init__(self):                                                               # Test auto-initialization
        with FLeT__Html__To__Cache() as _:
            assert type(_)          is FLeT__Html__To__Cache
            assert base_types(_)    == [Html_FLeT__Base, Type_Safe, object]
            assert _.cache_client   is None
            assert _.cache_id       is None
            assert _.namespace      is None
            assert _.config         is None

    def test__init____with_dependencies(self):                                            # Test with dependencies provided
        with FLeT__Html__To__Cache(cache_client = self.cache_client,
                                   cache_id     = self.cache_id    ,
                                   namespace    = self.namespace   ) as _:
            assert _.cache_client is self.cache_client
            assert _.cache_id     == self.cache_id
            assert _.namespace    == self.namespace

    # ═══════════════════════════════════════════════════════════════════════════
    # Setup Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_setup(self):                                                                 # Test setup initializes config
        with FLeT__Html__To__Cache() as _:
            result = _.setup()

            assert result        is _
            assert _.config      is not None
            assert _.config.name == 'html-to-cache'
            assert 'cache'       in _.config.description.lower()

    def test_setup__returns_self(self):                                                   # Test setup returns self for chaining
        flet = FLeT__Html__To__Cache().setup()

        assert type(flet)       is FLeT__Html__To__Cache
        assert flet.config.name == 'html-to-cache'

    # ═══════════════════════════════════════════════════════════════════════════
    # Execute Without Dependencies Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_execute__without_dependencies(self):                                         # Test execute without cache returns False
        flet       = FLeT__Html__To__Cache().setup()
        input_data = Schema__Html_To_Cache__Input(html = Safe_Str__Html(self.sample_html))

        result = flet.execute(input_data)

        assert type(result)      is Schema__FLeT__Execution__Result
        assert result.success    is True
        assert result.obj()      == __(success=True,
                                       duration=0.0,
                                       flow_output=__(store_response=None,
                                                      success=False,                # todo: review this use case where success=False here
                                                      data_key='html',
                                                      data_file_id='raw',
                                                      char_count=45),
                                       message='Flow executed ok')
        #assert result.char_count == len(self.sample_html)

    # ═══════════════════════════════════════════════════════════════════════════
    # Execute With Dependencies Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_execute__with_dependencies(self):                                            # Test execute with cache succeeds
        cache_id     = self.cache_id
        namespace    = self.namespace
        file_id      = self.file_id
        cache_key    = self.cache_key
        data_key     = DEFAULT__HTML_TO_CACHE__DATA_KEY     #'html'
        data_file_id = DEFAULT__HTML_TO_CACHE__DATA_FILE_ID #'raw'
        flet         = FLeT__Html__To__Cache(cache_client = self.cache_client,
                                             cache_id     = cache_id         ,
                                             namespace    = namespace        ).setup()
        input_data   = Schema__Html_To_Cache__Input(html = Safe_Str__Html(self.sample_html))
        result       = flet.execute(input_data)
        flow_output  = result.flow_output
        data_file_created = flow_output.store_response.data_files_created[0]

        assert result.success      is True
        assert type(flet.flow)     is Html_FLeT__Flow
        assert type(result)        is Schema__FLeT__Execution__Result
        assert type(flow_output)   is Schema__Html_To_Cache__Output
        assert data_file_created   == 'test-html-to-cache/data/key-based/test/entity/root/data/html/raw.txt'
        assert data_file_created   == f'{namespace}/data/key-based/{cache_key}/{file_id}/data/{data_key}/{data_file_id}.txt'
        assert result.obj()        == __(success=True,
                                         duration=0.0,
                                         flow_output=__(success      = True ,
                                                        data_key     = 'html',
                                                        data_file_id = 'raw' ,
                                                        char_count   = 45    ,
                                                        store_response=__(cache_id           = self.cache_id,
                                                                          data_files_created = [data_file_created],
                                                                          data_key           = 'html'          ,
                                                                          data_type          = 'string'        ,
                                                                          extension          = 'txt'           ,
                                                                          file_id            = 'raw'           ,
                                                                          file_size          = 45              ,
                                                                          namespace          = self.namespace  ,
                                                                          timestamp          = __SKIP__        )),
                                        message='Flow executed ok')

        flow_id = flet.flow.flow_id

        with flet.flow_data() as _:
            assert type(_)          is Cache__Entity__Json_File
            assert _.exists()       is True
            assert obj(_.retrieve()) == __(flow_data = __(flow_id      = flow_id                     ,
                                                          flow_name    = 'run_actions'               ,
                                                          start_time   = __SKIP__                    ,
                                                          end_time     = __SKIP__                    ,
                                                          status       = 'completed'                 ,
                                                          error        = None                        ,
                                                          tasks        = __SKIP__                    ,
                                                          events       = []                          ,
                                                          results      = [__(key         = 'flow-return-value' ,
                                                                             description = __SKIP__             ,
                                                                             timestamp   = __SKIP__             )],
                                                          artifacts    = []                          ,
                                                          logs         = [__(timestamp = __SKIP__, level = 10, message = __SKIP__, task_id = None   ),
                                                                          __(timestamp = __SKIP__, level = 10, message = __SKIP__, task_id = None   ),
                                                                          __(timestamp = __SKIP__, level = 10, message = __SKIP__, task_id = __SKIP__),
                                                                          __(timestamp = __SKIP__, level = 10, message = __SKIP__, task_id = __SKIP__),
                                                                          __(timestamp = __SKIP__, level = 10, message = __SKIP__, task_id = None   )],
                                                          return_value = __(store_response = __(cache_id            = self.cache_id                    ,
                                                                                                data_files_created  = ['test-html-to-cache/data/key-based/test/entity/root/data/html/raw.txt'],
                                                                                                data_key            = 'html'                          ,
                                                                                                data_type           = 'string'                        ,
                                                                                                extension           = 'txt'                           ,
                                                                                                file_id             = 'raw'                           ,
                                                                                                file_size           = 45                              ,
                                                                                                namespace           = 'test-html-to-cache'           ,
                                                                                                timestamp           = __SKIP__                        ),
                                                                            success       = True                     ,
                                                                            data_key      = 'html'                   ,
                                                                            data_file_id  = 'raw'                    ,
                                                                            char_count    = 45                       )),
                                         flow_events = [])


        with flet.cache_entity() as _:
            assert type(_)  is Cache__Entity
            assert _.data__files__paths().contains([ 'test-html-to-cache/data/key-based/test/entity/root/data/html/raw.txt'                       ,
                                                     'test-html-to-cache/data/key-based/test/entity/root/data/flows/html-to-cache/flow-data.json']) is True





    def test_execute__with_custom_data_key(self):                                         # Test execute with custom data_key
        flet = FLeT__Html__To__Cache(cache_client = self.cache_client,
                                     cache_id     = self.cache_id    ,
                                     namespace    = self.namespace   ).setup()

        input_data = Schema__Html_To_Cache__Input(html         = Safe_Str__Html('<p>custom</p>'),
                                                  data_key     = 'html/processed'              ,
                                                  data_file_id = 'cleaned'                     )

        result = flet.execute(input_data)

        assert result.success      is True
        assert result.obj()        == __(success=True,
                                         duration=0.0,
                                         flow_output=__(success=True,
                                                        data_key='html/processed',
                                                        data_file_id='cleaned',
                                                        char_count=13,
                                                        store_response=__(cache_id=self.cache_id,
                                                                          data_files_created=['test-html-to-cache/data/key-based/test/entity/root/data/html/processed/cleaned.txt'],
                                                                          data_key='html/processed',
                                                                          data_type='string',
                                                                          extension='txt',
                                                                          file_id='cleaned',
                                                                          file_size=13,
                                                                          namespace='test-html-to-cache',
                                                                          timestamp=__SKIP__)),
                                         message='Flow executed ok')
