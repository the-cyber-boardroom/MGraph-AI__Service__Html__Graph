# ═══════════════════════════════════════════════════════════════════════════════
# test_Routes__Cache__Data__client - HTTP client tests for cache data file routes
# Tests REST API calls: GET, POST, PUT, DELETE via FastAPI test client
# ═══════════════════════════════════════════════════════════════════════════════

import pytest
from unittest                                                                               import TestCase
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid                       import Random_Guid
from osbot_utils.utils.Files                                                                import path_combine
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                    import setup__html_graph_service__fast_api_test_objs, unload_local_dotenv
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                    import load_local_dotenv
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                    import TEST_API_KEY__NAME, TEST_API_KEY__VALUE


class test_Routes__Cache__Data__client(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dot_env_file = path_combine(__file__, '../.local-cache.env')
        if load_local_dotenv(cls.dot_env_file) is False:
            pytest.skip('test needs local env vars set')

        with setup__html_graph_service__fast_api_test_objs() as _:
            cls.client = _.fast_api__client
            cls.client.headers[TEST_API_KEY__NAME] = TEST_API_KEY__VALUE

        cls.namespace      = 'test-routes-cache-data-client'
        cls.base_path_data = '/cache-data'
        cls.base_path_entity = '/cache-entity'
        cls.cache_id       = cls.create_test_entity()

    @classmethod
    def tearDownClass(cls):
        assert unload_local_dotenv(cls.dot_env_file)

    @classmethod
    def create_test_entity(cls):
        url     = f'{cls.base_path_entity}/{cls.namespace}/entity/create'
        payload = {'cache_key': f'test/data/{Random_Guid()}'}
        response = cls.client.post(url, json=payload)
        return response.json()['cache_id']

    def unique_file_id(self, prefix: str = 'file') -> str:
        return f'{prefix}-{Random_Guid()[:8]}'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Store String Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_data__store_string(self):
        data_key     = 'test'
        data_file_id = self.unique_file_id('string')
        url          = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/store/string/{data_key}/{data_file_id}'
        payload      = {'content': 'Hello, World!'}

        response = self.client.post(url, json=payload)

        assert response.status_code == 200
        result = response.json()
        assert result['data_key']  == data_key
        assert result['data_type'] == 'string'

    def test_data__store_string__nested_path(self):
        data_key     = 'level1/level2/level3'
        data_file_id = self.unique_file_id('nested')
        url          = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/store/string/{data_key}/{data_file_id}'
        payload      = {'content': 'Nested content'}

        response = self.client.post(url, json=payload)

        assert response.status_code == 200
        result = response.json()
        assert result['data_key'] == data_key

    # ═══════════════════════════════════════════════════════════════════════════════
    # Store JSON Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_data__store_json(self):
        data_key     = 'test'
        data_file_id = self.unique_file_id('json')
        url          = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/store/json/{data_key}/{data_file_id}'
        payload      = {'content': {'key': 'value', 'num': 42}}

        response = self.client.post(url, json=payload)

        assert response.status_code == 200
        result = response.json()
        assert result['data_key']  == data_key
        assert result['data_type'] == 'json'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get String Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_data__get_string(self):
        data_key     = 'test'
        data_file_id = self.unique_file_id('get-str')
        content      = 'Get me back!'

        # Store first
        store_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/store/string/{data_key}/{data_file_id}'
        self.client.post(store_url, json={'content': content})

        # Get
        get_url  = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/string/{data_key}/{data_file_id}'
        response = self.client.get(get_url)

        assert response.status_code == 200
        assert response.json() == content

    def test_data__get_string__not_found(self):
        url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/string/nonexistent/missing'

        response = self.client.get(url)

        assert response.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get JSON Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_data__get_json(self):
        data_key     = 'test'
        data_file_id = self.unique_file_id('get-json')
        content      = {'key': 'value', 'nested': {'a': 1}}

        # Store first
        store_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/store/json/{data_key}/{data_file_id}'
        self.client.post(store_url, json={'content': content})

        # Get
        get_url  = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/json/{data_key}/{data_file_id}'
        response = self.client.get(get_url)

        assert response.status_code == 200
        assert response.json() == content

    def test_data__get_json__not_found(self):
        url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/json/nonexistent/missing'

        response = self.client.get(url)

        assert response.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════════
    # Update Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_data__update_string(self):
        data_key     = 'test'
        data_file_id = self.unique_file_id('update-str')

        # Store original
        store_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/store/string/{data_key}/{data_file_id}'
        self.client.post(store_url, json={'content': 'Original'})

        # Update
        update_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/string/{data_key}/{data_file_id}'
        response   = self.client.put(update_url, json={'content': 'Updated'})

        assert response.status_code == 200
        result = response.json()
        assert result['success'] is True

        # Verify updated
        get_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/string/{data_key}/{data_file_id}'
        get_response = self.client.get(get_url)
        assert get_response.json() == 'Updated'

    def test_data__update_json(self):
        data_key     = 'test'
        data_file_id = self.unique_file_id('update-json')

        # Store original
        store_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/store/json/{data_key}/{data_file_id}'
        self.client.post(store_url, json={'content': {'version': 1}})

        # Update
        update_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/json/{data_key}/{data_file_id}'
        response   = self.client.put(update_url, json={'content': {'version': 2}})

        assert response.status_code == 200
        result = response.json()
        assert result['success'] is True

        # Verify updated
        get_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/json/{data_key}/{data_file_id}'
        get_response = self.client.get(get_url)
        assert get_response.json() == {'version': 2}

    # ═══════════════════════════════════════════════════════════════════════════════
    # Exists Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_data__exists__true(self):
        data_key     = 'test'
        data_file_id = self.unique_file_id('exists')

        # Store first
        store_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/store/string/{data_key}/{data_file_id}'
        self.client.post(store_url, json={'content': 'Exists test'})

        # Check exists
        exists_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/exists/string/{data_key}/{data_file_id}'
        response   = self.client.get(exists_url)

        assert response.status_code == 200
        assert response.json()['exists'] is True

    def test_data__exists__false(self):
        exists_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/exists/string/nonexistent/missing'

        response = self.client.get(exists_url)

        assert response.status_code == 200
        assert response.json()['exists'] is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Delete Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_data__delete(self):
        data_key     = 'test'
        data_file_id = self.unique_file_id('delete')

        # Store first
        store_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/store/string/{data_key}/{data_file_id}'
        self.client.post(store_url, json={'content': 'Delete me'})

        # Verify exists
        exists_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/exists/string/{data_key}/{data_file_id}'
        assert self.client.get(exists_url).json()['exists'] is True

        # Delete
        delete_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/string/{data_key}/{data_file_id}'
        response   = self.client.delete(delete_url)

        assert response.status_code == 200
        result = response.json()
        assert result['success'] is True
        assert result['deleted'] is True

        # Verify gone
        assert self.client.get(exists_url).json()['exists'] is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # List Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_data__list(self):
        # Store some data first
        data_file_id = self.unique_file_id('list')
        store_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/store/string/list-test/{data_file_id}'
        self.client.post(store_url, json={'content': 'List test content'})

        # List files
        list_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/'
        response = self.client.get(list_url)

        assert response.status_code == 200
        result = response.json()
        assert 'files' in result

    def test_data__paths(self):
        # Store some data first
        data_file_id = self.unique_file_id('paths')
        store_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/store/string/paths-test/{data_file_id}'
        self.client.post(store_url, json={'content': 'Paths test content'})

        # Get paths
        paths_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/paths'
        response  = self.client.get(paths_url)

        assert response.status_code == 200
        result = response.json()
        assert 'file_paths' in result

    # ═══════════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_full_data_workflow(self):
        data_key     = 'workflow'
        data_file_id = self.unique_file_id('full')
        content      = 'Full workflow content'

        # 1. Store string
        store_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/store/string/{data_key}/{data_file_id}'
        store_response = self.client.post(store_url, json={'content': content})

        assert store_response.status_code == 200

        # 2. Get string
        get_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/string/{data_key}/{data_file_id}'
        get_response = self.client.get(get_url)

        assert get_response.status_code == 200
        assert get_response.json() == content

        # 3. Update string
        new_content = 'Updated workflow content'
        update_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/string/{data_key}/{data_file_id}'
        update_response = self.client.put(update_url, json={'content': new_content})

        assert update_response.status_code == 200
        assert update_response.json()['success'] is True

        # 4. Verify updated
        verify_response = self.client.get(get_url)
        assert verify_response.json() == new_content

        # 5. Check exists
        exists_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/exists/string/{data_key}/{data_file_id}'
        exists_response = self.client.get(exists_url)

        assert exists_response.json()['exists'] is True

        # 6. Delete
        delete_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/string/{data_key}/{data_file_id}'
        delete_response = self.client.delete(delete_url)

        assert delete_response.json()['deleted'] is True

        # 7. Verify gone
        exists_after = self.client.get(exists_url)
        assert exists_after.json()['exists'] is False

        get_after = self.client.get(get_url)
        assert get_after.status_code == 404

    def test_string_and_json_in_same_entity(self):
        data_key = 'mixed'

        # Store string
        str_file_id = self.unique_file_id('str')
        str_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/store/string/{data_key}/{str_file_id}'
        self.client.post(str_url, json={'content': 'String content'})

        # Store JSON
        json_file_id = self.unique_file_id('json')
        json_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/store/json/{data_key}/{json_file_id}'
        self.client.post(json_url, json={'content': {'type': 'json'}})

        # Get both
        get_str_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/string/{data_key}/{str_file_id}'
        get_json_url = f'{self.base_path_data}/{self.namespace}/data/{self.cache_id}/json/{data_key}/{json_file_id}'

        str_response = self.client.get(get_str_url)
        json_response = self.client.get(get_json_url)

        assert str_response.json() == 'String content'
        assert json_response.json() == {'type': 'json'}
