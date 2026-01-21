# ═══════════════════════════════════════════════════════════════════════════════
# test_FLeT__Html__From__Cache - Tests for HTML from cache FLeT
# Tests retrieving HTML from cache data layer
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                                                   import TestCase
from mgraph_ai_service_cache_client.client.client_entities.Cache__Entity                                                        import Cache__Entity
from mgraph_ai_service_cache_client.client.client_entities.Cache__Entity__Json_File                                             import Cache__Entity__Json_File
from mgraph_ai_service_html_graph.service.cache_storage.schemas.Schema__Html_Cache__Entry                                       import Schema__Html_Cache__Entry
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.base.Html_FLeT__Base                                               import Html_FLeT__Base
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.base.Html_FLeT__Flow                                               import Html_FLeT__Flow
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.Schema__FLeT__Execution__Result                            import Schema__FLeT__Execution__Result
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.FLeT__Html__From__Cache                    import FLeT__Html__From__Cache
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.schemas.Schema__Html_From_Cache__Input     import Schema__Html_From_Cache__Input
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.schemas.Schema__Html_From_Cache__Output    import Schema__Html_From_Cache__Output
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.FLeT__Html__To__Cache                        import FLeT__Html__To__Cache
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Input         import Schema__Html_To_Cache__Input
from osbot_utils.testing.__                                                                                                     import __, __SKIP__
from osbot_utils.testing.__helpers                                                                                              import obj
from osbot_utils.type_safe.Type_Safe                                                                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                                                       import Safe_Str__Html
from osbot_utils.utils.Objects                                                                                                  import base_types
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                                                        import create_html_cache_client

DEFAULT__HTML_FROM_CACHE__DATA_KEY     = 'html'
DEFAULT__HTML_FROM_CACHE__DATA_FILE_ID = 'raw'


class test_FLeT__Html__From__Cache(TestCase):

    @classmethod
    def setUpClass(cls):                                                                  # Shared test objects
        cls.cache_client, cls.cache_service = create_html_cache_client()
        cls.namespace    = 'test-html-from-cache'
        cls.cache_key    = 'test/entity'
        cls.file_id      = 'root'
        cls.sample_html  = '<html><body><p>Cached content for retrieval</p></body></html>'
        cls.cache_id     = cls.create_and_populate_entity()

    @classmethod
    def create_and_populate_entity(cls):                                                  # Create entity and store HTML
        entry    = Schema__Html_Cache__Entry()
        response = cls.cache_client.entry__store(namespace = cls.namespace ,
                                                 cache_key = cls.cache_key ,
                                                 file_id   = cls.file_id   ,
                                                 entry     = entry         )
        cache_id = response.cache_id if response else None

        # Store HTML using FLeT__Html__To__Cache
        flet = FLeT__Html__To__Cache(cache_client = cls.cache_client,
                                     cache_id     = cache_id        ,
                                     namespace    = cls.namespace   ).setup()
        flet.execute(Schema__Html_To_Cache__Input(html = Safe_Str__Html(cls.sample_html)))

        return cache_id

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                               # Test auto-initialization
        with FLeT__Html__From__Cache() as _:
            assert type(_)        is FLeT__Html__From__Cache
            assert base_types(_)  == [Html_FLeT__Base, Type_Safe, object]
            assert _.cache_client is None
            assert _.config       is None
            assert _.cache_id     is None
            assert _.namespace    is None

    def test__init____with_cache_client(self):                                            # Test with cache_client
        with FLeT__Html__From__Cache(cache_client = self.cache_client,
                                     cache_id     = self.cache_id    ,
                                     namespace    = self.namespace   ) as _:
            assert _.cache_client is self.cache_client
            assert _.cache_id     == self.cache_id
            assert _.namespace    == self.namespace

    # ═══════════════════════════════════════════════════════════════════════════
    # Setup Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_setup(self):                                                                 # Test setup configuration
        with FLeT__Html__From__Cache() as _:
            result = _.setup()

            assert result        is _
            assert _.config      is not None
            assert _.config.name == 'html-from-cache'
            assert 'cache'       in _.config.description.lower()

    # ═══════════════════════════════════════════════════════════════════════════
    # Execute Tests (without dependencies)
    # ═══════════════════════════════════════════════════════════════════════════

    def test_execute__without_cache_client(self):                                         # Test without cache_client
        flet       = FLeT__Html__From__Cache().setup()
        input_data = Schema__Html_From_Cache__Input()

        result = flet.execute(input_data)

        assert type(result)                is Schema__FLeT__Execution__Result
        assert result.success              is True
        assert result.flow_output.success  is False
        assert result.flow_output.found    is False

    def test_execute__without_cache_id(self):                                             # Test without cache_id
        flet       = FLeT__Html__From__Cache(cache_client = self.cache_client,
                                             namespace    = self.namespace   ).setup()
        input_data = Schema__Html_From_Cache__Input()

        result = flet.execute(input_data)

        assert result.success              is True
        assert result.flow_output.success  is False
        assert result.flow_output.found    is False

    # ═══════════════════════════════════════════════════════════════════════════
    # Execute Tests (with dependencies)
    # ═══════════════════════════════════════════════════════════════════════════

    def test_execute__with_dependencies(self):                                            # Test execute with cache succeeds
        cache_id     = self.cache_id
        namespace    = self.namespace
        file_id      = self.file_id
        cache_key    = self.cache_key
        data_key     = DEFAULT__HTML_FROM_CACHE__DATA_KEY
        data_file_id = DEFAULT__HTML_FROM_CACHE__DATA_FILE_ID
        flet         = FLeT__Html__From__Cache(cache_client = self.cache_client,
                                               cache_id     = cache_id         ,
                                               namespace    = namespace        ).setup()
        input_data   = Schema__Html_From_Cache__Input()
        result       = flet.execute(input_data)
        flow_output  = result.flow_output

        assert result.success           is True
        assert type(flet.flow)          is Html_FLeT__Flow
        assert type(result)             is Schema__FLeT__Execution__Result
        assert type(flow_output)        is Schema__Html_From_Cache__Output
        assert flow_output.success      is True
        assert flow_output.found        is True
        assert str(flow_output.html)    == self.sample_html
        assert result.obj()             == __(success     = True                ,
                                              duration    = 0.0                 ,
                                              flow_output = __(success = True             ,
                                                               html    = self.sample_html ,
                                                               found   = True             ),
                                              message     = 'Flow executed ok'  )

        # Verify flow data was stored
        with flet.flow_data() as _:
            assert type(_)    is Cache__Entity__Json_File
            assert _.exists() is True
            flow_json = _.retrieve()
            assert flow_json['flow_data']['status'] == 'completed'

        # Verify cache entity data files
        with flet.cache_entity() as _:
            assert type(_) is Cache__Entity
            files = _.data__files__paths()
            assert f'{namespace}/data/key-based/{cache_key}/{file_id}/data/{data_key}/{data_file_id}.txt' in files

    def test_execute__data_not_found(self):                                               # Test with nonexistent data_key
        flet       = FLeT__Html__From__Cache(cache_client = self.cache_client,
                                             cache_id     = self.cache_id    ,
                                             namespace    = self.namespace   ).setup()
        input_data = Schema__Html_From_Cache__Input(data_key = 'nonexistent')

        result = flet.execute(input_data)

        assert result.success              is True                                        # FLeT execution succeeded
        assert result.flow_output.success  is True                                        # Action succeeded
        assert result.flow_output.found    is False                                       # But data not found
        assert str(result.flow_output.html) == ''

    def test_execute__with_custom_data_key(self):                                         # Test with custom data_key
        # First store at custom location
        store_flet = FLeT__Html__To__Cache(cache_client = self.cache_client,
                                           cache_id     = self.cache_id    ,
                                           namespace    = self.namespace   ).setup()
        store_flet.execute(Schema__Html_To_Cache__Input(html         = Safe_Str__Html('<p>custom path</p>'),
                                                        data_key     = 'custom/path'                      ,
                                                        data_file_id = 'custom-file'                      ))

        # Then load from custom location
        load_flet  = FLeT__Html__From__Cache(cache_client = self.cache_client,
                                             cache_id     = self.cache_id    ,
                                             namespace    = self.namespace   ).setup()
        input_data = Schema__Html_From_Cache__Input(data_key     = 'custom/path' ,
                                                    data_file_id = 'custom-file' )

        result = load_flet.execute(input_data)

        assert result.success              is True
        assert result.flow_output.found    is True
        assert str(result.flow_output.html) == '<p>custom path</p>'

    # ═══════════════════════════════════════════════════════════════════════════
    # Observability Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_observability__flow_data_stored(self):                                       # Test flow data is stored
        flet       = FLeT__Html__From__Cache(cache_client = self.cache_client,
                                             cache_id     = self.cache_id    ,
                                             namespace    = self.namespace   ).setup()
        input_data = Schema__Html_From_Cache__Input()

        flet.execute(input_data)

        with flet.flow_data() as _:
            assert _.exists() is True
            flow_json = _.retrieve()
            assert obj(flow_json) == __(flow_data   = __(flow_id      = __SKIP__      ,
                                                         flow_name    = 'run_actions' ,
                                                         start_time   = __SKIP__      ,
                                                         end_time     = __SKIP__      ,
                                                         status       = 'completed'   ,
                                                         error        = None          ,
                                                         tasks        = __SKIP__      ,
                                                         events       = []            ,
                                                         results      = __SKIP__      ,
                                                         artifacts    = []            ,
                                                         logs         = __SKIP__      ,
                                                         return_value = __(success = True             ,
                                                                           html    = self.sample_html ,
                                                                           found   = True             )),
                                        flow_events = []                              )

    def test_observability__durations(self):                                              # Test duration tracking
        flet       = FLeT__Html__From__Cache(cache_client = self.cache_client,
                                             cache_id     = self.cache_id    ,
                                             namespace    = self.namespace   ).setup()
        input_data = Schema__Html_From_Cache__Input()

        flet.execute(input_data)

        assert flet.flow       is not None
        assert flet.flow_output is not None
        assert type(flet.durations()) is dict

    # ═══════════════════════════════════════════════════════════════════════════
    # Round-Trip Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_round_trip__store_and_retrieve(self):                                        # Test store then retrieve
        unique_html = '<div>Round trip test unique content 12345</div>'

        # Create new entity
        entry    = Schema__Html_Cache__Entry()
        response = self.cache_client.entry__store(namespace = self.namespace      ,
                                                  cache_key = 'test/round-trip'   ,
                                                  file_id   = 'root'              ,
                                                  entry     = entry               )
        cache_id = response.cache_id

        # Store using FLeT__Html__To__Cache
        store_flet = FLeT__Html__To__Cache(cache_client = self.cache_client,
                                           cache_id     = cache_id         ,
                                           namespace    = self.namespace   ).setup()
        store_result = store_flet.execute(Schema__Html_To_Cache__Input(html = Safe_Str__Html(unique_html)))

        assert store_result.success is True

        # Retrieve using FLeT__Html__From__Cache
        load_flet = FLeT__Html__From__Cache(cache_client = self.cache_client,
                                            cache_id     = cache_id         ,
                                            namespace    = self.namespace   ).setup()
        load_result = load_flet.execute(Schema__Html_From_Cache__Input())

        assert load_result.success              is True
        assert load_result.flow_output.found    is True
        assert load_result.flow_output.html     == unique_html

    def test_round_trip__multiple_data_keys(self):                                        # Test multiple data keys in same entity
        # Create entity
        entry    = Schema__Html_Cache__Entry()
        response = self.cache_client.entry__store(namespace = self.namespace           ,
                                                  cache_key = 'test/multiple-keys'     ,
                                                  file_id   = 'root'                   ,
                                                  entry     = entry                    )
        cache_id = response.cache_id

        # Store at different data keys
        store_flet = FLeT__Html__To__Cache(cache_client = self.cache_client,
                                           cache_id     = cache_id         ,
                                           namespace    = self.namespace   ).setup()

        store_flet.execute(Schema__Html_To_Cache__Input(html         = Safe_Str__Html('<p>original</p>'),
                                                        data_key     = 'html'                          ,
                                                        data_file_id = 'raw'                           ))
        store_flet.execute(Schema__Html_To_Cache__Input(html         = Safe_Str__Html('<p>cleaned</p>') ,
                                                        data_key     = 'html'                          ,
                                                        data_file_id = 'clean'                         ))
        store_flet.execute(Schema__Html_To_Cache__Input(html         = Safe_Str__Html('<p>rendered</p>'),
                                                        data_key     = 'rendered'                      ,
                                                        data_file_id = 'output'                        ))

        # Load from each
        load_flet = FLeT__Html__From__Cache(cache_client = self.cache_client,
                                            cache_id     = cache_id         ,
                                            namespace    = self.namespace   ).setup()

        result_raw      = load_flet.execute(Schema__Html_From_Cache__Input(data_key='html', data_file_id='raw'))
        result_clean    = load_flet.execute(Schema__Html_From_Cache__Input(data_key='html', data_file_id='clean'))
        result_rendered = load_flet.execute(Schema__Html_From_Cache__Input(data_key='rendered', data_file_id='output'))

        assert str(result_raw.flow_output.html)      == '<p>original</p>'
        assert str(result_clean.flow_output.html)    == '<p>cleaned</p>'
        assert str(result_rendered.flow_output.html) == '<p>rendered</p>'