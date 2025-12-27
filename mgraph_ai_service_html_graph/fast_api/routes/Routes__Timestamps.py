# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Timestamp Routes
# v1.0.0 - Routes for graph transformation with timestamp capture
#
# URL pattern: /timestamps/graph/from/html/to/{engine}/{transformation}/{format}
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_fast_api.api.decorators.route_path                                                            import route_path
from osbot_fast_api.api.routes.Fast_API__Routes                                                          import Fast_API__Routes
from osbot_utils.helpers.timestamp_capture.Timestamp_Collector                                           import Timestamp_Collector
from osbot_utils.helpers.timestamp_capture.actions.Timestamp_Collector__Export                           import Timestamp_Collector__Export
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__Graph__With_Traces__Request                 import Schema__Graph__With_Traces__Request
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__Graph__With_Traces__Response__Full          import Schema__Graph__With_Traces__Response__Full
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__Graph__With_Traces__Response__Summary       import Schema__Graph__With_Traces__Response__Summary
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__Graph__With_Traces__Response__Speedscope    import Schema__Graph__With_Traces__Response__Speedscope
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Schemas                 import Schema__Graph__From_Html__Request, Schema__Graph__Response__Base
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service                 import Html_Graph__Export__Service
from osbot_utils.helpers.timestamp_capture.decorators.timestamp import timestamp

TAG__ROUTES_TIMESTAMPS = 'timestamps'

ROUTES_PATHS__TIMESTAMPS = [
    f'/{TAG__ROUTES_TIMESTAMPS}/graph/from/html/to/{{engine}}/{{transformation}}/full',
    f'/{TAG__ROUTES_TIMESTAMPS}/graph/from/html/to/{{engine}}/{{transformation}}/summary',
    f'/{TAG__ROUTES_TIMESTAMPS}/graph/from/html/to/{{engine}}/{{transformation}}/speedscope',
]


class Routes__Timestamps(Fast_API__Routes):                                      # Routes for graph export with timestamp capture
    tag           : str                         = TAG__ROUTES_TIMESTAMPS
    graph_service : Html_Graph__Export__Service

    # ═══════════════════════════════════════════════════════════════════════════
    # Route Handlers
    # ═══════════════════════════════════════════════════════════════════════════

    @route_path("/graph/from/html/to/{engine}/{transformation}/full")
    def from_html_with_traces_full(self, engine        : str                                    ,
                                         transformation: str                                    ,
                                         request       : Schema__Graph__With_Traces__Request
                                  ) -> Schema__Graph__With_Traces__Response__Full:
        graph_response, export = self._execute_with_timestamps(engine, transformation, request)
        traces                 = export.to_export_full()
        return Schema__Graph__With_Traces__Response__Full(graph  = graph_response,
                                                          traces = traces        )

    @route_path("/graph/from/html/to/{engine}/{transformation}/summary")
    def from_html_with_traces_summary(self, engine        : str                                 ,
                                            transformation: str                                 ,
                                            request       : Schema__Graph__With_Traces__Request
                                     ) -> Schema__Graph__With_Traces__Response__Summary:
        graph_response, export = self._execute_with_timestamps(engine, transformation, request)
        traces                 = export.to_export_summary()
        return Schema__Graph__With_Traces__Response__Summary(graph  = graph_response,
                                                             traces = traces        )

    @route_path("/graph/from/html/to/{engine}/{transformation}/speedscope")
    def from_html_with_traces_speedscope(self, engine        : str                              ,
                                               transformation: str                              ,
                                               request       : Schema__Graph__With_Traces__Request
                                        ) -> Schema__Graph__With_Traces__Response__Speedscope:
        graph_response, export = self._execute_with_timestamps(engine, transformation, request)
        traces                 = export.to_speedscope_json()
        return Schema__Graph__With_Traces__Response__Speedscope(graph  = graph_response,
                                                                traces = traces        )

    # ═══════════════════════════════════════════════════════════════════════════
    # Internal Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _execute_with_timestamps(self, engine        : str                              ,
                                       transformation: str                              ,
                                       request       : Schema__Graph__With_Traces__Request
                                ) -> tuple[Schema__Graph__Response__Base, Timestamp_Collector__Export]:
        collector_name         = f"{transformation}.{engine}"
        _timestamp_collector_  = Timestamp_Collector(name=collector_name)

        with _timestamp_collector_:
            graph_response = self._execute_pipeline(engine, transformation, request.graph_request)

        export = Timestamp_Collector__Export(collector=_timestamp_collector_)
        return graph_response, export

    @timestamp(name='routes.timestamsps.execute_pipeline')
    def _execute_pipeline(self, engine        : str                          ,
                                transformation: str                          ,
                                request       : Schema__Graph__From_Html__Request
                         ) -> Schema__Graph__Response__Base:
        render_method = self._get_render_method(engine)
        return render_method(request, transformation=transformation)

    def _get_render_method(self, engine: str):
        engine_methods = { 'default'  : self.graph_service.to_dot      ,
                           'dot'      : self.graph_service.to_dot       ,
                           'visjs'    : self.graph_service.to_visjs     ,
                           'd3'       : self.graph_service.to_d3        ,
                           'cytoscape': self.graph_service.to_cytoscape ,
                           'mermaid'  : self.graph_service.to_mermaid   ,
                           'tree'     : self.graph_service.to_tree      }
        if engine not in engine_methods:
            raise ValueError(f"Unknown graph engine: {engine}")
        return engine_methods[engine]

    # ═══════════════════════════════════════════════════════════════════════════
    # Route Setup
    # ═══════════════════════════════════════════════════════════════════════════

    def setup_routes(self):
        self.add_route_post(self.from_html_with_traces_full)
        self.add_route_post(self.from_html_with_traces_summary)
        self.add_route_post(self.from_html_with_traces_speedscope)
        return self
