# ═══════════════════════════════════════════════════════════════════════════════
# test_Routes__FLeT__Html__Execute__client - HTTP client tests for FLeT HTML execution routes
# Tests REST API calls: POST via FastAPI test client
# ═══════════════════════════════════════════════════════════════════════════════

import pytest
from unittest                                                                               import TestCase
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid                       import Random_Guid
from osbot_utils.utils.Files                                                                import path_combine
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                    import setup__html_graph_service__fast_api_test_objs, unload_local_dotenv
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                    import load_local_dotenv
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                    import TEST_API_KEY__NAME, TEST_API_KEY__VALUE


class test_Routes__FLeT__Html__Execute__client(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dot_env_file = path_combine(__file__, '../.local-cache.env')
        if load_local_dotenv(cls.dot_env_file) is False:
            pytest.skip('test needs local env vars set')


        with setup__html_graph_service__fast_api_test_objs() as _:
            cls.client = _.fast_api__client
            cls.client.headers[TEST_API_KEY__NAME] = TEST_API_KEY__VALUE

        cls.namespace        = 'test-routes-flet-html-execute-client'
        cls.base_path_exec   = '/flet-html-execute'
        cls.base_path_entity = '/cache-entity'
        cls.cache_id         = cls.create_test_entity()

    @classmethod
    def tearDownClass(cls):
        assert unload_local_dotenv(cls.dot_env_file)


    @classmethod
    def create_test_entity(cls):
        url     = f'{cls.base_path_entity}/{cls.namespace}/entity/create'
        payload = {'cache_key': f'test/flet/execute-{Random_Guid()}'}
        response = cls.client.post(url, json=payload)
        return response.json()['cache_id']

    def create_new_entity(self, suffix: str = '') -> str:
        url     = f'{self.base_path_entity}/{self.namespace}/entity/create'
        payload = {'cache_key': f'test/flet/execute-{suffix}-{Random_Guid()}'}
        response = self.client.post(url, json=payload)
        return response.json()['cache_id']

    def sample_html(self, content: str = 'Test') -> str:
        return f'<html><body><h1>{content}</h1></body></html>'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Html-To-Cache Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_html__to__cache(self):
        html    = self.sample_html('Store Test')
        url     = f'{self.base_path_exec}/html/to/cache/{self.namespace}/{self.cache_id}'
        payload = {'html': html}

        response = self.client.post(url, json=payload)

        assert response.status_code == 200
        result = response.json()
        assert result['success']      is True
        assert result['cache_id']     == self.cache_id
        assert result['char_count']   == len(html)
        assert result['data_key']     == 'html'
        assert result['data_file_id'] == 'raw'
        assert result['flow_saved']   is True

    def test_html__to__cache__custom_location(self):
        cache_id = self.create_new_entity('custom-loc')
        html     = self.sample_html('Custom Location')
        url      = f'{self.base_path_exec}/html/to/cache/{self.namespace}/{cache_id}'
        payload  = {'html': html, 'data_key': 'custom', 'data_file_id': 'v1'}

        response = self.client.post(url, json=payload)

        assert response.status_code == 200
        result = response.json()
        assert result['success']      is True
        assert result['data_key']     == 'custom'
        assert result['data_file_id'] == 'v1'

    def test_html__to__cache__empty_html(self):
        url     = f'{self.base_path_exec}/html/to/cache/{self.namespace}/{self.cache_id}'
        payload = {'html': ''}

        response = self.client.post(url, json=payload)

        assert response.status_code == 200
        result = response.json()
        assert result['success'] is False

    def test_html__to__cache__entity_not_found(self):
        fake_cache_id = str(Random_Guid())
        url     = f'{self.base_path_exec}/html/to/cache/{self.namespace}/{fake_cache_id}'
        payload = {'html': '<p>test</p>'}

        response = self.client.post(url, json=payload)

        assert response.status_code == 404

    def test_html__to__cache__large_html(self):
        cache_id = self.create_new_entity('large')
        html     = '<html><body>' + '<p>Large content paragraph</p>' * 500 + '</body></html>'
        url      = f'{self.base_path_exec}/html/to/cache/{self.namespace}/{cache_id}'
        payload  = {'html': html}

        response = self.client.post(url, json=payload)

        assert response.status_code == 200
        result = response.json()
        assert result['success']    is True
        assert result['char_count'] == len(html)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Html-From-Cache Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_html__from__cache(self):
        cache_id = self.create_new_entity('from-cache')
        html     = self.sample_html('Retrieve Me')

        # Store first
        store_url = f'{self.base_path_exec}/html/to/cache/{self.namespace}/{cache_id}'
        self.client.post(store_url, json={'html': html})

        # Retrieve
        retrieve_url = f'{self.base_path_exec}/html/from/cache/{self.namespace}/{cache_id}'
        response     = self.client.post(retrieve_url, json={})

        assert response.status_code == 200
        result = response.json()
        assert result['success']    is True
        assert result['cache_id']   == cache_id
        assert result['found']      is True
        assert result['html']       == html
        assert result['char_count'] == len(html)
        assert result['flow_saved'] is True

    def test_html__from__cache__custom_location(self):
        cache_id = self.create_new_entity('custom-retrieve')
        html     = self.sample_html('Custom Retrieve')

        # Store at custom location
        store_url = f'{self.base_path_exec}/html/to/cache/{self.namespace}/{cache_id}'
        self.client.post(store_url, json={'html': html, 'data_key': 'custom', 'data_file_id': 'special'})

        # Retrieve from custom location
        retrieve_url = f'{self.base_path_exec}/html/from/cache/{self.namespace}/{cache_id}'
        response     = self.client.post(retrieve_url, json={'data_key': 'custom', 'data_file_id': 'special'})

        assert response.status_code == 200
        result = response.json()
        assert result['success'] is True
        assert result['html']    == html

    def test_html__from__cache__not_found(self):
        cache_id     = self.create_new_entity('not-found')
        retrieve_url = f'{self.base_path_exec}/html/from/cache/{self.namespace}/{cache_id}'

        response = self.client.post(retrieve_url, json={'data_key': 'nonexistent', 'data_file_id': 'missing'})

        assert response.status_code == 200
        result = response.json()
        assert result['success'] is True
        assert result['found']   is False

    def test_html__from__cache__entity_not_found(self):
        fake_cache_id = str(Random_Guid())
        url = f'{self.base_path_exec}/html/from/cache/{self.namespace}/{fake_cache_id}'

        response = self.client.post(url, json={})

        assert response.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════════
    # Round-Trip Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_round_trip__store_and_retrieve(self):
        cache_id = self.create_new_entity('roundtrip')
        original_html = '''<!DOCTYPE html>
<html>
<head><title>Round Trip Test</title></head>
<body>
    <h1>Hello World</h1>
    <p>This is a round-trip test.</p>
</body>
</html>'''

        # Store
        store_url = f'{self.base_path_exec}/html/to/cache/{self.namespace}/{cache_id}'
        store_response = self.client.post(store_url, json={'html': original_html})

        assert store_response.status_code == 200
        assert store_response.json()['success'] is True

        # Retrieve
        retrieve_url = f'{self.base_path_exec}/html/from/cache/{self.namespace}/{cache_id}'
        retrieve_response = self.client.post(retrieve_url, json={})

        assert retrieve_response.status_code == 200
        result = retrieve_response.json()
        assert result['success'] is True
        assert result['found']   is True
        assert result['html']    == original_html

    def test_multiple_data_locations(self):
        cache_id = self.create_new_entity('multi-loc')
        html_v1  = '<p>Version 1</p>'
        html_v2  = '<p>Version 2</p>'

        store_url = f'{self.base_path_exec}/html/to/cache/{self.namespace}/{cache_id}'

        # Store v1 at default location
        self.client.post(store_url, json={'html': html_v1})

        # Store v2 at custom location
        self.client.post(store_url, json={'html': html_v2, 'data_key': 'html', 'data_file_id': 'v2'})

        retrieve_url = f'{self.base_path_exec}/html/from/cache/{self.namespace}/{cache_id}'

        # Retrieve v1 (default)
        response_v1 = self.client.post(retrieve_url, json={})
        assert response_v1.json()['html'] == html_v1

        # Retrieve v2 (custom)
        response_v2 = self.client.post(retrieve_url, json={'data_key': 'html', 'data_file_id': 'v2'})
        assert response_v2.json()['html'] == html_v2

    # ═══════════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_full_execution_workflow(self):
        cache_id = self.create_new_entity('full-workflow')
        html     = self.sample_html(f'Full Workflow {Random_Guid()}')

        store_url    = f'{self.base_path_exec}/html/to/cache/{self.namespace}/{cache_id}'
        retrieve_url = f'{self.base_path_exec}/html/from/cache/{self.namespace}/{cache_id}'

        # 1. Store HTML
        store_response = self.client.post(store_url, json={'html': html})

        assert store_response.status_code == 200
        store_result = store_response.json()
        assert store_result['success']    is True
        assert store_result['flow_saved'] is True

        # 2. Retrieve HTML
        retrieve_response = self.client.post(retrieve_url, json={})

        assert retrieve_response.status_code == 200
        retrieve_result = retrieve_response.json()
        assert retrieve_result['success']    is True
        assert retrieve_result['found']      is True
        assert retrieve_result['html']       == html
        assert retrieve_result['flow_saved'] is True

        # 3. Store at different location
        html_alt = self.sample_html('Alternative Version')
        alt_response = self.client.post(store_url, json={
            'html': html_alt,
            'data_key': 'html/versions',
            'data_file_id': 'alt'
        })

        assert alt_response.status_code == 200
        assert alt_response.json()['data_key'] == 'html/versions'

        # 4. Retrieve from different location
        alt_retrieve = self.client.post(retrieve_url, json={
            'data_key': 'html/versions',
            'data_file_id': 'alt'
        })

        assert alt_retrieve.json()['html'] == html_alt

        # 5. Original still intact
        original_retrieve = self.client.post(retrieve_url, json={})
        assert original_retrieve.json()['html'] == html

    def test_overwrite_same_location(self):
        cache_id = self.create_new_entity('overwrite')
        html_v1  = self.sample_html('Version 1')
        html_v2  = self.sample_html('Version 2')

        store_url    = f'{self.base_path_exec}/html/to/cache/{self.namespace}/{cache_id}'
        retrieve_url = f'{self.base_path_exec}/html/from/cache/{self.namespace}/{cache_id}'

        # Store v1
        self.client.post(store_url, json={'html': html_v1})

        # Verify v1
        response_1 = self.client.post(retrieve_url, json={})
        assert response_1.json()['html'] == html_v1

        # Overwrite with v2 (same location)
        self.client.post(store_url, json={'html': html_v2})

        # Verify v2 replaced v1
        response_2 = self.client.post(retrieve_url, json={})
        assert response_2.json()['html'] == html_v2