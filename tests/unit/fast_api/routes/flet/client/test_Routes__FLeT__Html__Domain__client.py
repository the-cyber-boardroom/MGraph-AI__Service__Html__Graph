# ═══════════════════════════════════════════════════════════════════════════════
# test_Routes__FLeT__Html__Domain__client - HTTP client tests for domain-level HTML routes
# Tests REST API calls for store/load operations via FastAPI test client
# ═══════════════════════════════════════════════════════════════════════════════

import pytest
from unittest                                                                               import TestCase
from osbot_utils.utils.Files                                                                import path_combine
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid                       import Random_Guid
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                    import setup__html_graph_service__fast_api_test_objs, unload_local_dotenv
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                    import load_local_dotenv
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                    import TEST_API_KEY__NAME, TEST_API_KEY__VALUE


class test_Routes__FLeT__Html__Domain__client(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dot_env_file = path_combine(__file__, '../.local-cache.env')
        if load_local_dotenv(cls.dot_env_file) is False:
            pytest.skip('test needs local env vars set')

        with setup__html_graph_service__fast_api_test_objs() as _:
            cls.client = _.fast_api__client
            cls.client.headers[TEST_API_KEY__NAME] = TEST_API_KEY__VALUE

        cls.namespace = 'test-routes-flet-html-domain-client'
        cls.base_path = '/flet-html-domain'

    @classmethod
    def tearDownClass(cls):
        assert unload_local_dotenv(cls.dot_env_file)


    def cache_key(self, suffix: str = '') -> str:                                           # Generate unique cache key
        return f'test/client/{Random_Guid()}/{suffix}'

    def sample_html(self, content: str = 'Test') -> str:                                    # Generate sample HTML
        return f'<html><body><h1>{content}</h1></body></html>'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Store Raw Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_store__raw(self):
        html    = self.sample_html('Store Raw Test')
        url     = f'{self.base_path}/html/store/{self.namespace}/raw'
        payload = {'html': html}

        response = self.client.post(url, json=payload)


        assert response.status_code == 200
        result = response.json()
        assert result['success']    is True
        assert result['cache_id']   != ''
        assert result['cache_key']  != ''
        assert result['cache_hash'] != ''
        assert result['char_count'] == len(html)

    def test_store__raw__creates_entity(self):
        html    = self.sample_html('Entity Creation Test')
        url     = f'{self.base_path}/html/store/{self.namespace}/raw'
        payload = {'html': html}

        response1 = self.client.post(url, json=payload)
        response2 = self.client.post(url, json=payload)

        assert response1.status_code == 200
        assert response2.status_code == 200

        result1 = response1.json()
        result2 = response2.json()

        # Same content = same entity reused
        assert result1['cache_id'] == result2['cache_id']

    def test_store__raw__empty_html(self):
        url     = f'{self.base_path}/html/store/{self.namespace}/raw'
        payload = {'html': ''}

        response = self.client.post(url, json=payload)

        assert response.status_code == 200
        result = response.json()
        assert result['success'] is False

    def test_store__raw__large_html(self):
        html    = '<html><body>' + '<p>Paragraph</p>' * 1000 + '</body></html>'
        url     = f'{self.base_path}/html/store/{self.namespace}/raw'
        payload = {'html': html}

        response = self.client.post(url, json=payload)

        assert response.status_code == 200
        result = response.json()
        assert result['success']    is True
        assert result['char_count'] == len(html)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Store with Key Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_store__key(self):
        html      = self.sample_html('Store with Key Test')
        cache_key = self.cache_key('store-key')
        url       = f'{self.base_path}/html/store/{self.namespace}/key/{cache_key}'
        payload   = {'html': html}

        response = self.client.post(url, json=payload)

        assert response.status_code == 200
        result = response.json()
        assert result['success']    is True
        assert result['cache_key']  == cache_key
        assert result['char_count'] == len(html)

    def test_store__key__nested_path(self):
        html      = self.sample_html('Nested Path Test')
        cache_key = f'level1/level2/level3/{Random_Guid()}'
        url       = f'{self.base_path}/html/store/{self.namespace}/key/{cache_key}'
        payload   = {'html': html}

        response = self.client.post(url, json=payload)

        assert response.status_code == 200
        result = response.json()
        assert result['success']   is True
        assert result['cache_key'] == cache_key

    def test_store__key__empty_html(self):
        cache_key = self.cache_key('empty-html')
        url       = f'{self.base_path}/html/store/{self.namespace}/key/{cache_key}'
        payload   = {'html': ''}

        response = self.client.post(url, json=payload)

        assert response.status_code == 200
        result = response.json()
        assert result['success'] is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Load by ID Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_load__id(self):
        html = self.sample_html('Load by ID Test')

        # Store first
        store_url = f'{self.base_path}/html/store/{self.namespace}/raw'
        store_response = self.client.post(store_url, json={'html': html})
        cache_id = store_response.json()['cache_id']

        # Load by ID
        load_url = f'{self.base_path}/html/load/{self.namespace}/id'
        load_response = self.client.post(load_url, json={'cache_id': cache_id})

        assert load_response.status_code == 200
        result = load_response.json()
        assert result['success']    is True
        assert result['found']      is True
        assert result['html']       == html
        assert result['cache_id']   == cache_id
        assert result['char_count'] == len(html)

    def test_load__id__not_found(self):
        fake_cache_id = str(Random_Guid())
        url = f'{self.base_path}/html/load/{self.namespace}/id'

        response = self.client.post(url, json={'cache_id': fake_cache_id})

        # Returns 500 because entity doesn't exist
        assert response.status_code == 500

    def test_load__id__empty_id(self):
        url = f'{self.base_path}/html/load/{self.namespace}/id'

        response = self.client.post(url, json={'cache_id': ''})

        assert response.status_code == 404
        assert response.json() == {'detail': 'Entity not found: '}

    # ═══════════════════════════════════════════════════════════════════════════════
    # Load by Key Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_load__key(self):
        html      = self.sample_html('Load by Key Test')
        cache_key = self.cache_key('load-key')

        # Store first
        store_url = f'{self.base_path}/html/store/{self.namespace}/key/{cache_key}'
        self.client.post(store_url, json={'html': html})

        # Load by key
        load_url = f'{self.base_path}/html/load/{self.namespace}/key/{cache_key}'
        load_response = self.client.post(load_url)

        assert load_response.status_code == 200
        result = load_response.json()
        assert result['success']   is True
        assert result['found']     is True
        assert result['html']      == html
        assert result['cache_key'] == cache_key

    def test_load__key__not_found(self):
        cache_key = f'nonexistent/{Random_Guid()}'
        url = f'{self.base_path}/html/load/{self.namespace}/key/{cache_key}'

        response = self.client.post(url)

        assert response.status_code == 200
        result = response.json()
        assert result['success'] is True
        assert result['found']   is False

    def test_load__key__nested_path(self):
        html      = self.sample_html('Nested Load Test')
        cache_key = f'deep/nested/path/{Random_Guid()}'

        # Store first
        store_url = f'{self.base_path}/html/store/{self.namespace}/key/{cache_key}'
        self.client.post(store_url, json={'html': html})

        # Load by key
        load_url = f'{self.base_path}/html/load/{self.namespace}/key/{cache_key}'
        load_response = self.client.post(load_url)

        assert load_response.status_code == 200
        result = load_response.json()
        assert result['found'] is True
        assert result['html']  == html

    # ═══════════════════════════════════════════════════════════════════════════════
    # Load by Hash Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_load__hash(self):
        html = self.sample_html(f'Load by Hash Test {Random_Guid()}')

        # Store first
        store_url = f'{self.base_path}/html/store/{self.namespace}/raw'
        store_response = self.client.post(store_url, json={'html': html})
        cache_hash = store_response.json()['cache_hash']

        # Load by hash
        load_url = f'{self.base_path}/html/load/{self.namespace}/hash'
        load_response = self.client.post(load_url, json={'cache_hash': cache_hash})

        assert load_response.status_code == 200
        result = load_response.json()
        assert result['success'] is True
        assert result['found']   is True
        assert result['html']    == html

    def test_load__hash__not_found(self):
        url = f'{self.base_path}/html/load/{self.namespace}/hash'

        response = self.client.post(url, json={'cache_hash': 'aaaaa12345'})

        assert response.status_code == 200
        result = response.json()
        assert result['success'] is True
        assert result['found']   is False

    def test_load__hash__empty_hash(self):
        url = f'{self.base_path}/html/load/{self.namespace}/hash'

        response = self.client.post(url, json={'cache_hash': ''})

        assert response.status_code == 200
        result = response.json()
        assert result['found'] is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Round-Trip Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_round_trip__store_raw_load_by_id(self):
        html = self.sample_html(f'Round Trip ID {Random_Guid()}')

        # Store
        store_url = f'{self.base_path}/html/store/{self.namespace}/raw'
        store_response = self.client.post(store_url, json={'html': html})

        assert store_response.status_code == 200
        cache_id = store_response.json()['cache_id']

        # Load
        load_url = f'{self.base_path}/html/load/{self.namespace}/id'
        load_response = self.client.post(load_url, json={'cache_id': cache_id})

        assert load_response.status_code == 200
        assert load_response.json()['html'] == html

    def test_round_trip__store_key_load_key(self):
        html      = self.sample_html(f'Round Trip Key {Random_Guid()}')
        cache_key = self.cache_key('round-trip-key')

        # Store
        store_url = f'{self.base_path}/html/store/{self.namespace}/key/{cache_key}'
        store_response = self.client.post(store_url, json={'html': html})

        assert store_response.status_code == 200

        # Load
        load_url = f'{self.base_path}/html/load/{self.namespace}/key/{cache_key}'
        load_response = self.client.post(load_url)

        assert load_response.status_code == 200
        assert load_response.json()['html'] == html

    def test_round_trip__store_raw_load_by_hash(self):
        html = self.sample_html(f'Round Trip Hash {Random_Guid()}')

        # Store
        store_url = f'{self.base_path}/html/store/{self.namespace}/raw'
        store_response = self.client.post(store_url, json={'html': html})

        assert store_response.status_code == 200
        cache_hash = store_response.json()['cache_hash']

        # Load
        load_url = f'{self.base_path}/html/load/{self.namespace}/hash'
        load_response = self.client.post(load_url, json={'cache_hash': cache_hash})

        assert load_response.status_code == 200
        assert load_response.json()['html'] == html

    # ═══════════════════════════════════════════════════════════════════════════════
    # Entity Reuse Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_store_reuses_entity_by_key(self):
        cache_key = self.cache_key('entity-reuse')
        html_v1   = self.sample_html('Version 1')
        html_v2   = self.sample_html('Version 2')

        # Store v1
        store_url = f'{self.base_path}/html/store/{self.namespace}/key/{cache_key}'
        response1 = self.client.post(store_url, json={'html': html_v1})

        # Store v2 (same key)
        response2 = self.client.post(store_url, json={'html': html_v2})

        assert response1.status_code == 200
        assert response2.status_code == 200

        result1 = response1.json()
        result2 = response2.json()

        # Same cache_id (entity reused)
        assert result1['cache_id'] == result2['cache_id']

        # Load should return v2 (latest)
        load_url = f'{self.base_path}/html/load/{self.namespace}/key/{cache_key}'
        load_response = self.client.post(load_url)

        assert load_response.json()['html'] == html_v2

    def test_different_keys_create_different_entities(self):
        html = self.sample_html('Same Content')

        # Store with key1
        key1 = self.cache_key('entity-1')
        url1 = f'{self.base_path}/html/store/{self.namespace}/key/{key1}'
        response1 = self.client.post(url1, json={'html': html})

        # Store with key2
        key2 = self.cache_key('entity-2')
        url2 = f'{self.base_path}/html/store/{self.namespace}/key/{key2}'
        response2 = self.client.post(url2, json={'html': html})

        result1 = response1.json()
        result2 = response2.json()

        # Different keys = different entities
        assert result1['cache_id'] != result2['cache_id']

        # Different hashes = different keys
        assert result1['cache_hash'] != result2['cache_hash']

    # ═══════════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_full_workflow(self):
        cache_key = self.cache_key('full-workflow')
        html      = self.sample_html(f'Full Workflow {Random_Guid()}')

        # 1. Store with key
        store_url = f'{self.base_path}/html/store/{self.namespace}/key/{cache_key}'
        store_response = self.client.post(store_url, json={'html': html})

        assert store_response.status_code == 200
        stored = store_response.json()
        assert stored['success'] is True
        cache_id   = stored['cache_id']
        cache_hash = stored['cache_hash']

        # 2. Load by ID
        load_id_url = f'{self.base_path}/html/load/{self.namespace}/id'
        load_id_response = self.client.post(load_id_url, json={'cache_id': cache_id})

        assert load_id_response.status_code == 200
        assert load_id_response.json()['html'] == html

        # 3. Load by key
        load_key_url = f'{self.base_path}/html/load/{self.namespace}/key/{cache_key}'
        load_key_response = self.client.post(load_key_url)

        assert load_key_response.status_code == 200
        assert load_key_response.json()['html'] == html

        # 4. Load by hash
        load_hash_url = f'{self.base_path}/html/load/{self.namespace}/hash'
        load_hash_response = self.client.post(load_hash_url, json={'cache_hash': cache_hash})

        assert load_hash_response.status_code == 200
        assert load_hash_response.json()['html'] == html

        # 5. Update with same key (v2)
        html_v2 = self.sample_html(f'Full Workflow V2 {Random_Guid()}')
        update_response = self.client.post(store_url, json={'html': html_v2})

        assert update_response.status_code == 200
        assert update_response.json()['cache_id'] == cache_id                               # Same entity

        # 6. Load by key returns v2
        load_v2_response = self.client.post(load_key_url)

        assert load_v2_response.json()['html'] == html_v2

    def test_cross_namespace_isolation(self):
        html      = self.sample_html('Isolation Test')
        cache_key = self.cache_key('isolation')

        # Store in namespace A
        ns_a = f'{self.namespace}-a'
        store_url_a = f'{self.base_path}/html/store/{ns_a}/key/{cache_key}'
        self.client.post(store_url_a, json={'html': html})

        # Load from namespace B (should not find it)
        ns_b = f'{self.namespace}-b'
        load_url_b = f'{self.base_path}/html/load/{ns_b}/key/{cache_key}'
        load_response = self.client.post(load_url_b)

        assert load_response.status_code == 200
        assert load_response.json()['found'] is False

        # Load from namespace A (should find it)
        load_url_a = f'{self.base_path}/html/load/{ns_a}/key/{cache_key}'
        load_response_a = self.client.post(load_url_a)

        assert load_response_a.json()['found'] is True
        assert load_response_a.json()['html']  == html