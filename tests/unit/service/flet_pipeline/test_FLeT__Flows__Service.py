# ═══════════════════════════════════════════════════════════════════════════════
# Test__FLeT__Flows__Service - Tests for flow observability service
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                               import TestCase

from mgraph_ai_service_cache_client.client.cache_service.register_cache_service import register_cache_service__in_memory
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Create__Request      import Schema__Entity__Create__Request
from mgraph_ai_service_html_graph.schemas.flet.flows.Schema__Flow__Data__Response           import Schema__Flow__Data__Response
from mgraph_ai_service_html_graph.schemas.flet.flows.Schema__Flow__Durations__Response      import Schema__Flow__Durations__Response
from mgraph_ai_service_html_graph.schemas.flet.flows.Schema__Flow__List__Response           import Schema__Flow__List__Response
from mgraph_ai_service_html_graph.schemas.flet.flows.Schema__Flow__Logs__Response           import Schema__Flow__Logs__Response
from mgraph_ai_service_html_graph.schemas.flet.flows.Schema__Flow__Tasks__Response          import Schema__Flow__Tasks__Response
from mgraph_ai_service_html_graph.schemas.flet.html.Schema__FLeT__Html__To__Cache__Request  import Schema__FLeT__Html__To__Cache__Request
from mgraph_ai_service_html_graph.service.cache.Cache__Entity__Service                      import Cache__Entity__Service
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client import Html_Cache__Client
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.FLeT__Flows__Service           import FLeT__Flows__Service
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.FLeT__Html__Execute__Service   import FLeT__Html__Execute__Service
from osbot_utils.testing.__                                                                 import __
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid                       import Random_Guid
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List                       import Type_Safe__List


class test_FLeT__Flows__Service(TestCase):

    @classmethod
    def setUpClass(cls):                                                          # Shared test objects
        cls.cache_service_client = register_cache_service__in_memory(return_client=True)
        cls.html_cache_client    = Html_Cache__Client()
        cls.entity_service       = Cache__Entity__Service      (html_cache_client=cls.html_cache_client)
        cls.execute_service      = FLeT__Html__Execute__Service(html_cache_client=cls.html_cache_client)
        cls.flows_service        = FLeT__Flows__Service        (html_cache_client=cls.html_cache_client)
        cls.namespace            = 'test-flet-flows-service'
        cls.test_html            = '<html><body><h1>Test Content</h1></body></html>'

    def setUp(self):                                                              # Per-test setup
        self.cache_key = f'test/flows/{Random_Guid()}'

    def _create_entity_with_flow(self):                                           # Helper to create entity and execute FLeT
        create_request = Schema__Entity__Create__Request(cache_key=self.cache_key)
        create_result  = self.entity_service.create(namespace=self.namespace, request=create_request)
        cache_id       = create_result.cache_id

        execute_request = Schema__FLeT__Html__To__Cache__Request(html=self.test_html)
        self.execute_service.execute_to_cache(namespace=self.namespace, cache_id=cache_id, request=execute_request)

        return cache_id

    # ═══════════════════════════════════════════════════════════════════════════
    # list_flets Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__list_flets__empty_when_no_flows(self):
        create_request = Schema__Entity__Create__Request(cache_key=self.cache_key)
        create_result  = self.entity_service.create(namespace=self.namespace, request=create_request)

        result = self.flows_service.list_flets(namespace=self.namespace, cache_id=create_result.cache_id)

        assert type(result)   is Schema__Flow__List__Response
        assert result.success is True
        assert result.flets   == []
        assert result.count   == 0

    def test__list_flets__returns_executed_flets(self):
        cache_id = self._create_entity_with_flow()

        result = self.flows_service.list_flets(namespace=self.namespace, cache_id=cache_id)

        assert result.success    is True
        assert result.count      >= 1
        assert len(result.flets) >= 1                                             # At least html-to-cache executed
        assert result.obj()      == __(success = True            ,
                                       flets   = ['html-to-cache'],
                                       count   = 1               )

    # ═══════════════════════════════════════════════════════════════════════════
    # get_flow Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__get_flow__not_found(self):
        create_request = Schema__Entity__Create__Request(cache_key=self.cache_key)
        create_result  = self.entity_service.create(namespace=self.namespace, request=create_request)

        result = self.flows_service.get_flow(namespace=self.namespace, cache_id=create_result.cache_id, flet_name='nonexistent')

        assert type(result)   is Schema__Flow__Data__Response
        assert result.success is False

    def test__get_flow__success_after_execution(self):
        cache_id = self._create_entity_with_flow()

        flets_result = self.flows_service.list_flets(namespace=self.namespace, cache_id=cache_id)
        if flets_result.flets:
            flet_name = flets_result.flets[0]

            result = self.flows_service.get_flow(namespace=self.namespace, cache_id=cache_id, flet_name=flet_name)

            assert result.success   is True
            assert result.flet_name == flet_name
            assert result.flow_data is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # get_logs Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__get_logs__flow_not_found(self):
        create_request = Schema__Entity__Create__Request(cache_key=self.cache_key)
        create_result  = self.entity_service.create(namespace=self.namespace, request=create_request)

        result = self.flows_service.get_logs(namespace=self.namespace, cache_id=create_result.cache_id, flet_name='nonexistent')

        assert type(result)   is Schema__Flow__Logs__Response
        assert result.success is False
        assert result.logs    == []

    def test__get_logs__returns_logs_after_execution(self):
        cache_id = self._create_entity_with_flow()

        flets_result = self.flows_service.list_flets(namespace=self.namespace, cache_id=cache_id)
        if flets_result.flets:
            flet_name = flets_result.flets[0]

            result = self.flows_service.get_logs(namespace=self.namespace, cache_id=cache_id, flet_name=flet_name)

            assert result.success    is True
            assert result.flet_name  == flet_name
            assert type(result.logs) is Type_Safe__List

    # ═══════════════════════════════════════════════════════════════════════════
    # get_tasks Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__get_tasks__flow_not_found(self):
        create_request = Schema__Entity__Create__Request(cache_key=self.cache_key)
        create_result  = self.entity_service.create(namespace=self.namespace, request=create_request)

        result = self.flows_service.get_tasks(namespace=self.namespace, cache_id=create_result.cache_id, flet_name='nonexistent')

        assert type(result)   is Schema__Flow__Tasks__Response
        assert result.success is False
        assert result.tasks   == {}

    def test__get_tasks__returns_tasks_after_execution(self):
        cache_id = self._create_entity_with_flow()

        flets_result = self.flows_service.list_flets(namespace=self.namespace, cache_id=cache_id)
        if flets_result.flets:
            flet_name = flets_result.flets[0]

            result = self.flows_service.get_tasks(namespace=self.namespace, cache_id=cache_id, flet_name=flet_name)

            assert result.success     is True
            assert result.flet_name   == flet_name
            assert type(result.tasks) is dict

    # ═══════════════════════════════════════════════════════════════════════════
    # get_durations Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__get_durations__flow_not_found(self):
        create_request = Schema__Entity__Create__Request(cache_key=self.cache_key)
        create_result  = self.entity_service.create(namespace=self.namespace, request=create_request)

        result = self.flows_service.get_durations(namespace = self.namespace,
                                                  cache_id  = create_result.cache_id,
                                                  flet_name = 'nonexistent')

        assert type(result)          is Schema__Flow__Durations__Response
        assert result.success        is False
        assert result.durations      == {}
        assert result.total_duration == 0.0

    def test__get_durations__returns_durations_after_execution(self):
        cache_id = self._create_entity_with_flow()

        flets_result = self.flows_service.list_flets(namespace=self.namespace, cache_id=cache_id)
        if flets_result.flets:
            flet_name = flets_result.flets[0]

            result = self.flows_service.get_durations(namespace = self.namespace,
                                                      cache_id  = cache_id      ,
                                                      flet_name = flet_name     )

            assert result.success   is True
            assert result.flet_name == flet_name
            assert type(result.durations) is dict
            assert result.total_duration >= 0.0
