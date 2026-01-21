# ═══════════════════════════════════════════════════════════════════════════════
# Routes__FLeT__Flows - REST API for FLeT flow observability
# Provides endpoints to inspect flow data, logs, tasks, and durations
#
# Path pattern: /flet/flows/{namespace}/{cache_id}/...
# ═══════════════════════════════════════════════════════════════════════════════

from fastapi                                                                            import HTTPException
from osbot_fast_api.api.decorators.route_path                                           import route_path
from mgraph_ai_service_html_graph.schemas.flet.flows.Schema__Flow__Data__Response       import Schema__Flow__Data__Response
from mgraph_ai_service_html_graph.schemas.flet.flows.Schema__Flow__Durations__Response  import Schema__Flow__Durations__Response
from mgraph_ai_service_html_graph.schemas.flet.flows.Schema__Flow__List__Response       import Schema__Flow__List__Response
from mgraph_ai_service_html_graph.schemas.flet.flows.Schema__Flow__Logs__Response       import Schema__Flow__Logs__Response
from mgraph_ai_service_html_graph.schemas.flet.flows.Schema__Flow__Tasks__Response      import Schema__Flow__Tasks__Response
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.FLeT__Flows__Service       import FLeT__Flows__Service
from osbot_fast_api.api.routes.Fast_API__Routes                                         import Fast_API__Routes


TAG__ROUTES_FLET_FLOWS = 'flet-flows'

ROUTES_PATHS__FLET_FLOWS = [f'/{TAG__ROUTES_FLET_FLOWS}' + '/flows/{namespace}/{cache_id}'                    ,
                            f'/{TAG__ROUTES_FLET_FLOWS}' + '/flows/{namespace}/{cache_id}/{flet_name}'        ,
                            f'/{TAG__ROUTES_FLET_FLOWS}' + '/flows/{namespace}/{cache_id}/{flet_name}/logs'   ,
                            f'/{TAG__ROUTES_FLET_FLOWS}' + '/flows/{namespace}/{cache_id}/{flet_name}/tasks'  ,
                            f'/{TAG__ROUTES_FLET_FLOWS}' + '/flows/{namespace}/{cache_id}/{flet_name}/durations']


class Routes__FLeT__Flows(Fast_API__Routes):                                        # FLeT flow observability routes
    tag     : str                  = TAG__ROUTES_FLET_FLOWS                         # Route tag
    service : FLeT__Flows__Service                                                  # Flows service

    # ═══════════════════════════════════════════════════════════════════════════════
    # List FLeTs
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/flows/{namespace}/{cache_id}')
    def flows__list(self              ,                                             # List all FLeTs for entity
                    namespace : str   ,                                             # Cache namespace
                    cache_id  : str                                                 # Entity cache ID
               ) -> Schema__Flow__List__Response:                                   # GET /flows/{namespace}/{cache_id}
        try:
            return self.service.list_flets(namespace = namespace ,
                                           cache_id  = cache_id  )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Flow Data
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/flows/{namespace}/{cache_id}/{flet_name}')
    def flows__get(self              ,                                              # Get full flow data for FLeT
                   namespace  : str  ,                                              # Cache namespace
                   cache_id   : str  ,                                              # Entity cache ID
                   flet_name  : str                                                 # FLeT name
              ) -> Schema__Flow__Data__Response:                                    # GET /flows/{namespace}/{cache_id}/{flet_name}
        try:
            result = self.service.get_flow(namespace = namespace ,
                                           cache_id  = cache_id  ,
                                           flet_name = flet_name )
            if result.success is False:
                raise HTTPException(status_code = 404                                         ,
                                    detail      = f"Flow data not found for FLeT: {flet_name}")
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Logs
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/flows/{namespace}/{cache_id}/{flet_name}/logs')
    def flows__logs(self              ,                                             # Get logs from FLeT execution
                    namespace  : str  ,                                             # Cache namespace
                    cache_id   : str  ,                                             # Entity cache ID
                    flet_name  : str                                                # FLeT name
               ) -> Schema__Flow__Logs__Response:                                   # GET /flows/{namespace}/{cache_id}/{flet_name}/logs
        try:
            result = self.service.get_logs(namespace = namespace ,
                                           cache_id  = cache_id  ,
                                           flet_name = flet_name )
            if result.success is False:
                raise HTTPException(status_code = 404                                         ,
                                    detail      = f"Flow data not found for FLeT: {flet_name}")
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Tasks
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/flows/{namespace}/{cache_id}/{flet_name}/tasks')
    def flows__tasks(self              ,                                            # Get tasks from FLeT execution
                     namespace  : str  ,                                            # Cache namespace
                     cache_id   : str  ,                                            # Entity cache ID
                     flet_name  : str                                               # FLeT name
                ) -> Schema__Flow__Tasks__Response:                                 # GET /flows/{namespace}/{cache_id}/{flet_name}/tasks
        try:
            result = self.service.get_tasks(namespace = namespace ,
                                            cache_id  = cache_id  ,
                                            flet_name = flet_name )
            if result.success is False:
                raise HTTPException(status_code = 404                                         ,
                                    detail      = f"Flow data not found for FLeT: {flet_name}")
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Durations
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/flows/{namespace}/{cache_id}/{flet_name}/durations')
    def flows__durations(self              ,                                        # Get task durations from FLeT
                         namespace  : str  ,                                        # Cache namespace
                         cache_id   : str  ,                                        # Entity cache ID
                         flet_name  : str                                           # FLeT name
                    ) -> Schema__Flow__Durations__Response:                         # GET /flows/{namespace}/{cache_id}/{flet_name}/durations
        try:
            result = self.service.get_durations(namespace = namespace ,
                                                cache_id  = cache_id  ,
                                                flet_name = flet_name )
            if result.success is False:
                raise HTTPException(status_code = 404                                         ,
                                    detail      = f"Flow data not found for FLeT: {flet_name}")
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Route Setup
    # ═══════════════════════════════════════════════════════════════════════════════

    def setup_routes(self):                                                         # Configure all routes
        self.add_route_get(self.flows__list     )
        self.add_route_get(self.flows__get      )
        self.add_route_get(self.flows__logs     )
        self.add_route_get(self.flows__tasks    )
        self.add_route_get(self.flows__durations)

        return self