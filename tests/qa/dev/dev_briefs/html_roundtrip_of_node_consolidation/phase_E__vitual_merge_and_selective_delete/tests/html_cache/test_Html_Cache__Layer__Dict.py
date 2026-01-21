# ═══════════════════════════════════════════════════════════════════════════════
# Test: Html_Cache__Layer__Dict (L2)
# Tests the parsed HTML dict caching layer
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                           import TestCase

import pytest
from memory_fs.schemas.Schema__Memory_FS__File__Config                                  import Schema__Memory_FS__File__Config
from memory_fs.schemas.Schema__Memory_FS__File__Metadata                                import Schema__Memory_FS__File__Metadata
from mgraph_ai_service_cache_client.schemas.cache.file.Schema__Cache__File__Refs        import Schema__Cache__File__Refs
from mgraph_ai_service_cache_client.schemas.cache.store.Schema__Cache__Hash__Reference  import Schema__Cache__Hash__Reference
from osbot_utils.testing.Graph__Deterministic__Ids                                      import graph_deterministic_ids
from osbot_utils.testing.__                                                             import __, __SKIP__
from osbot_utils.testing.__helpers                                                      import obj
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                      import Cache_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id                       import Safe_Id
from osbot_utils.type_safe.type_safe_core.config.type_safe_fast_create                  import type_safe_fast_create
from osbot_utils.utils.Objects                                                          import base_classes
from phase_e.html_cache.Html_Cache__Layer__Base                                         import Html_Cache__Layer__Base
from phase_e.html_cache.Html_Cache__Layer__Html__Dict                                   import Html_Cache__Layer__Html__Dict
from phase_e.html_cache.Html_Cache__Manager                                             import Html_Cache__Manager
from phase_e.storage.backends.Perf__Storage__Cache_Service                              import Perf__Storage__Cache_Service, DEFAULT__PERF_STORAGE__FILE_ID__PERF_ENTRY
from phase_e.storage.base.Perf__Storage__Base                                           import Perf__Storage__Base
from phase_e.storage.cache_service.Cache_Service__Client                                import Cache_Service__Client
from phase_e.storage.enums.Enum__Storage_Mode                                           import Enum__Storage_Mode
from phase_e.storage.schemas.Schema__Perf__Entry                                        import Schema__Perf__Entry
from phase_e.storage.schemas.Schema__Perf__Storage__Config                              import Schema__Perf__Storage__Config
from tests.Phase_E__Fast_API__Test_Objs                                                 import client_cache_service

class Schema__Perf__Test_Data(Type_Safe):
    cache_id = None

class test_Html_Cache__Layer__Dict(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.session_name    = 'test-html-cache'
        cls.target_name     = 'layer-base'
        cls.storage         = cls.create_storage(session_name=cls.session_name,
                                                 target_name=cls.target_name)
        cls.cache_manager   = Html_Cache__Manager           (storage      = cls.storage                                             )
        cls.layer           = Html_Cache__Layer__Html__Dict (storage      = cls.cache_manager.storage, stats=cls.cache_manager.stats)
        cls.stats           = cls.cache_manager.stats
        cls.test_data       = cls.create__perf_test_data()


    @classmethod
    def create_storage(cls, session_name, target_name):
        cls.cache_namespace = 'pytest'
        cls.config          = Schema__Perf__Storage__Config(storage_mode    = Enum__Storage_Mode.CACHE_SERVICE,
                                                            cache_namespace = cls.cache_namespace             )

        cls.cache_client, cls.cache_service = client_cache_service()                                                    # In-memory cache service
        cls.cache_client_wrapper            = Cache_Service__Client(cache_client=cls.cache_client)

        storage                             = Perf__Storage__Cache_Service(config       = cls.config              ,
                                                                           client       = cls.cache_client_wrapper,
                                                                           session_name = session_name            ,
                                                                           target_name  = target_name             )
        return storage

    @classmethod
    def create__perf_test_data(cls):
        cls.cache_id = cls.storage.create_file__perf_entry()
        perf_test_data =  Schema__Perf__Test_Data(cache_id = cls.cache_id)
        return perf_test_data

    @pytest.fixture(autouse=True)
    def _inject_pytest_request(self, request):
        self._pytest_request = request

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                     # Test L2 layer initialization
        with Html_Cache__Layer__Html__Dict() as _:
            assert type(_) is Html_Cache__Layer__Html__Dict
            assert base_classes(_) == [Html_Cache__Layer__Base, Type_Safe, object]
            assert type(_.storage) is Perf__Storage__Base
            assert _.layer_name    == 'L2'                      # Fixed layer name


    def test__init____with_manager(self):                       # Test initialization with manager
        with self.layer as _:
            assert _.storage    is self.storage
            assert _.layer_name == 'L2'

    # ═══════════════════════════════════════════════════════════════════════════
    # Key Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_key_data(self):                                    # L2 uses dict.json
        assert self.layer.key_data() == 'L2/html-dict'

    # ═══════════════════════════════════════════════════════════════════════════
    # Save Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_save(self):                                        # Test basic save
        all_items = self._pytest_request.session.items
        if len(all_items) > 1:
            pytest.skip("This test doesn't work when executed with multiple tests")
        with self.layer as _:
            cache_id            = _.cache_id()
            key_data            = _.key_data()                             # todo: review this name, since key_data is not very clear
            cache_hash          = _.cache_hash()
            cache_key           = _.cache_key()
            cache_key__safe_id  = Safe_Id(cache_key)
            data_folder         = _.data_folder()
            data_file           = _.data_file()
            file_folder         = _.file_folder()
            session_name        = self.storage.session_name
            target_name         = self.storage.target_name
            file_id             = DEFAULT__PERF_STORAGE__FILE_ID__PERF_ENTRY
            cache_id__sharded   = f"{cache_id[0:2]}/{cache_id[2:4]}/{cache_id}"
            cache_hash__sharded = f"{cache_hash[0:2]}/{cache_hash[2:4]}/{cache_hash}"

            result              = _.save(cache_id, DICT_SAMPLE)                                 # create the file

            assert _.exists()                is True                                                  # confirm it exists
            assert _.load(cache_id=cache_id) == DICT_SAMPLE                                           # confirm load returns the data saved

            assert cache_id                  == self.test_data.cache_id
            assert cache_hash                == 'b9fc56d4592ecb45'
            assert cache_hash__sharded       == 'b9/fc/b9fc56d4592ecb45'
            assert cache_key                 == 'sessions/test-html-cache/targets/layer-base'
            assert cache_key                 == f'sessions/{session_name}/targets/{target_name}'
            assert cache_key__safe_id        == 'sessions_test-html-cache_targets_layer-base'
            assert data_folder               == f'{self.cache_namespace}/data/key-based/{cache_key}/{file_id}/data'
            assert data_file                 == f'{data_folder}/{key_data}.json'
            assert file_folder               == f'{self.cache_namespace}/data/key-based/sessions/{session_name}/targets/{target_name}'
            assert key_data                  == 'L2/html-dict'
            assert result                    is True




            assert 'pytest'                            in _.storage.namespaces__list()
            assert _.storage.namespace__cache_hashes() == ['b9fc56d4592ecb45']


            assert _.storage.namespace__all_files() == [  'pytest/data/key-based/sessions/test-html-cache/targets/layer-base/perf-entry.json',
                                                          'pytest/data/key-based/sessions/test-html-cache/targets/layer-base/perf-entry.json.config',
                                                          'pytest/data/key-based/sessions/test-html-cache/targets/layer-base/perf-entry.json.metadata',
                                                          'pytest/data/key-based/sessions/test-html-cache/targets/layer-base/perf-entry/data/L2/html-dict.json',
                                                          'pytest/refs/by-hash/b9/fc/b9fc56d4592ecb45.json',
                                                          f'pytest/refs/by-id/{cache_id[0:2]}/{cache_id[2:4]}/{cache_id}.json']

            assert _.storage.namespace__all_files() == [ f'{file_folder}/{file_id}.json',
                                                         f'{file_folder}/{file_id}.json.config',
                                                         f'{file_folder}/{file_id}.json.metadata',
                                                         f'{data_file}',
                                                         f'{self.cache_namespace}/refs/by-hash/{cache_hash__sharded}.json',
                                                         f'pytest/refs/by-id/{cache_id__sharded}.json']

            file_id__file_contents =    _.storage.file__contents__json(cache_id)
            perf_entry             = Schema__Perf__Entry.from_json(file_id__file_contents)

            assert obj(file_id__file_contents)      == __(cache_key    = cache_key,
                                                          session_name = session_name,
                                                          target_name  = target_name,
                                                          timestamp    = __SKIP__,
                                                          config       =__(),
                                                          summary      =__())

            assert perf_entry.json() == file_id__file_contents

            file_id__config__json   = _.storage.file__config  (cache_id   = cache_id)
            file_id__metadata__json = _.storage.file__metadata(cache_id   = cache_id)
            file_id__hash__json     = _.storage.file__hash    (cache_hash = cache_hash)

            file_id__refs           = _.storage.file__refs    (cache_id   = cache_id)
            assert type(file_id__config__json  ) is dict
            assert type(file_id__metadata__json) is dict
            assert type(file_id__hash__json    ) is dict
            assert type(file_id__refs          ) is not dict # is it already Schema__Cache__File__Refs

            file_id__config   = Schema__Memory_FS__File__Config  .from_json(file_id__config__json  )
            file_id__metadata = Schema__Memory_FS__File__Metadata.from_json(file_id__metadata__json)
            file_id__hash     = Schema__Cache__Hash__Reference   .from_json(file_id__hash__json)

            assert file_id__config  .json() == file_id__config__json                # confirm roundtrip
            assert file_id__metadata.json() == file_id__metadata__json              # and the native schemas of the responses
            assert file_id__hash    .json() == file_id__hash__json

            assert type(file_id__config  ) is Schema__Memory_FS__File__Config
            assert type(file_id__metadata) is Schema__Memory_FS__File__Metadata
            assert type(file_id__refs    ) is Schema__Cache__File__Refs
            assert type(file_id__hash    ) is Schema__Cache__Hash__Reference

            assert perf_entry.obj()      == obj(file_id__file_contents)

            assert file_id__config.obj() == __(file_id         = file_id,
                                               exists_strategy = 'first',
                                               file_key        = cache_key,
                                               file_paths      =[f'{self.cache_namespace}/data/key-based/{cache_key}'],
                                               file_type       =__(name           = 'json',
                                                                   content_type   = 'application/json; charset=utf-8',
                                                                   file_extension = 'json',
                                                                   encoding       = 'utf-8',
                                                                   serialization  = 'json'))


            assert file_id__metadata.obj() == __(content__hash         = __SKIP__,
                                                 chain_hash            = None,
                                                 previous_version_path = None,
                                                 content__size         = 195,
                                                 tags                  = [],
                                                 timestamp             =__SKIP__,
                                                 data                  =__(cache_hash       = cache_hash                 ,
                                                                           cache_key        = cache_key__safe_id         ,
                                                                           cache_id         = cache_id                   ,
                                                                           content_encoding = None                       ,
                                                                           file_id          = file_id                    ,
                                                                           file_type        = 'json'                     ,
                                                                           json_field_path  = 'cache_key'                ,
                                                                           namespace        = self.config.cache_namespace,
                                                                           stored_at        =__SKIP__                    ,
                                                                           strategy         = 'key_based')               )

            assert file_id__refs.obj() == __(all_paths      =__(data    = [f'{self.cache_namespace}/data/key-based/{cache_key}/{file_id}.json',
                                                                           f'{self.cache_namespace}/data/key-based/{cache_key}/{file_id}.json.config',
                                                                           f'{self.cache_namespace}/data/key-based/{cache_key}/{file_id}.json.metadata'],
                                                                by_hash = [f'{self.cache_namespace}/refs/by-hash/{cache_hash__sharded}.json'],
                                                                by_id   = [f'{self.cache_namespace}/refs/by-id/{cache_id__sharded}.json']),
                                               cache_id     = cache_id ,
                                               cache_hash   = cache_hash,
                                               file_type    = 'json',
                                               namespace    = 'pytest',
                                               file_paths   =   __( content_files = [f'{self.cache_namespace}/data/key-based/{cache_key}/{file_id}.json'],
                                                                    data_folders  = [f'{self.cache_namespace}/data/key-based/{cache_key}/{file_id}/data']),
                                               strategy     = 'key_based',
                                               timestamp    = __SKIP__)

            assert file_id__hash.obj() == __(cache_hash     = cache_hash    ,
                                             cache_ids      = [__(cache_id=cache_id,
                                                                  timestamp=__SKIP__)],
                                             latest_id      = cache_id,
                                             total_versions = 1)

            assert _.delete(cache_id=self.cache_id)  is True
            assert _.delete(cache_id=self.cache_id)  is False
            assert _.exists()                        is False
            assert _.load(cache_id = self.cache_id)  is None

    def test_save__empty_dict(self):                            # Test empty dict saves
        with self.layer as _:
            _.delete(cache_id=self.cache_id)
            result = _.save(cache_id  = self.cache_id,
                            html_dict = {})                # this will not save or create the file
            assert result                           is True
            assert _.load(cache_id=self.cache_id)   is None
            assert _.exists()                       is False

    def test_save__nested_structure(self):                      # Test deeply nested dict
        nested = {
            'level1': {
                'level2': {
                    'level3': {
                        'value': 'deep'
                    }
                }
            }
        }
        with self.layer as _:
            save_result = _.save(cache_id  = self.cache_id,
                            html_dict = nested)
            load_result = _.load(cache_id = self.cache_id)

            assert _.exists()                        is True
            assert save_result                       is True
            assert load_result                       == nested
            assert _.delete(cache_id=self.cache_id)  is True
            assert _.delete(cache_id=self.cache_id)  is False
            assert _.exists()                        is False
            assert _.load(cache_id = self.cache_id)  is None


    # ═══════════════════════════════════════════════════════════════════════════
    # Load Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_load(self):                                        # Test basic load
        assert self.layer.save(cache_id  = self.cache_id,
                               html_dict = DICT_SAMPLE  ) is True
        assert self.layer.load(cache_id=self.cache_id   ) == DICT_SAMPLE

    def test_load__not_found(self):                             # Returns None when not found
        self.layer.delete(cache_id=self.cache_id)
        assert self.layer.load(cache_id=self.cache_id) is None


    def test_load__tracks_hit(self):                            # Load success increments hit counter
        self.layer.save(cache_id = self.cache_id, html_dict= DICT_SAMPLE)
        self.stats.l2_hits = 0                          # Reset

        self.layer.load(cache_id=self.cache_id)

        assert self.stats.l2_hits == 1

    def test_load__tracks_miss(self):                           # Load failure increments miss counter
        self.stats.l2_hits   = 0
        self.stats.l2_misses = 0                        # Reset

        self.layer.load(cache_id=Cache_Id())

        assert self.stats.l2_hits   == 0
        assert self.stats.l2_misses == 1

    # ═══════════════════════════════════════════════════════════════════════════
    # Build from HTML Tests
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test_build_from_html(self):                             # Test parsing HTML to dict
        html_dict = self.layer.build_from_html(HTML_SIMPLE)

        assert html_dict is not None
        assert isinstance(html_dict, dict)

    @type_safe_fast_create
    def test_build_from_html__tracks_builds(self):              # Build increments counter
        self.stats.l2_builds = 0                        # Reset

        self.layer.build_from_html(HTML_SIMPLE)

        assert self.stats.l2_builds == 1

    @type_safe_fast_create
    def test_build_from_html__has_structure(self):              # Built dict has expected structure
        with graph_deterministic_ids():
            html_dict = self.layer.build_from_html(HTML_SIMPLE)

            assert obj(html_dict) == __(tag='html',
                                        attrs=__(),
                                        nodes=[__(tag='head',
                                                  attrs=__(),
                                                  nodes=[__(tag='title',
                                                            attrs=__(),
                                                            nodes=[__(type='TEXT', data='Test', node_id='f0000004')],
                                                            node_id='f0000003')],
                                                  node_id='f0000002'),
                                               __(tag='body',
                                                  attrs=__(),
                                                  nodes=[__(tag='h1',
                                                            attrs=__(),
                                                            nodes=[__(type='TEXT',
                                                                      data='Hello',
                                                                      node_id='f0000007')],
                                                            node_id='f0000006'),
                                                         __(tag='p',
                                                            attrs=__(),
                                                            nodes=[__(type='TEXT',
                                                                      data='World',
                                                                      node_id='f0000009')],
                                                            node_id='f0000008')],
                                                  node_id='f0000005')],
                                        node_id='f0000001')


    @type_safe_fast_create
    def test_build_from_html__nested(self):                     # Nested HTML parses correctly
        html_dict = self.layer.build_from_html(HTML_NESTED)

        assert html_dict is not None
        assert isinstance(html_dict, dict)

    @type_safe_fast_create
    def test_build_from_html__invalid_html(self):               # Invalid HTML handled gracefully
        html_dict = self.layer.build_from_html('<not valid html')

        assert html_dict is None

    # ═══════════════════════════════════════════════════════════════════════════
    # Overwrite Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_save__overwrite(self):                             # Overwriting dict works
        self.layer.save(cache_id=self.cache_id, html_dict={'version': 1})
        self.layer.save(cache_id=self.cache_id, html_dict={'version': 2})

        assert self.layer.load(cache_id=self.cache_id) == {'version': 2}


    # ═══════════════════════════════════════════════════════════════════════════
    # Delete Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_delete(self):                                      # Delete removes dict and metadata
        assert self.layer.save(cache_id=self.cache_id, html_dict = DICT_SAMPLE) is True
        assert self.layer.exists()                                              is True
        assert self.layer.delete(cache_id=self.cache_id)                        is True
        assert self.layer.exists()                                              is False
        assert self.layer.load  (cache_id=self.cache_id)                        is None


# ═══════════════════════════════════════════════════════════════════════════════
# Test Data
# ═══════════════════════════════════════════════════════════════════════════════

HTML_SIMPLE = '''<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><h1>Hello</h1><p>World</p></body>
</html>'''

HTML_NESTED = '''<!DOCTYPE html>
<html>
<head><title>Nested</title></head>
<body>
<div>
    <p>Para 1</p>
    <p>Para 2</p>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
    </ul>
</div>
</body>
</html>'''

DICT_SAMPLE = {                                                 # Pre-built dict for save/load tests
    'head': {'nodes': [{'tag': 'title', 'text': 'Test'}]},
    'body': {'nodes': [
        {'tag': 'h1', 'text': 'Hello'},
        {'tag': 'p', 'text': 'World'}
    ]}
}