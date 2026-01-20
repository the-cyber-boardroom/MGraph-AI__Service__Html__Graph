# ═══════════════════════════════════════════════════════════════════════════════
# test_Routes__FLeT__Flows__client - HTTP client tests for FLeT flow observability routes
# Tests REST API calls: GET via FastAPI test client
# ═══════════════════════════════════════════════════════════════════════════════

import pytest
from unittest                                                                               import TestCase
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid                       import Random_Guid
from osbot_utils.utils.Files                                                                import path_combine
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                    import setup__html_graph_service__fast_api_test_objs
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                    import load_local_dotenv
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                    import TEST_API_KEY__NAME, TEST_API_KEY__VALUE


class test_Routes__FLeT__Flows__client(TestCase):

    @classmethod
    def setUpClass(cls):
        dot_env_file = path_combine(__file__, '../.local-cache.env')
        if load_local_dotenv(dot_env_file) is False:
            pytest.skip('test needs local env vars set')

        with setup__html_graph_service__fast_api_test_objs() as _:
            cls.client = _.fast_api__client
            cls.client.headers[TEST_API_KEY__NAME] = TEST_API_KEY__VALUE

        cls.namespace        = 'test-routes-flet-flows-client'
        cls.base_path_flows  = '/flet-flows'
        cls.base_path_entity = '/cache-entity'
        cls.base_path_data   = '/cache-data'
        cls.cache_id         = cls.create_test_entity_with_flows()

    @classmethod
    def create_test_entity_with_flows(cls):
        # Create entity
        entity_url = f'{cls.base_path_entity}/{cls.namespace}/entity/create'
        entity_response = cls.client.post(entity_url, json={'cache_key': f'test/flows/{Random_Guid()}'})
        cache_id = entity_response.json()['cache_id']

        # Create flow data for html-to-cache
        flow_data_1 = {
            'flow_data': {
                'flow_id'  : 'flow-123',
                'flow_name': 'html-to-cache',
                'logs'     : [
                    {'level': 'INFO', 'message': 'Starting flow'  , 'timestamp': '2026-01-19T10:00:00'},
                    {'level': 'INFO', 'message': 'Processing HTML', 'timestamp': '2026-01-19T10:00:01'},
                    {'level': 'INFO', 'message': 'Flow completed' , 'timestamp': '2026-01-19T10:00:02'}
                ],
                'tasks': [
                    {'task_name': 'load'     , 'status': 'completed', 'duration': 0.1},
                    {'task_name': 'transform', 'status': 'completed', 'duration': 0.2},
                    {'task_name': 'save'     , 'status': 'completed', 'duration': 0.3}
                ]
            },
            'flow_events': [
                {'event': 'flow_started'  , 'timestamp': '2026-01-19T10:00:00'},
                {'event': 'flow_completed', 'timestamp': '2026-01-19T10:00:02'}
            ]
        }

        store_url_1 = f'{cls.base_path_data}/{cls.namespace}/data/{cache_id}/store/json/flows/html-to-cache/flow-data'
        cls.client.post(store_url_1, json={'content': flow_data_1})

        # Create flow data for html-from-cache
        flow_data_2 = {
            'flow_data': {
                'flow_id'  : 'flow-456',
                'flow_name': 'html-from-cache',
                'logs'     : [{'level': 'INFO', 'message': 'Loading from cache', 'timestamp': '2026-01-19T11:00:00'}],
                'tasks'    : [{'task_name': 'load', 'status': 'completed', 'duration': 0.05}]
            },
            'flow_events': []
        }

        store_url_2 = f'{cls.base_path_data}/{cls.namespace}/data/{cache_id}/store/json/flows/html-from-cache/flow-data'
        cls.client.post(store_url_2, json={'content': flow_data_2})

        return cache_id

    # ═══════════════════════════════════════════════════════════════════════════════
    # List FLeTs Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_flows__list(self):
        url = f'{self.base_path_flows}/flows/{self.namespace}/{self.cache_id}'

        response = self.client.get(url)

        assert response.status_code == 200
        result = response.json()
        assert result['success'] is True
        assert result['count']   == 2
        assert 'html-to-cache'   in result['flets']
        assert 'html-from-cache' in result['flets']

    def test_flows__list__empty(self):
        # Create entity with no flows
        entity_url = f'{self.base_path_entity}/{self.namespace}/entity/create'
        entity_response = self.client.post(entity_url, json={'cache_key': f'test/flows/empty-{Random_Guid()}'})
        empty_cache_id = entity_response.json()['cache_id']

        url = f'{self.base_path_flows}/flows/{self.namespace}/{empty_cache_id}'
        response = self.client.get(url)

        assert response.status_code == 200
        result = response.json()
        assert result['success'] is True
        assert result['count']   == 0
        assert result['flets']   == []

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Flow Data Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_flows__get(self):
        url = f'{self.base_path_flows}/flows/{self.namespace}/{self.cache_id}/html-to-cache'

        response = self.client.get(url)

        assert response.status_code == 200
        result = response.json()
        assert result['success']     is True
        assert result['flet_name']   == 'html-to-cache'
        assert result['flow_data']   is not None
        assert result['flow_events'] is not None
        assert len(result['flow_events']) == 2

    def test_flows__get__not_found(self):
        url = f'{self.base_path_flows}/flows/{self.namespace}/{self.cache_id}/nonexistent-flet'

        response = self.client.get(url)

        assert response.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Logs Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_flows__logs(self):
        url = f'{self.base_path_flows}/flows/{self.namespace}/{self.cache_id}/html-to-cache/logs'

        response = self.client.get(url)

        assert response.status_code == 200
        result = response.json()
        assert result['success']   is True
        assert result['flet_name'] == 'html-to-cache'
        assert result['count']     == 3
        assert len(result['logs']) == 3

    def test_flows__logs__not_found(self):
        url = f'{self.base_path_flows}/flows/{self.namespace}/{self.cache_id}/nonexistent-flet/logs'

        response = self.client.get(url)

        assert response.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Tasks Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_flows__tasks(self):
        url = f'{self.base_path_flows}/flows/{self.namespace}/{self.cache_id}/html-to-cache/tasks'

        response = self.client.get(url)

        assert response.status_code == 200
        result = response.json()
        assert result['success']   is True
        assert result['flet_name'] == 'html-to-cache'
        assert result['count']     == 3

    def test_flows__tasks__not_found(self):
        url = f'{self.base_path_flows}/flows/{self.namespace}/{self.cache_id}/nonexistent-flet/tasks'

        response = self.client.get(url)

        assert response.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Durations Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_flows__durations(self):
        url = f'{self.base_path_flows}/flows/{self.namespace}/{self.cache_id}/html-to-cache/durations'

        response = self.client.get(url)

        assert response.status_code == 200
        result = response.json()
        assert result['success']   is True
        assert result['flet_name'] == 'html-to-cache'
        assert 'durations' in result

    def test_flows__durations__not_found(self):
        url = f'{self.base_path_flows}/flows/{self.namespace}/{self.cache_id}/nonexistent-flet/durations'

        response = self.client.get(url)

        assert response.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_full_flow_inspection_workflow(self):
        # 1. List all flows
        list_url = f'{self.base_path_flows}/flows/{self.namespace}/{self.cache_id}'
        list_response = self.client.get(list_url)

        assert list_response.status_code == 200
        list_result = list_response.json()
        assert list_result['success'] is True
        assert 'html-to-cache' in list_result['flets']

        # 2. Get flow data
        flow_url = f'{self.base_path_flows}/flows/{self.namespace}/{self.cache_id}/html-to-cache'
        flow_response = self.client.get(flow_url)

        assert flow_response.status_code == 200
        assert flow_response.json()['success'] is True

        # 3. Get logs
        logs_url = f'{self.base_path_flows}/flows/{self.namespace}/{self.cache_id}/html-to-cache/logs'
        logs_response = self.client.get(logs_url)

        assert logs_response.status_code == 200
        assert logs_response.json()['count'] > 0

        # 4. Get tasks
        tasks_url = f'{self.base_path_flows}/flows/{self.namespace}/{self.cache_id}/html-to-cache/tasks'
        tasks_response = self.client.get(tasks_url)

        assert tasks_response.status_code == 200
        assert tasks_response.json()['count'] > 0

        # 5. Get durations
        durations_url = f'{self.base_path_flows}/flows/{self.namespace}/{self.cache_id}/html-to-cache/durations'
        durations_response = self.client.get(durations_url)

        assert durations_response.status_code == 200
        assert durations_response.json()['success'] is True

    def test_multiple_flows_in_same_entity(self):
        # Get flow data for both flows
        flow_1_url = f'{self.base_path_flows}/flows/{self.namespace}/{self.cache_id}/html-to-cache'
        flow_2_url = f'{self.base_path_flows}/flows/{self.namespace}/{self.cache_id}/html-from-cache'

        response_1 = self.client.get(flow_1_url)
        response_2 = self.client.get(flow_2_url)

        assert response_1.status_code == 200
        assert response_2.status_code == 200

        result_1 = response_1.json()
        result_2 = response_2.json()

        assert result_1['flet_name'] == 'html-to-cache'
        assert result_2['flet_name'] == 'html-from-cache'

        # Different flow data
        assert result_1['flow_data']['flow_id'] == 'flow-123'
        assert result_2['flow_data']['flow_id'] == 'flow-456'