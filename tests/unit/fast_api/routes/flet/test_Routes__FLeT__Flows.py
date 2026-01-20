# ═══════════════════════════════════════════════════════════════════════════════
# test_Routes__FLeT__Flows - Tests for FLeT flow observability routes
# Tests flow listing, data retrieval, logs, tasks, and durations
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                           import TestCase
from fastapi                                                                            import HTTPException
from mgraph_ai_service_html_graph.fast_api.routes.flet.Routes__FLeT__Flows              import Routes__FLeT__Flows
from mgraph_ai_service_html_graph.fast_api.routes.flet.Routes__FLeT__Flows              import TAG__ROUTES_FLET_FLOWS
from osbot_fast_api.api.routes.Fast_API__Routes                                         import Fast_API__Routes
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Create__Request  import Schema__Entity__Create__Request
from mgraph_ai_service_html_graph.schemas.flet.flows.Schema__Flow__Data__Response       import Schema__Flow__Data__Response
from mgraph_ai_service_html_graph.schemas.flet.flows.Schema__Flow__Durations__Response  import Schema__Flow__Durations__Response
from mgraph_ai_service_html_graph.schemas.flet.flows.Schema__Flow__List__Response       import Schema__Flow__List__Response
from mgraph_ai_service_html_graph.schemas.flet.flows.Schema__Flow__Logs__Response       import Schema__Flow__Logs__Response
from mgraph_ai_service_html_graph.schemas.flet.flows.Schema__Flow__Tasks__Response      import Schema__Flow__Tasks__Response
from mgraph_ai_service_html_graph.service.cache.Cache__Data__Service                    import Cache__Data__Service
from mgraph_ai_service_html_graph.service.cache.Cache__Entity__Service                  import Cache__Entity__Service
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.FLeT__Flows__Service       import FLeT__Flows__Service
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.utils.Objects                                                          import base_types
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                import create_html_cache_client


class test_Routes__FLeT__Flows(TestCase):

    @classmethod
    def setUpClass(cls):                                                            # Shared test objects
        cls.cache_client, cls.cache_service = create_html_cache_client()
        cls.flows_service  = FLeT__Flows__Service  (cache_client = cls.cache_client)
        cls.entity_service = Cache__Entity__Service(cache_client = cls.cache_client)
        cls.data_service   = Cache__Data__Service  (cache_client = cls.cache_client)
        cls.routes         = Routes__FLeT__Flows   (service      = cls.flows_service)
        cls.namespace      = 'test-routes-flet-flows'
        cls.cache_id       = cls.create_test_entity_with_flows()

    @classmethod
    def create_test_entity_with_flows(cls):                                         # Create entity with flow data
        request  = Schema__Entity__Create__Request(cache_key = 'test/flows/entity')
        response = cls.entity_service.create(namespace = cls.namespace ,
                                             request   = request       )
        cache_id = response.cache_id

        flow_data_1 = { 'flow_data'  : { 'flow_id'  : 'flow-123'                                                           ,
                                         'flow_name': 'html-to-cache'                                                      ,
                                         'logs'     : [{'level': 'INFO', 'message': 'Starting flow'  , 'timestamp': '2026-01-19T10:00:00'},
                                                       {'level': 'INFO', 'message': 'Processing HTML', 'timestamp': '2026-01-19T10:00:01'},
                                                       {'level': 'INFO', 'message': 'Flow completed' , 'timestamp': '2026-01-19T10:00:02'}],
                                         'tasks'    : [{'task_name': 'load'     , 'status': 'completed', 'duration': 0.1},
                                                       {'task_name': 'transform', 'status': 'completed', 'duration': 0.2},
                                                       {'task_name': 'save'     , 'status': 'completed', 'duration': 0.3}]},
                        'flow_events': [{'event': 'flow_started'  , 'timestamp': '2026-01-19T10:00:00'},
                                        {'event': 'flow_completed', 'timestamp': '2026-01-19T10:00:02'}]}

        cls.data_service.store_json(namespace    = cls.namespace         ,
                                    cache_id     = cache_id              ,
                                    data_key     = 'flows/html-to-cache' ,
                                    data_file_id = 'flow-data'           ,
                                    content      = flow_data_1           )

        flow_data_2 = { 'flow_data'  : { 'flow_id'  : 'flow-456'                                                                 ,
                                         'flow_name': 'html-from-cache'                                                         ,
                                         'logs'     : [{'level': 'INFO', 'message': 'Loading from cache', 'timestamp': '2026-01-19T11:00:00'}],
                                         'tasks'    : [{'task_name': 'load', 'status': 'completed', 'duration': 0.05}]          },
                        'flow_events': []                                                                                        }

        cls.data_service.store_json(namespace    = cls.namespace           ,
                                    cache_id     = cache_id                ,
                                    data_key     = 'flows/html-from-cache' ,
                                    data_file_id = 'flow-data'             ,
                                    content      = flow_data_2             )

        return cache_id

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                         # Test initialization
        with Routes__FLeT__Flows() as _:
            assert type(_)       is Routes__FLeT__Flows
            assert base_types(_) == [Fast_API__Routes, Type_Safe, object]
            assert _.tag         == TAG__ROUTES_FLET_FLOWS
            assert _.service     is None

    def test__init____with_service(self):                                           # Test with service
        with Routes__FLeT__Flows(service=self.flows_service) as _:
            assert _.service is self.flows_service

    # ═══════════════════════════════════════════════════════════════════════════════
    # List FLeTs Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_flows__list(self):                                                     # Test list FLeTs
        response = self.routes.flows__list(namespace = self.namespace ,
                                           cache_id  = self.cache_id  )

        assert type(response)   is Schema__Flow__List__Response
        assert response.success is True
        assert response.count   == 2
        assert 'html-to-cache'   in response.flets
        assert 'html-from-cache' in response.flets

    def test_flows__list__empty(self):                                              # Test list with no flows
        request        = Schema__Entity__Create__Request(cache_key = 'test/flows/empty')
        response       = self.entity_service.create(namespace = self.namespace, request = request)
        empty_cache_id = response.cache_id

        result = self.routes.flows__list(namespace = self.namespace ,
                                         cache_id  = empty_cache_id )

        assert result.success is True
        assert result.count   == 0
        assert result.flets   == []

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Flow Data Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_flows__get(self):                                                      # Test get flow data
        response = self.routes.flows__get(namespace = self.namespace  ,
                                          cache_id  = self.cache_id   ,
                                          flet_name = 'html-to-cache' )

        assert type(response)       is Schema__Flow__Data__Response
        assert response.success     is True
        assert response.flet_name   == 'html-to-cache'
        assert response.flow_data   is not None
        assert response.flow_events is not None
        assert len(response.flow_events) == 2

    def test_flows__get__not_found(self):                                           # Test get non-existent flow
        with self.assertRaises(HTTPException) as context:
            self.routes.flows__get(namespace = self.namespace     ,
                                   cache_id  = self.cache_id      ,
                                   flet_name = 'nonexistent-flet' )

        assert context.exception.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Logs Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_flows__logs(self):                                                     # Test get logs
        response = self.routes.flows__logs(namespace = self.namespace  ,
                                           cache_id  = self.cache_id   ,
                                           flet_name = 'html-to-cache' )

        assert type(response)     is Schema__Flow__Logs__Response
        assert response.success   is True
        assert response.flet_name == 'html-to-cache'
        assert response.count     == 3
        assert len(response.logs) == 3

    def test_flows__logs__not_found(self):                                          # Test get logs for non-existent flow
        with self.assertRaises(HTTPException) as context:
            self.routes.flows__logs(namespace = self.namespace     ,
                                    cache_id  = self.cache_id      ,
                                    flet_name = 'nonexistent-flet' )

        assert context.exception.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Tasks Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_flows__tasks(self):                                                    # Test get tasks
        response = self.routes.flows__tasks(namespace = self.namespace  ,
                                            cache_id  = self.cache_id   ,
                                            flet_name = 'html-to-cache' )

        assert type(response)               is Schema__Flow__Tasks__Response
        assert response.success             is True
        assert response.flet_name           == 'html-to-cache'
        assert response.count               == 3
        assert len(response.tasks__as_list) == 3

    def test_flows__tasks__not_found(self):                                         # Test get tasks for non-existent flow
        with self.assertRaises(HTTPException) as context:
            self.routes.flows__tasks(namespace = self.namespace     ,
                                     cache_id  = self.cache_id      ,
                                     flet_name = 'nonexistent-flet' )

        assert context.exception.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Durations Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__bug__flows__durations(self):                                                # Test get durations
        response = self.routes.flows__durations(namespace = self.namespace  ,
                                                cache_id  = self.cache_id   ,
                                                flet_name = 'html-to-cache' )

        assert type(response)                      is Schema__Flow__Durations__Response
        assert response.success                    is True
        assert response.flet_name                  == 'html-to-cache'
        assert response.durations                  is not None
        assert response.durations                  == {}            # BUG, the values below are not being set
        # assert response.durations.get('load')      == 0.1
        # assert response.durations.get('transform') == 0.2
        # assert response.durations.get('save')      == 0.3
        # assert response.total_duration             == 0.6                           # 0.1 + 0.2 + 0.3

    def test_flows__durations__not_found(self):                                     # Test get durations for non-existent flow
        with self.assertRaises(HTTPException) as context:
            self.routes.flows__durations(namespace = self.namespace     ,
                                         cache_id  = self.cache_id      ,
                                         flet_name = 'nonexistent-flet' )

        assert context.exception.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_full_flow_inspection_workflow(self):                                   # Test complete inspection workflow
        list_response = self.routes.flows__list(namespace = self.namespace ,
                                                cache_id  = self.cache_id  )

        assert list_response.success   is True
        assert 'html-to-cache' in list_response.flets

        flow_response = self.routes.flows__get(namespace = self.namespace  ,
                                               cache_id  = self.cache_id   ,
                                               flet_name = 'html-to-cache' )

        assert flow_response.success is True

        logs_response = self.routes.flows__logs(namespace = self.namespace  ,
                                                cache_id  = self.cache_id   ,
                                                flet_name = 'html-to-cache' )

        assert logs_response.success is True
        assert logs_response.count   > 0

        tasks_response = self.routes.flows__tasks(namespace = self.namespace  ,
                                                  cache_id  = self.cache_id   ,
                                                  flet_name = 'html-to-cache' )

        assert tasks_response.success is True
        assert tasks_response.count   > 0

        durations_response = self.routes.flows__durations(namespace = self.namespace  ,
                                                          cache_id  = self.cache_id   ,
                                                          flet_name = 'html-to-cache' )

        assert durations_response.success        is True
        #assert durations_response.total_duration > 0
