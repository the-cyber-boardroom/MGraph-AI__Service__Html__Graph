# ═══════════════════════════════════════════════════════════════════════════════
# test_Cache__Namespace - Tests for namespace helper class
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                       import TestCase

from mgraph_ai_service_cache_client.client.cache_service.register_cache_service import register_cache_service__in_memory
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client import Html_Cache__Client
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Namespace       import Html_Cache__Namespace
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid               import Random_Guid
from mgraph_ai_service_cache_client.client.client_entities.Cache__Entity            import Cache__Entity
from mgraph_ai_service_cache_client.client.client_entities.Cache__Entity__Data_File import Cache__Entity__Data_File



class test_Html_Cache__Namespace(TestCase):

    @classmethod
    def setUpClass(cls):                                                            # Shared test objects
        cls.cache_service_client = register_cache_service__in_memory(return_client=True)
        cls.html_cache_client    = Html_Cache__Client()
        cls.cache_namespace = Html_Cache__Namespace(html_cache_client = cls.html_cache_client  ,
                                                    namespace         = 'test-cache-namespace' )
        cls.create_test_data()

    @classmethod
    def create_test_data(cls):                                                      # Create test data
        cls.cache_key    = f'test/namespace/{Random_Guid()}'
        cls.test_entity  = cls.cache_namespace.entity__create(cache_key=cls.cache_key)
        cls.cache_id     = cls.test_entity.cache_id
        cls.test_content = '<html><body>Test Content</body></html>'
        cls.test_json    = {'key': 'value', 'count': 42}

    # ═══════════════════════════════════════════════════════════════════════════════
    # Test Setup
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__setUpClass(self):                                                     # Test setup verification
        assert type(self.cache_namespace)             is Html_Cache__Namespace
        assert self.cache_namespace.html_cache_client == self.html_cache_client
        assert self.cache_namespace.namespace         == 'test-cache-namespace'

    def test__create_test_data(self):                                               # Test data verification
        assert type(self.test_entity)     is Cache__Entity
        assert self.test_entity.cache_id  == self.cache_id
        assert self.test_entity.namespace == 'test-cache-namespace'

    # ═══════════════════════════════════════════════════════════════════════════════
    # entity Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_entity__returns_cache_entity(self):                                    # Test entity returns object
        entity = self.cache_namespace.entity(cache_id=self.cache_id)

        assert type(entity)     is Cache__Entity
        assert entity.cache_id  == self.cache_id
        assert entity.namespace == 'test-cache-namespace'

    def test_entity__can_access_entry_json(self):                                   # Test entity access
        entity     = self.cache_namespace.entity(cache_id=self.cache_id)
        entry_json = entity.entry__json()

        assert entry_json == {'cache_key': self.cache_key}

    # ═══════════════════════════════════════════════════════════════════════════════
    # entity__create Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_entity__create__returns_cache_entity(self):                            # Test create returns entity
        new_cache_key = f'test/namespace/create-{Random_Guid()}'

        entity = self.cache_namespace.entity__create(cache_key=new_cache_key)

        assert type(entity)         is Cache__Entity
        assert entity.cache_id      != ''
        assert entity.namespace     == 'test-cache-namespace'
        assert entity.entry__json() == {'cache_key': new_cache_key}

    def test_entity__create__with_custom_file_id(self):                             # Test create with file_id
        new_cache_key = f'test/namespace/custom-{Random_Guid()}'

        entity = self.cache_namespace.entity__create(cache_key = new_cache_key  ,
                                                     file_id   = 'custom-root'  )

        assert type(entity)    is Cache__Entity
        assert entity.cache_id != ''

    # ═══════════════════════════════════════════════════════════════════════════════
    # entity__via__cache_key Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_entity__via__cache_key__found(self):                                           # Test lookup found
        entity = self.cache_namespace.entity__via__cache_key(cache_key=self.cache_key)

        assert type(entity)    is Cache__Entity
        assert entity.cache_id == self.cache_id

    def test_entity__via__cache_key__not_found(self):                                       # Test lookup not found
        entity = self.cache_namespace.entity__via__cache_key(cache_key=f'nonexistent/{Random_Guid()}')

        assert entity is None

    # ═══════════════════════════════════════════════════════════════════════════════
    # entity__get_or_create Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_entity__get_or_create__gets_existing(self):                            # Test gets existing entity
        entity = self.cache_namespace.entity__get_or_create(cache_key=self.cache_key)

        assert type(entity)    is Cache__Entity
        assert entity.cache_id == self.cache_id                                     # Same entity

    def test_entity__get_or_create__creates_new(self):                              # Test creates new entity
        new_cache_key = f'test/namespace/get-or-create-{Random_Guid()}'

        entity = self.cache_namespace.entity__get_or_create(cache_key=new_cache_key)

        assert type(entity)         is Cache__Entity
        assert entity.cache_id      != ''
        assert entity.entry__json() == {'cache_key': new_cache_key}

    # ═══════════════════════════════════════════════════════════════════════════════
    # entity__exists Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_entity__exists__returns_true(self):                                    # Test exists returns true
        result = self.cache_namespace.entity__exists(cache_id=self.cache_id)

        assert result is True

    def test_entity__exists__returns_false(self):                                   # Test exists returns false
        result = self.cache_namespace.entity__exists(cache_id=Random_Guid())

        assert result is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # entity__delete Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_entity__delete__success(self):                                         # Test delete success
        new_cache_key = f'test/namespace/delete-{Random_Guid()}'
        entity        = self.cache_namespace.entity__create(cache_key=new_cache_key)
        cache_id      = entity.cache_id

        result = self.cache_namespace.entity__delete(cache_id=cache_id)

        assert result                                              is True
        assert self.cache_namespace.entity__exists(cache_id=cache_id) is False

    def test_entity__delete__not_found(self):                                       # Test delete not found
        result = self.cache_namespace.entity__delete(cache_id=Random_Guid())

        assert result is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # data_file Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_data_file__returns_data_file_object(self):                             # Test returns data file
        data_file = self.cache_namespace.data_file(cache_id     = self.cache_id  ,
                                                   data_key     = 'html/content' ,
                                                   data_file_id = 'raw'          )

        assert type(data_file) is Cache__Entity__Data_File

    def test_data_file__can_store_and_retrieve_string(self):                        # Test string store/retrieve
        new_cache_key = f'test/namespace/data-{Random_Guid()}'
        entity        = self.cache_namespace.entity__create(cache_key=new_cache_key)
        data_file     = self.cache_namespace.data_file(cache_id     = entity.cache_id ,
                                                       data_key     = 'html'          ,
                                                       data_file_id = 'raw'           )

        data_file.store__string(self.test_content)

        assert data_file.exists__string() is True
        assert data_file.string()         == self.test_content

    def test_data_file__can_store_and_retrieve_json(self):                          # Test JSON store/retrieve
        new_cache_key = f'test/namespace/json-{Random_Guid()}'
        entity        = self.cache_namespace.entity__create(cache_key=new_cache_key)
        data_file     = self.cache_namespace.data_file(cache_id     = entity.cache_id ,
                                                       data_key     = 'meta'          ,
                                                       data_file_id = 'info'          )

        data_file.store__json(self.test_json)

        assert data_file.exists__json() is True
        assert data_file.json()         == self.test_json

    # ═══════════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_full_workflow__create_store_retrieve_delete(self):                     # Test complete workflow
        cache_key = f'test/namespace/workflow-{Random_Guid()}'
        entity    = self.cache_namespace.entity__create(cache_key=cache_key)
        cache_id  = entity.cache_id

        data_file = self.cache_namespace.data_file(cache_id     = cache_id  ,
                                                   data_key     = 'content' ,
                                                   data_file_id = 'main'    )
        data_file.store__string('<html>Workflow Test</html>')

        found_entity = self.cache_namespace.entity__via__cache_key(cache_key=cache_key)
        assert found_entity.cache_id == cache_id

        found_data_file = found_entity.data_file(data_key     = 'content' ,
                                                 data_file_id = 'main'    )
        assert found_data_file.string() == '<html>Workflow Test</html>'

        assert self.cache_namespace.entity__delete(cache_id=cache_id) is True
        assert self.cache_namespace.entity__exists(cache_id=cache_id) is False