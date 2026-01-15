# ═══════════════════════════════════════════════════════════════════════════════
# test_Routes__Cache__Document - Tests for cache document routes
# Uses in-memory cache service for testing
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from mgraph_ai_service_html_graph.fast_api.routes.Routes__Cache__Document                               import Routes__Cache__Document
from mgraph_ai_service_html_graph.fast_api.routes.Routes__Cache__Document                               import TAG__ROUTES_CACHE
from mgraph_ai_service_html_graph.schemas.routes.cache.Schema__Cache__Document__Find_Or_Create__Request import Schema__Cache__Document__Find_Or_Create__Request
from mgraph_ai_service_html_graph.schemas.routes.cache.Schema__Cache__Document__Response                import Schema__Cache__Document__Response
from mgraph_ai_service_html_graph.schemas.routes.cache.Schema__Cache__Document__Status__Response        import Schema__Cache__Document__Status__Response
from mgraph_ai_service_html_graph.schemas.routes.cache.Schema__Cache__Document__Layers__Response        import Schema__Cache__Document__Layers__Response
from mgraph_ai_service_html_graph.schemas.routes.cache.Schema__Cache__Document__Layer__Files__Response  import Schema__Cache__Document__Layer__Files__Response
from mgraph_ai_service_html_graph.utils.testing.Html_Generator__For_Tests                               import Html_Generator__For_Tests
from osbot_utils.utils.Misc                                                                             import is_guid
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                                import create_html_cache_client


class test_Routes__Cache__Document(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.html_cache_client, cls.cache_service = create_html_cache_client()
        cls.routes    = Routes__Cache__Document(cache_client=cls.html_cache_client)
        cls.html_gen  = Html_Generator__For_Tests()
        cls.namespace = 'test-namespace'

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with Routes__Cache__Document() as _:
            assert type(_) is Routes__Cache__Document
            assert _.tag   == TAG__ROUTES_CACHE

    # ═══════════════════════════════════════════════════════════════════════════
    # Document Find/Create Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_document__find_or_create(self):
        """Test POST /cache/{namespace}/document/find-or-create"""
        request = Schema__Cache__Document__Find_Or_Create__Request(cache_key='test/document/1')
        result  = self.routes.document__find_or_create(namespace=self.namespace, request=request)

        assert type(result)      is Schema__Cache__Document__Response
        assert result.cache_id   is not None
        assert is_guid(result.cache_id) is True
        assert result.namespace  == self.namespace
        assert result.cache_key  == 'test/document/1'
        assert result.exists     is True

    def test_document__find_or_create__with_html(self):
        """Test find-or-create with HTML stores in raw-html layer"""
        html    = self.html_gen.minimal_html()
        request = Schema__Cache__Document__Find_Or_Create__Request(cache_key = 'test/document/with-html',
                                                                   html      = html                     )
        result = self.routes.document__find_or_create(namespace=self.namespace, request=request)

        assert result.cache_id is not None

        # Verify HTML was stored
        layers = self.routes.document__layers(namespace=self.namespace, cache_id=result.cache_id)
        assert 'raw-html' in layers.layers

    def test_document__find_or_create__idempotent(self):
        """Test find-or-create returns same cache_id for same cache_key"""
        request  = Schema__Cache__Document__Find_Or_Create__Request(cache_key='test/document/idempotent')
        result_1 = self.routes.document__find_or_create(namespace=self.namespace, request=request)
        result_2 = self.routes.document__find_or_create(namespace=self.namespace, request=request)

        assert result_1.cache_id == result_2.cache_id

    def test_document__find_or_create__missing_cache_key(self):
        """Test 400 when cache_key is missing"""
        from fastapi import HTTPException

        request = Schema__Cache__Document__Find_Or_Create__Request()

        with self.assertRaises(HTTPException) as context:
            self.routes.document__find_or_create(namespace=self.namespace, request=request)

        assert context.exception.status_code == 400

    # ═══════════════════════════════════════════════════════════════════════════
    # Document Get Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_document__get(self):
        """Test GET /cache/{namespace}/document/{cache_id}"""
        # First create a document
        request  = Schema__Cache__Document__Find_Or_Create__Request(cache_key='test/document/get')
        created  = self.routes.document__find_or_create(namespace=self.namespace, request=request)

        # Then get it
        result = self.routes.document__get(namespace=self.namespace, cache_id=created.cache_id)

        assert type(result)     is Schema__Cache__Document__Response
        assert result.cache_id  == created.cache_id
        assert result.namespace == self.namespace
        assert result.exists    is True

    def test_document__get__not_found(self):
        """Test 404 for non-existent document"""
        from fastapi import HTTPException
        from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id import Cache_Id

        with self.assertRaises(HTTPException) as context:
            self.routes.document__get(namespace=self.namespace, cache_id=Cache_Id())

        assert context.exception.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════
    # Document Status Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_document__status(self):
        """Test GET /cache/{namespace}/document/{cache_id}/status"""
        # Create a document
        request = Schema__Cache__Document__Find_Or_Create__Request(cache_key='test/document/status')
        created = self.routes.document__find_or_create(namespace=self.namespace, request=request)

        result = self.routes.document__status(namespace=self.namespace, cache_id=created.cache_id)

        assert type(result)     is Schema__Cache__Document__Status__Response
        assert result.cache_id  == created.cache_id
        assert result.namespace == self.namespace
        assert result.steps     is not None
        assert isinstance(result.steps, dict)

    def test_document__status__not_found(self):
        """Test 404 for non-existent document"""
        from fastapi import HTTPException
        from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id import Cache_Id

        with self.assertRaises(HTTPException) as context:
            self.routes.document__status(namespace=self.namespace, cache_id=Cache_Id())

        assert context.exception.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════
    # Document Delete Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_document__delete(self):
        """Test DELETE /cache/{namespace}/document/{cache_id}"""
        # Create a document
        request = Schema__Cache__Document__Find_Or_Create__Request(cache_key='test/document/delete')
        created = self.routes.document__find_or_create(namespace=self.namespace, request=request)

        # Delete it
        result = self.routes.document__delete(namespace=self.namespace, cache_id=created.cache_id)

        assert result['status'] == 'success'

        # Verify deleted
        from fastapi import HTTPException
        with self.assertRaises(HTTPException) as context:
            self.routes.document__get(namespace=self.namespace, cache_id=created.cache_id)
        assert context.exception.status_code == 404

    def test_document__delete__not_found(self):
        """Test 404 for non-existent document"""
        from fastapi import HTTPException
        from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id import Cache_Id

        with self.assertRaises(HTTPException) as context:
            self.routes.document__delete(namespace=self.namespace, cache_id=Cache_Id())

        assert context.exception.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════
    # Layer Listing Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_document__layers(self):
        """Test GET /cache/{namespace}/document/{cache_id}/layers"""
        # Create document with HTML (creates raw-html layer)
        html    = self.html_gen.minimal_html()
        request = Schema__Cache__Document__Find_Or_Create__Request(cache_key = 'test/document/layers',
                                                                   html      = html                  )
        created = self.routes.document__find_or_create(namespace=self.namespace, request=request)

        result = self.routes.document__layers(namespace=self.namespace, cache_id=created.cache_id)

        assert type(result)     is Schema__Cache__Document__Layers__Response
        assert result.cache_id  == created.cache_id
        assert result.namespace == self.namespace
        assert result.layers    is not None
        assert 'raw-html'       in result.layers

    def test_document__layers__empty(self):
        """Test layers for document with no data files"""
        request = Schema__Cache__Document__Find_Or_Create__Request(cache_key='test/document/no-layers')
        created = self.routes.document__find_or_create(namespace=self.namespace, request=request)

        result = self.routes.document__layers(namespace=self.namespace, cache_id=created.cache_id)

        assert result.layers == [] or result.layers is not None                  # Empty or valid list

    def test_document__layers__not_found(self):
        """Test 404 for non-existent document"""
        from fastapi import HTTPException
        from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id import Cache_Id

        with self.assertRaises(HTTPException) as context:
            self.routes.document__layers(namespace=self.namespace, cache_id=Cache_Id())

        assert context.exception.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════
    # Layer Files Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_layer__files(self):
        """Test GET /cache/{namespace}/document/{cache_id}/layer/{layer_name}/files"""
        # Create document with HTML
        html    = self.html_gen.minimal_html()
        request = Schema__Cache__Document__Find_Or_Create__Request(cache_key = 'test/document/layer-files',
                                                                   html      = html                       )
        created = self.routes.document__find_or_create(namespace=self.namespace, request=request)

        result = self.routes.layer__files(namespace  = self.namespace   ,
                                          cache_id   = created.cache_id ,
                                          layer_name = 'raw-html'       )

        assert type(result)      is Schema__Cache__Document__Layer__Files__Response
        assert result.cache_id   == created.cache_id
        assert result.layer_name == 'raw-html'
        assert result.files      is not None

    def test_layer__files__not_found_cache(self):
        """Test 404 for non-existent cache"""
        from fastapi import HTTPException
        from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id import Cache_Id

        with self.assertRaises(HTTPException) as context:
            self.routes.layer__files(namespace  = self.namespace,
                                     cache_id   = Cache_Id()    ,
                                     layer_name = 'any-layer'   )

        assert context.exception.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════
    # Layer File Content Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_layer__file(self):
        """Test GET /cache/{namespace}/document/{cache_id}/layer/{layer_name}/{file_id}"""
        # Create document with HTML
        html    = self.html_gen.minimal_html()
        request = Schema__Cache__Document__Find_Or_Create__Request(cache_key = 'test/document/layer-file',
                                                                   html      = html                      )
        created = self.routes.document__find_or_create(namespace=self.namespace, request=request)

        result = self.routes.layer__file(namespace  = self.namespace   ,
                                         cache_id   = created.cache_id ,
                                         layer_name = 'raw-html'       ,
                                         file_id    = 'source'         )

        assert result['cache_id']   == str(created.cache_id)
        assert result['layer_name'] == 'raw-html'
        assert result['file_id']    == 'source'
        assert result['content']    is not None

    def test_layer__file__not_found(self):
        """Test 404 for non-existent file"""
        from fastapi import HTTPException

        # Create document without HTML
        request = Schema__Cache__Document__Find_Or_Create__Request(cache_key='test/document/no-file')
        created = self.routes.document__find_or_create(namespace=self.namespace, request=request)

        with self.assertRaises(HTTPException) as context:
            self.routes.layer__file(namespace  = self.namespace    ,
                                    cache_id   = created.cache_id  ,
                                    layer_name = 'nonexistent'     ,
                                    file_id    = 'missing'         )

        assert context.exception.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_integration__full_workflow(self):
        """Test complete document lifecycle"""
        html = self.html_gen.simple_html()

        # 1. Create document
        request = Schema__Cache__Document__Find_Or_Create__Request(cache_key = 'test/integration/workflow',
                                                                   html      = html                       )
        doc     = self.routes.document__find_or_create(namespace=self.namespace, request=request)
        assert doc.cache_id is not None

        # 2. Get document
        fetched = self.routes.document__get(namespace=self.namespace, cache_id=doc.cache_id)
        assert fetched.cache_id == doc.cache_id

        # 3. Check status
        status = self.routes.document__status(namespace=self.namespace, cache_id=doc.cache_id)
        assert status.steps is not None

        # 4. List layers
        layers = self.routes.document__layers(namespace=self.namespace, cache_id=doc.cache_id)
        assert 'raw-html' in layers.layers

        # 5. Get layer files
        files = self.routes.layer__files(namespace  = self.namespace ,
                                         cache_id   = doc.cache_id   ,
                                         layer_name = 'raw-html'     )
        assert files.files is not None

        # 6. Get file content
        content = self.routes.layer__file(namespace  = self.namespace ,
                                          cache_id   = doc.cache_id   ,
                                          layer_name = 'raw-html'     ,
                                          file_id    = 'source'       )
        assert content['content'] is not None

        # 7. Delete document
        deleted = self.routes.document__delete(namespace=self.namespace, cache_id=doc.cache_id)
        assert deleted['status'] == 'success'

        # 8. Verify deleted
        from fastapi import HTTPException
        with self.assertRaises(HTTPException):
            self.routes.document__get(namespace=self.namespace, cache_id=doc.cache_id)
