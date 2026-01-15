# ═══════════════════════════════════════════════════════════════════════════════
# test_Html_Cache__Document - Tests for cached document state manager
# Uses in-memory cache service via FastAPI test client
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                              import TestCase
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.safe_str.Safe_Str__LETS__Name import Safe_Str__LETS__Name
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Status  import Schema__LETS__Status
from osbot_utils.type_safe.Type_Safe                                                       import Type_Safe
from osbot_utils.utils.Objects                                                             import base_types
from osbot_utils.utils.Misc                                                                import is_guid
from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type             import Enum__Cache__Data_Type
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Document               import Html_Cache__Document
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Layer                  import Html_Cache__Layer
from mgraph_ai_service_html_graph.service.cache_storage.safe_str.Safe_Str__Layer_Name      import Safe_Str__Layer_Name
from mgraph_ai_service_html_graph.service.cache_storage.schemas.Schema__Html_Cache__Root   import Schema__Html_Cache__Root
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                   import create_html_cache_client


class test_Html_Cache__Document(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup - in-memory cache
        cls.html_cache_client, cls.cache_service = create_html_cache_client()
        cls.namespace = 'test-namespace'

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test auto-initialization
        with Html_Cache__Document() as _:
            assert type(_)        is Html_Cache__Document
            assert base_types(_)  == [Type_Safe, object]
            assert _.cache_id     is None
            assert _.root         is None

    def test__init____with_params(self):                                         # Test with parameters
        with Html_Cache__Document(client    = self.html_cache_client,
                                  namespace = self.namespace        ,
                                  cache_key = 'example.com/page'    ) as _:
            assert _.client    is self.html_cache_client
            assert _.namespace == self.namespace
            assert _.cache_key == 'example.com/page'
            assert _.file_id   == 'html-entry'                                   # Default value

    def test__init____custom_file_id(self):                                      # Test custom file_id
        with Html_Cache__Document(client    = self.html_cache_client,
                                  namespace = self.namespace        ,
                                  cache_key = 'test/key'            ,
                                  file_id   = 'custom-entry'        ) as _:
            assert _.file_id == 'custom-entry'

    # ═══════════════════════════════════════════════════════════════════════════
    # ensure_cache_id Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_ensure_cache_id__creates_new(self):                                 # Test creates new entry
        with Html_Cache__Document(client    = self.html_cache_client,
                                  namespace = self.namespace        ,
                                  cache_key = 'new/document'        ) as _:
            cache_id = _.ensure_cache_id()

            assert cache_id is not None
            assert is_guid(cache_id) is True
            assert _.cache_id == cache_id

    def test_ensure_cache_id__returns_existing(self):                            # Test returns same ID
        with Html_Cache__Document(client    = self.html_cache_client,
                                  namespace = self.namespace        ,
                                  cache_key = 'existing/document'   ) as _:
            cache_id_1 = _.ensure_cache_id()
            cache_id_2 = _.ensure_cache_id()

            assert cache_id_1 == cache_id_2

    def test_ensure_cache_id__uses_provided(self):                               # Test uses pre-set ID
        with Html_Cache__Document(client    = self.html_cache_client,
                                  namespace = self.namespace        ,
                                  cache_key = 'preset/document'     ,
                                  cache_id  = 'preset-id-12345'     ) as _:
            cache_id = _.ensure_cache_id()

            assert cache_id == 'preset-id-12345'

    # ═══════════════════════════════════════════════════════════════════════════
    # create_entry Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_create_entry(self):                                                 # Test creates entry
        with Html_Cache__Document(client    = self.html_cache_client,
                                  namespace = self.namespace        ,
                                  cache_key = 'create/entry'        ) as _:
            cache_id = _.create_entry()

            assert cache_id is not None
            assert is_guid(cache_id) is True

    # ═══════════════════════════════════════════════════════════════════════════
    # load_root / save_root Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_load_root__creates_new(self):                                       # Test creates root if none
        with Html_Cache__Document(client    = self.html_cache_client,
                                  namespace = self.namespace        ,
                                  cache_key = 'new/root'            ) as _:
            root = _.load_root()

            assert root           is not None
            assert type(root)     is Schema__Html_Cache__Root
            assert root.cache_key == 'new/root'
            assert root.created_at is not None

    def test_load_root__returns_same(self):                                      # Test returns cached root
        with Html_Cache__Document(client    = self.html_cache_client,
                                  namespace = self.namespace        ,
                                  cache_key = 'cached/root'         ) as _:
            root_1 = _.load_root()
            root_2 = _.load_root()

            assert root_1 is root_2                                              # Same object

    # ═══════════════════════════════════════════════════════════════════════════
    # update_lets_status / get_lets_status Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_update_lets_status(self):                                           # Test updates status
        with Html_Cache__Document(client    = self.html_cache_client,
                                  namespace = self.namespace        ,
                                  cache_key = 'status/update'       ) as _:
            status = Schema__LETS__Status(name        = 'html-to-dict',
                                          completed   = True          ,
                                          data_key    = 'html-to-dict',
                                          file_id     = 'html-dict'   ,
                                          duration_ms = 150           )

            result = _.update_lets_status(status=status)

            assert result is True

    def test_get_lets_status(self):                                              # Test gets status
        with Html_Cache__Document(client    = self.html_cache_client,
                                  namespace = self.namespace        ,
                                  cache_key = 'status/get'          ) as _:
            # First update
            status = Schema__LETS__Status(name        = 'dict-to-mgraph',
                                          completed   = True           ,
                                          data_key    = 'dict-to-mgraph',
                                          file_id     = 'mgraph'       ,
                                          duration_ms = 200            )
            _.update_lets_status(status=status)

            # Then get
            retrieved = _.get_lets_status(name=Safe_Str__LETS__Name('dict-to-mgraph'))

            assert retrieved             is not None
            assert retrieved.name        == 'dict-to-mgraph'
            assert retrieved.completed   is True
            assert retrieved.duration_ms == 200

    def test_get_lets_status__not_found(self):                                   # Test returns None
        with Html_Cache__Document(client    = self.html_cache_client,
                                  namespace = self.namespace        ,
                                  cache_key = 'status/missing'      ) as _:
            _.load_root()                                                        # Initialize root

            result = _.get_lets_status(name=Safe_Str__LETS__Name('nonexistent'))

            assert result is None

    # ═══════════════════════════════════════════════════════════════════════════
    # layer Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_layer(self):                                                        # Test creates layer accessor
        with Html_Cache__Document(client    = self.html_cache_client,
                                  namespace = self.namespace        ,
                                  cache_key = 'layer/access'        ) as _:
            layer = _.layer(layer_name=Safe_Str__Layer_Name('html-to-dict'))

            assert type(layer)      is Html_Cache__Layer
            assert layer.document   is _
            assert layer.layer_name == 'html-to-dict'

    def test_layer__multiple_layers(self):                                       # Test multiple layers
        with Html_Cache__Document(client    = self.html_cache_client,
                                  namespace = self.namespace        ,
                                  cache_key = 'layer/multiple'      ) as _:
            layer1 = _.layer(layer_name=Safe_Str__Layer_Name('layer-1'))
            layer2 = _.layer(layer_name=Safe_Str__Layer_Name('layer-2'))

            assert layer1.layer_name == 'layer-1'
            assert layer2.layer_name == 'layer-2'
            assert layer1.document is layer2.document                            # Same document

    # ═══════════════════════════════════════════════════════════════════════════
    # layer_status Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_layer_status__empty(self):                                          # Test empty status
        with Html_Cache__Document(client    = self.html_cache_client,
                                  namespace = self.namespace        ,
                                  cache_key = 'status/empty'        ) as _:
            status = _.layer_status()

            assert status == {}

    def test_layer_status__with_completions(self):                               # Test with completions
        with Html_Cache__Document(client    = self.html_cache_client,
                                  namespace = self.namespace        ,
                                  cache_key = 'status/complete'     ) as _:
            # Add statuses
            _.update_lets_status(Schema__LETS__Status(name='lets-1', completed=True,
                                                      data_key='lets-1', file_id='out'))
            _.update_lets_status(Schema__LETS__Status(name='lets-2', completed=False,
                                                      data_key='lets-2', file_id='out'))

            status = _.layer_status()

            assert status.get(Safe_Str__LETS__Name('lets-1')) is True
            assert status.get(Safe_Str__LETS__Name('lets-2')) is False

    # ═══════════════════════════════════════════════════════════════════════════
    # exists / delete Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_exists(self):                                                       # Test exists returns True
        with Html_Cache__Document(client    = self.html_cache_client,
                                  namespace = self.namespace        ,
                                  cache_key = 'exists/doc'          ) as _:
            _.ensure_cache_id()
            assert _.exists() is True

    def test_delete(self):                                                       # Test delete removes doc
        with Html_Cache__Document(client    = self.html_cache_client,
                                  namespace = self.namespace        ,
                                  cache_key = 'delete/doc'          ) as _:
            _.ensure_cache_id()
            assert _.exists() is True

            result = _.delete()
            assert result is True
            assert _.exists() is False

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_integration__full_document_workflow(self):                          # Test complete workflow
        cache_key = 'integration/full-doc'

        with Html_Cache__Document(client    = self.html_cache_client,
                                  namespace = self.namespace        ,
                                  cache_key = cache_key             ) as _:
            # 1. Ensure cache_id
            cache_id = _.ensure_cache_id()
            assert cache_id is not None

            # 2. Load root
            root = _.load_root()
            assert root.cache_key == cache_key

            # 3. Update LETS statuses
            _.update_lets_status(Schema__LETS__Status(name        = 'html-to-dict',
                                                      completed   = True          ,
                                                      data_key    = 'html-to-dict',
                                                      file_id     = 'html-dict'   ,
                                                      duration_ms = 100           ))
            _.update_lets_status(Schema__LETS__Status(name        = 'dict-to-mgraph',
                                                      completed   = True           ,
                                                      data_key    = 'dict-to-mgraph',
                                                      file_id     = 'mgraph'       ,
                                                      duration_ms = 200            ))

            # 4. Check layer status
            status = _.layer_status()
            assert len(status) == 2

            # 5. Get specific status
            lets_status = _.get_lets_status(name=Safe_Str__LETS__Name('html-to-dict'))
            assert lets_status.completed   is True
            assert lets_status.duration_ms == 100

            # 6. Use layers
            layer = _.layer(layer_name=Safe_Str__Layer_Name('html-to-dict'))
            layer.save_string(file_id='html', content='<html>test</html>')
            assert layer.exists(file_id='html', data_type=Enum__Cache__Data_Type.STRING) is True
            assert layer.load_string(file_id='html') == '<html>test</html>'

            # 7. Check document exists
            assert _.exists() is True

            # 8. Delete document
            _.delete()
            assert _.exists() is False
