# ═══════════════════════════════════════════════════════════════════════════════
# FLeT__Flows__Service - Service layer for flow observability operations
# ═══════════════════════════════════════════════════════════════════════════════

from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__Namespace              import Safe_Str__Cache__Namespace
from mgraph_ai_service_html_graph.schemas.flet.flows.Schema__Flow__Data__Response                  import Schema__Flow__Data__Response
from mgraph_ai_service_html_graph.schemas.flet.flows.Schema__Flow__Durations__Response             import Schema__Flow__Durations__Response
from mgraph_ai_service_html_graph.schemas.flet.flows.Schema__Flow__List__Response                  import Schema__Flow__List__Response
from mgraph_ai_service_html_graph.schemas.flet.flows.Schema__Flow__Logs__Response                  import Schema__Flow__Logs__Response
from mgraph_ai_service_html_graph.schemas.flet.flows.Schema__Flow__Tasks__Response                 import Schema__Flow__Tasks__Response
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                         import Html_Cache__Client
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.safe_str.Safe_Str__FLeT__Name import Safe_Str__FLeT__Name
from osbot_utils.type_safe.Type_Safe                                                               import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                 import Cache_Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                     import type_safe


class FLeT__Flows__Service(Type_Safe):                                              # Service for flow observability
    html_cache_client : Html_Cache__Client                                               # Cache client for data access

    @type_safe
    def list_flets(self                                       ,                     # List all FLeTs executed for entity
                   namespace : Safe_Str__Cache__Namespace     ,                     # Cache namespace
                   cache_id  : Cache_Id                                             # Entity cache ID
              ) -> Schema__Flow__List__Response:
        try:
            result = self.html_cache_client.data__list(namespace = namespace,
                                                       cache_id  = cache_id,
                                                       data_key  = 'flows',
                                                       recursive = True)
            if result is None or not result.files:
                return Schema__Flow__List__Response(success = True ,
                                                    flets   = []   ,
                                                    count   = 0    )
            flet_names = set()
            for file_info in result.files:
                path  = file_info.file_path
                parts = path.split('/')
                if len(parts) >= 2:
                    flet_names.add(parts[-2])                                                           # todo: find a better way to map and figure this out

            sorted_names = sorted(list(flet_names))
            return Schema__Flow__List__Response(success = True              ,
                                                flets   = sorted_names      ,
                                                count   = len(sorted_names) )
        except Exception:
            return Schema__Flow__List__Response(success = False ,
                                                flets   = []    ,
                                                count   = 0     )

    @type_safe
    def get_flow(self                                      ,                        # Get full flow data for FLeT
                 namespace : Safe_Str__Cache__Namespace    ,                        # Cache namespace
                 cache_id  : Cache_Id                      ,                        # Entity cache ID
                 flet_name : Safe_Str__FLeT__Name                                   # FLeT name to retrieve
            ) -> Schema__Flow__Data__Response:
        try:
            flow_data = self.html_cache_client.data__retrieve_json(namespace    = namespace,
                                                                   cache_id     = cache_id,
                                                                   data_key     = f'flows/{flet_name}',  # todo: find a better way to resolve this name so that it is not hardcoded here
                                                                   data_file_id = 'flow-data')           #       same here
            if flow_data is None:
                return Schema__Flow__Data__Response(success   = False    ,
                                                    flet_name = flet_name)

            inner_flow_data = flow_data.get('flow_data'  , flow_data)
            flow_events     = flow_data.get('flow_events', []       )

            return Schema__Flow__Data__Response(success     = True           ,
                                                flet_name   = flet_name      ,
                                                flow_data   = inner_flow_data,
                                                flow_events = flow_events    )
        except Exception:
            return Schema__Flow__Data__Response(success   = False    ,
                                                flet_name = flet_name)

    @type_safe
    def get_logs(self                                      ,                        # Get logs from flow data
                 namespace : Safe_Str__Cache__Namespace    ,                        # Cache namespace
                 cache_id  : Cache_Id                      ,                        # Entity cache ID
                 flet_name : Safe_Str__FLeT__Name                                   # FLeT name
            ) -> Schema__Flow__Logs__Response:
        flow_response = self.get_flow(namespace = namespace ,
                                      cache_id  = cache_id  ,
                                      flet_name = flet_name )
        if flow_response.success is False:
            return Schema__Flow__Logs__Response(success   = False    ,
                                                flet_name = flet_name,
                                                logs      = []       ,
                                                count     = 0        )
        logs = []
        if flow_response.flow_data:
            logs = flow_response.flow_data.get('logs', [])

        return Schema__Flow__Logs__Response(success   = True      ,
                                            flet_name = flet_name ,
                                            logs      = logs      ,
                                            count     = len(logs) )

    @type_safe
    def get_tasks(self                                      ,                       # Get tasks from flow data
                  namespace : Safe_Str__Cache__Namespace    ,                       # Cache namespace
                  cache_id  : Cache_Id                      ,                       # Entity cache ID
                  flet_name : Safe_Str__FLeT__Name                                  # FLeT name
             ) -> Schema__Flow__Tasks__Response:
        flow_response = self.get_flow(namespace = namespace ,
                                      cache_id  = cache_id  ,
                                      flet_name = flet_name )
        if flow_response.success is False:
            return Schema__Flow__Tasks__Response(success   = False    ,
                                                 flet_name = flet_name,
                                                 tasks     = {}       ,
                                                 count     = 0        )
        tasks = {}
        tasks__as_list = []
        if flow_response.flow_data:
            tasks_data = flow_response.flow_data.get('tasks')                               # todo: this should be a type_safe object
            if type(tasks_data) is list:                                                    #       exactly because of this
                tasks__as_list = tasks_data
            elif type(tasks_data) is dict:
                tasks = tasks_data

        return Schema__Flow__Tasks__Response(success        = True                               ,
                                             flet_name      = flet_name                          ,
                                             tasks          = tasks                              ,
                                             tasks__as_list = tasks__as_list                     ,   # todo: BUG - this should be a type_safe class (and not be needed)
                                             count          = len(tasks__as_list) + len(tasks)   )   #       BUG - this should only be tasks

    @type_safe
    def get_durations(self                                      ,                   # Get task durations from flow
                      namespace : Safe_Str__Cache__Namespace    ,                   # Cache namespace
                      cache_id  : Cache_Id                      ,                   # Entity cache ID
                      flet_name : Safe_Str__FLeT__Name                              # FLeT name
                 ) -> Schema__Flow__Durations__Response:
        tasks_response = self.get_tasks(namespace = namespace ,
                                        cache_id  = cache_id  ,
                                        flet_name = flet_name )
        if tasks_response.success is False:
            return Schema__Flow__Durations__Response(success        = False    ,
                                                     flet_name      = flet_name,
                                                     durations      = {}       ,
                                                     total_duration = 0.0      )
        durations      = {}
        total_duration = 0.0

        for task_name, task in tasks_response.tasks.items():
            duration  = task.get('duration')
            if duration is not None:
                durations[task_name] = duration
                total_duration      += duration

        return Schema__Flow__Durations__Response(success        = True          ,
                                                 flet_name      = flet_name     ,
                                                 durations      = durations     ,
                                                 total_duration = total_duration)