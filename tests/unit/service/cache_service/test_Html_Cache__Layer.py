# ═══════════════════════════════════════════════════════════════════════════════
# test_Html_Cache__Layer - Tests for single layer access
# Uses in-memory cache service via FastAPI test client
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                            import TestCase
from osbot_utils.type_safe.Type_Safe                                                     import Type_Safe
from osbot_utils.utils.Objects                                                           import base_types
from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type           import Enum__Cache__Data_Type
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Layer                import Html_Cache__Layer
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Document             import Html_Cache__Document
from mgraph_ai_service_html_graph.service.cache_storage.safe_str.Safe_Str__Layer_Name    import Safe_Str__Layer_Name
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                 import create_html_cache_client


class test_Html_Cache__Layer(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup - in-memory cache
        cls.html_cache_client, cls.cache_service = create_html_cache_client()
        cls.namespace  = 'test-namespace'
        cls.cache_key  = 'layer/test/doc'

        # Create document for layer tests
        cls.document = Html_Cache__Document(client    = cls.html_cache_client,
                                            namespace = cls.namespace        ,
                                            cache_key = cls.cache_key        )
        cls.cache_id = cls.document.ensure_cache_id()

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test auto-initialization
        with Html_Cache__Layer() as _:
            assert type(_)        is Html_Cache__Layer
            assert base_types(_)  == [Type_Safe, object]

    def test__init____with_document_and_layer(self):                             # Test with document
        layer_name = Safe_Str__Layer_Name('html-to-dict')
        with Html_Cache__Layer(document=self.document, layer_name=layer_name) as _:
            assert _.document   is self.document
            assert _.layer_name == layer_name

    # ═══════════════════════════════════════════════════════════════════════════
    # save_json / load_json Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_save_json(self):                                                    # Test save JSON
        layer_name = Safe_Str__Layer_Name('json-layer')
        layer      = Html_Cache__Layer(document=self.document, layer_name=layer_name)
        data       = {'tag': 'html', 'children': []}

        result = layer.save_json(file_id='output', data=data)

        assert result is True

    def test_save_and_load_json(self):                                           # Test JSON roundtrip
        layer_name = Safe_Str__Layer_Name('roundtrip-json')
        layer      = Html_Cache__Layer(document=self.document, layer_name=layer_name)
        data       = {'tag': 'html', 'body': {'text': 'test'}}

        # Save
        layer.save_json(file_id='data', data=data)

        # Load
        loaded = layer.load_json(file_id='data')

        assert loaded         is not None
        assert loaded['tag']  == 'html'

    def test_load_json__not_found(self):                                         # Test returns None when not found
        layer_name = Safe_Str__Layer_Name('nonexistent-json')
        layer      = Html_Cache__Layer(document=self.document, layer_name=layer_name)

        result = layer.load_json(file_id='missing')

        assert result is None

    def test_update_json(self):                                                  # Test update JSON
        layer_name = Safe_Str__Layer_Name('update-json')
        layer      = Html_Cache__Layer(document=self.document, layer_name=layer_name)

        # Create initial
        layer.save_json(file_id='data', data={'version': 1})

        # Update
        result = layer.update_json(file_id='data', data={'version': 2})
        assert result is True

        # Verify
        loaded = layer.load_json(file_id='data')
        assert loaded == {'version': 2}

    # ═══════════════════════════════════════════════════════════════════════════
    # save_string / load_string Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_save_string(self):                                                  # Test save string
        layer_name = Safe_Str__Layer_Name('string-layer')
        layer      = Html_Cache__Layer(document=self.document, layer_name=layer_name)
        content    = '<html><body>Test</body></html>'

        result = layer.save_string(file_id='source', content=content)

        assert result is True

    def test_save_and_load_string(self):                                         # Test string roundtrip
        layer_name = Safe_Str__Layer_Name('roundtrip-string')
        layer      = Html_Cache__Layer(document=self.document, layer_name=layer_name)
        content    = '<html><head><title>Test</title></head></html>'

        # Save
        layer.save_string(file_id='html', content=content)

        # Load
        loaded = layer.load_string(file_id='html')

        assert loaded == content

    def test_load_string__not_found(self):                                       # Test returns None when not found
        layer_name = Safe_Str__Layer_Name('missing-string')
        layer      = Html_Cache__Layer(document=self.document, layer_name=layer_name)

        result = layer.load_string(file_id='missing')

        assert result is None

    def test_update_string(self):                                                # Test update string
        layer_name = Safe_Str__Layer_Name('update-string')
        layer      = Html_Cache__Layer(document=self.document, layer_name=layer_name)

        # Create initial
        layer.save_string(file_id='html', content='original')

        # Update
        result = layer.update_string(file_id='html', content='updated')
        assert result is True

        # Verify
        loaded = layer.load_string(file_id='html')
        assert loaded == 'updated'

    # ═══════════════════════════════════════════════════════════════════════════
    # exists Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_exists__true(self):                                                 # Test exists returns True
        layer_name = Safe_Str__Layer_Name('exists-layer')
        layer      = Html_Cache__Layer(document=self.document, layer_name=layer_name)

        # Create data
        layer.save_string(file_id='data', content='exists')

        # Check exists
        result = layer.exists(file_id='data', data_type=Enum__Cache__Data_Type.STRING)

        assert result is True

    def test_exists__false(self):                                                # Test exists returns False
        layer_name = Safe_Str__Layer_Name('noexist-layer')
        layer      = Html_Cache__Layer(document=self.document, layer_name=layer_name)

        result = layer.exists(file_id='nonexistent', data_type=Enum__Cache__Data_Type.STRING)

        assert result is False

    # ═══════════════════════════════════════════════════════════════════════════
    # delete Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_delete(self):                                                       # Test delete removes data
        layer_name = Safe_Str__Layer_Name('delete-layer')
        layer      = Html_Cache__Layer(document=self.document, layer_name=layer_name)

        # Create data
        layer.save_string(file_id='to-delete', content='delete me')
        assert layer.exists(file_id='to-delete', data_type=Enum__Cache__Data_Type.STRING) is True

        # Delete
        result = layer.delete(file_id='to-delete', data_type=Enum__Cache__Data_Type.STRING)
        assert result is True

        # Verify gone
        assert layer.exists(file_id='to-delete', data_type=Enum__Cache__Data_Type.STRING) is False

    def test_delete__not_found(self):                                            # Test delete returns False
        layer_name = Safe_Str__Layer_Name('delete-missing')
        layer      = Html_Cache__Layer(document=self.document, layer_name=layer_name)

        result = layer.delete(file_id='never-existed', data_type=Enum__Cache__Data_Type.STRING)

        assert result is False

    # ═══════════════════════════════════════════════════════════════════════════
    # list_files Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_list_files(self):                                                   # Test list files in layer
        layer_name = Safe_Str__Layer_Name('list-layer')
        layer      = Html_Cache__Layer(document=self.document, layer_name=layer_name)

        # Create some files
        layer.save_string(file_id='file1', content='content1')
        layer.save_json(file_id='file2', data={'key': 'val'})

        result = layer.list_files()

        assert result is not None
        assert result.file_count >= 2

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_integration__multiple_layers(self):                                 # Test multiple layers same doc
        layer1 = Html_Cache__Layer(document=self.document,
                                   layer_name=Safe_Str__Layer_Name('layer-1'))
        layer2 = Html_Cache__Layer(document=self.document,
                                   layer_name=Safe_Str__Layer_Name('layer-2'))

        # Save to different layers
        layer1.save_string(file_id='data', content='layer 1 content')
        layer2.save_string(file_id='data', content='layer 2 content')

        # Verify isolation
        assert layer1.load_string(file_id='data') == 'layer 1 content'
        assert layer2.load_string(file_id='data') == 'layer 2 content'

    def test_integration__full_workflow(self):                                   # Test complete layer workflow
        layer_name = Safe_Str__Layer_Name('full-workflow')
        layer      = Html_Cache__Layer(document=self.document, layer_name=layer_name)

        # 1. Save string
        layer.save_string(file_id='html', content='<html/>')
        assert layer.exists(file_id='html', data_type=Enum__Cache__Data_Type.STRING) is True

        # 2. Save JSON
        layer.save_json(file_id='dict', data={'tag': 'html'})
        assert layer.exists(file_id='dict', data_type=Enum__Cache__Data_Type.JSON) is True

        # 3. Load both
        html = layer.load_string(file_id='html')
        assert html == '<html/>'

        json_data = layer.load_json(file_id='dict')
        assert json_data == {'tag': 'html'}

        # 4. Update both
        layer.update_string(file_id='html', content='<html>updated</html>')
        layer.update_json(file_id='dict', data={'tag': 'html', 'updated': True})

        assert layer.load_string(file_id='html') == '<html>updated</html>'
        assert layer.load_json(file_id='dict') == {'tag': 'html', 'updated': True}

        # 5. Delete string
        layer.delete(file_id='html', data_type=Enum__Cache__Data_Type.STRING)
        assert layer.exists(file_id='html', data_type=Enum__Cache__Data_Type.STRING) is False
        assert layer.exists(file_id='dict', data_type=Enum__Cache__Data_Type.JSON)   is True
