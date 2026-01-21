# ═══════════════════════════════════════════════════════════════════════════════
# test_Routes__Cache__Entity__client - HTTP client tests for cache entity routes
# Tests REST API calls: POST, GET, DELETE via FastAPI test client
# ═══════════════════════════════════════════════════════════════════════════════
import pytest
from unittest                                                                               import TestCase
from osbot_utils.testing.__                                                                 import __
from mgraph_ai_service_html_graph.schemas.cache.Schema__Route__Cache_Status__Response       import Schema__Route__Cache_Status__Response
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid                       import Random_Guid
from osbot_utils.utils.Files                                                                import path_combine
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                    import setup__html_graph_service__fast_api_test_objs, load_local_dotenv, unload_local_dotenv
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                    import TEST_API_KEY__NAME, TEST_API_KEY__VALUE


class test_Routes__Cache__Entity__client(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dot_env_file = path_combine(__file__, '../.local-cache.env')
        if load_local_dotenv(cls.dot_env_file) is False:
            pytest.skip('test needs local env vars set')
        with setup__html_graph_service__fast_api_test_objs() as _:
            cls.client    = _.fast_api__client
            cls.client.headers[TEST_API_KEY__NAME] = TEST_API_KEY__VALUE
        cls.namespace = 'test-routes-cache-entity-client'
        cls.base_path = '/cache-entity'

    @classmethod
    def tearDownClass(cls):
        assert unload_local_dotenv(cls.dot_env_file)


    def cache_key(self, suffix: str = '') -> str:                                           # Generate unique cache key
        return f'test/client/{Random_Guid()}/{suffix}'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Cache config
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_cache_config(self):
        url       = f'{self.base_path}/cache/status'
        response  = self.client.get(url)

        cache_status = Schema__Route__Cache_Status__Response.from_json(response.json())
        assert response.status_code == 200
        assert cache_status.obj()   == __(cache_enabled = True                  ,
                                          health_check  = True                  ,
                                          target_server = 'http://0.0.0.0:10017')


    # ═══════════════════════════════════════════════════════════════════════════════
    # Create Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_entity__create(self):
        cache_key = self.cache_key('create')
        url       = f'{self.base_path}/{self.namespace}/entity/create'
        payload   = {'cache_key': cache_key, 'file_id': 'root'}
        response  = self.client.post(url, json=payload)

        assert response.status_code == 200
        result = response.json()
        assert result['success'   ] is True
        assert result['cache_id'  ] != ''
        assert result['cache_hash'] != ''

    def test_entity__create__duplicate_creates_new(self):
        cache_key = self.cache_key('duplicate')
        url       = f'{self.base_path}/{self.namespace}/entity/create'
        payload   = {'cache_key': cache_key}

        response1 = self.client.post(url, json=payload)
        response2 = self.client.post(url, json=payload)

        assert response1.status_code == 200
        assert response2.status_code == 200

        result1 = response1.json()
        result2 = response2.json()

        assert result1['cache_id']   != result2['cache_id']                                 # Different cache_ids
        assert result1['cache_hash'] == result2['cache_hash']                               # Same cache_hash

    def test_entity__create__empty_cache_key(self):
        url     = f'{self.base_path}/{self.namespace}/entity/create'
        payload = {'cache_key': ''}

        response = self.client.post(url, json=payload)

        assert response.status_code == 200
        result = response.json()
        assert result['success'] is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Lookup Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_entity__lookup__by_cache_key(self):
        cache_key = self.cache_key('lookup')

        # Create first
        create_url = f'{self.base_path}/{self.namespace}/entity/create'
        create_response = self.client.post(create_url, json={'cache_key': cache_key})
        created = create_response.json()

        # Lookup
        lookup_url = f'{self.base_path}/{self.namespace}/entity/lookup'
        lookup_response = self.client.post(lookup_url, json={'cache_key': cache_key})

        assert lookup_response.status_code == 200
        result = lookup_response.json()
        assert result['success']  is True
        assert result['found']    is True
        assert result['cache_id'] == created['cache_id']

    def test_entity__lookup__not_found(self):
        url     = f'{self.base_path}/{self.namespace}/entity/lookup'
        payload = {'cache_key': f'nonexistent/{Random_Guid()}'}

        response = self.client.post(url, json=payload)

        assert response.status_code == 200
        result = response.json()
        assert result['success']  is True
        assert result['found']    is False
        assert result['cache_id'] == ''

    def test_entity__lookup__empty_request(self):
        url = f'{self.base_path}/{self.namespace}/entity/lookup'

        response = self.client.post(url, json={})

        assert response.status_code == 200
        result = response.json()
        assert result['success'] is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # List By Path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_entity__list_by_path(self):
        base_path = f'test/client-list/{Random_Guid()[:8]}'

        # Create some entities
        create_url = f'{self.base_path}/{self.namespace}/entity/create'
        self.client.post(create_url, json={'cache_key': f'{base_path}/item-1'})
        self.client.post(create_url, json={'cache_key': f'{base_path}/item-2'})
        self.client.post(create_url, json={'cache_key': f'{base_path}/item-3'})

        # List
        list_url = f'{self.base_path}/{self.namespace}/entities/list/{base_path}'
        response = self.client.get(list_url)

        assert response.status_code == 200
        result = response.json()
        assert result['success']     is True
        assert result['namespace']   == self.namespace
        assert result['path_prefix'] == base_path
        assert result['count']       == 3
        assert result                == { 'count': 3,
                                          'entities': ['item-1', 'item-2', 'item-3'],
                                          'namespace': 'test-routes-cache-entity-client',
                                          'path_prefix': base_path,
                                          'success': True}


    def test_entity__list_by_path__empty(self):
        empty_path = f'test/client-empty/{Random_Guid()}'

        list_url = f'{self.base_path}/{self.namespace}/entities/list/{empty_path}'
        response = self.client.get(list_url)

        assert response.status_code == 200
        result = response.json()
        assert result['success'] is True
        assert result['count']   == 0
        assert result['entities'] == []

    def test_entity__list_by_path__drill_down(self):
        base_path = f'test/client-drill/{Random_Guid()[:8]}'

        # Create nested structure
        create_url = f'{self.base_path}/{self.namespace}/entity/create'
        self.client.post(create_url, json={'cache_key': f'{base_path}/sites/example.com/page1'})
        self.client.post(create_url, json={'cache_key': f'{base_path}/sites/example.com/page2'})
        self.client.post(create_url, json={'cache_key': f'{base_path}/sites/other.com/index'})

        # List at base
        response_1 = self.client.get(f'{self.base_path}/{self.namespace}/entities/list/{base_path}')
        assert response_1.json()['entities'] == ['sites']

        # Drill into sites
        response_2 = self.client.get(f'{self.base_path}/{self.namespace}/entities/list/{base_path}/sites')
        result_2 = response_2.json()
        assert result_2['count'] == 2
        assert 'example_com' in result_2['entities']
        assert 'other_com'   in result_2['entities']

        # Drill into example.com
        response_3 = self.client.get(f'{self.base_path}/{self.namespace}/entities/list/{base_path}/sites/example.com')
        result_3 = response_3.json()
        assert result_3['count'] == 2
        assert 'page1' in result_3['entities']
        assert 'page2' in result_3['entities']
    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_entity__get(self):
        cache_key = self.cache_key('get')

        # Create first
        create_url = f'{self.base_path}/{self.namespace}/entity/create'
        create_response = self.client.post(create_url, json={'cache_key': cache_key})
        cache_id = create_response.json()['cache_id']

        # Get
        get_url  = f'{self.base_path}/{self.namespace}/entity/{cache_id}'
        response = self.client.get(get_url)

        assert response.status_code == 200
        result = response.json()
        assert result == {'cache_key': cache_key}

    def test_entity__get__not_found(self):
        fake_cache_id = Random_Guid()
        url = f'{self.base_path}/{self.namespace}/entity/{fake_cache_id}'

        response = self.client.get(url)

        assert response.status_code == 404
        assert 'not found' in response.json()['detail'].lower()

    def test_entity__metadata(self):
        cache_key = self.cache_key('metadata')

        # Create first
        create_url = f'{self.base_path}/{self.namespace}/entity/create'
        create_response = self.client.post(create_url, json={'cache_key': cache_key})
        cache_id = create_response.json()['cache_id']

        # Get metadata
        url      = f'{self.base_path}/{self.namespace}/entity/{cache_id}/metadata'
        response = self.client.get(url)

        assert response.status_code == 200
        result = response.json()
        assert 'data' in result
        assert result['data']['cache_id'] == cache_id

    def test_entity__metadata__not_found(self):
        fake_cache_id = Random_Guid()
        url = f'{self.base_path}/{self.namespace}/entity/{fake_cache_id}/metadata'

        response = self.client.get(url)

        assert response.status_code == 404

    def test_entity__refs(self):
        cache_key = self.cache_key('refs')

        # Create first
        create_url = f'{self.base_path}/{self.namespace}/entity/create'
        create_response = self.client.post(create_url, json={'cache_key': cache_key})
        cache_id = create_response.json()['cache_id']

        # Get refs
        url      = f'{self.base_path}/{self.namespace}/entity/{cache_id}/refs'
        response = self.client.get(url)

        assert response.status_code == 200
        result = response.json()
        assert 'all_paths' in result

    def test_entity__refs__not_found(self):
        fake_cache_id = Random_Guid()
        url = f'{self.base_path}/{self.namespace}/entity/{fake_cache_id}/refs'

        response = self.client.get(url)

        assert response.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════════
    # Exists Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_entity__exists__true(self):
        cache_key = self.cache_key('exists-true')

        # Create first
        create_url = f'{self.base_path}/{self.namespace}/entity/create'
        create_response = self.client.post(create_url, json={'cache_key': cache_key})
        cache_id = create_response.json()['cache_id']

        # Check exists
        url      = f'{self.base_path}/{self.namespace}/entity/{cache_id}/exists'
        response = self.client.get(url)

        assert response.status_code == 200
        result = response.json()
        assert result['exists'] is True

    def test_entity__exists__false(self):
        fake_cache_id = Random_Guid()
        url = f'{self.base_path}/{self.namespace}/entity/{fake_cache_id}/exists'

        response = self.client.get(url)

        assert response.status_code == 200
        result = response.json()
        assert result['exists'] is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Delete Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_entity__delete(self):
        cache_key = self.cache_key('delete')

        # Create first
        create_url = f'{self.base_path}/{self.namespace}/entity/create'
        create_response = self.client.post(create_url, json={'cache_key': cache_key})
        cache_id = create_response.json()['cache_id']

        # Verify exists
        exists_url = f'{self.base_path}/{self.namespace}/entity/{cache_id}/exists'
        assert self.client.get(exists_url).json()['exists'] is True

        # Delete
        delete_url = f'{self.base_path}/{self.namespace}/entity/{cache_id}'
        response   = self.client.delete(delete_url)

        assert response.status_code == 200
        result = response.json()
        assert result['success'] is True
        assert result['deleted'] is True

        # Verify gone
        assert self.client.get(exists_url).json()['exists'] is False

    def test_entity__delete__not_found(self):
        fake_cache_id = Random_Guid()
        url = f'{self.base_path}/{self.namespace}/entity/{fake_cache_id}'

        response = self.client.delete(url)

        assert response.status_code == 200
        result = response.json()
        assert result['success'] is True
        assert result['deleted'] is False                                                   # Nothing to delete

    # ═══════════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_full_entity_workflow(self):
        cache_key = self.cache_key('workflow')

        # 1. Create
        create_url = f'{self.base_path}/{self.namespace}/entity/create'
        create_response = self.client.post(create_url, json={'cache_key': cache_key})

        assert create_response.status_code == 200
        created = create_response.json()
        assert created['success'] is True
        cache_id = created['cache_id']

        # 2. Lookup
        lookup_url = f'{self.base_path}/{self.namespace}/entity/lookup'
        lookup_response = self.client.post(lookup_url, json={'cache_key': cache_key})

        assert lookup_response.status_code == 200
        lookup = lookup_response.json()
        assert lookup['found']    is True
        assert lookup['cache_id'] == cache_id

        # 3. Get
        get_url = f'{self.base_path}/{self.namespace}/entity/{cache_id}'
        get_response = self.client.get(get_url)

        assert get_response.status_code == 200
        entity = get_response.json()
        assert entity == {'cache_key': cache_key}

        # 4. Get metadata
        metadata_url = f'{self.base_path}/{self.namespace}/entity/{cache_id}/metadata'
        metadata_response = self.client.get(metadata_url)

        assert metadata_response.status_code == 200

        # 5. Get refs
        refs_url = f'{self.base_path}/{self.namespace}/entity/{cache_id}/refs'
        refs_response = self.client.get(refs_url)

        assert refs_response.status_code == 200

        # 6. Exists
        exists_url = f'{self.base_path}/{self.namespace}/entity/{cache_id}/exists'
        exists_response = self.client.get(exists_url)

        assert exists_response.status_code == 200
        assert exists_response.json()['exists'] is True

        # 7. Delete
        delete_url = f'{self.base_path}/{self.namespace}/entity/{cache_id}'
        delete_response = self.client.delete(delete_url)

        assert delete_response.status_code == 200
        assert delete_response.json()['deleted'] is True

        # 8. Verify gone
        exists_after = self.client.get(exists_url)
        assert exists_after.json()['exists'] is False

        get_after = self.client.get(get_url)
        assert get_after.status_code == 404
