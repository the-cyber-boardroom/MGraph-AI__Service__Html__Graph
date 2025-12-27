# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Timestamp Routes
# v1.0.0 - Routes for graph transformation with timestamp capture
#
# URL pattern: /timestamps/graph/from/html/to/{engine}/{transformation}/{format}
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_fast_api.api.decorators.route_path                                                            import route_path
from osbot_fast_api.api.routes.Fast_API__Routes                                                          import Fast_API__Routes
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__Trace_Config                                import Schema__Trace_Config
from mgraph_ai_service_html_graph.schemas.timestamps.enums.Enum__Trace_Output                            import Enum__Trace_Output
from mgraph_ai_service_html_graph.schemas.timestamps.enums.Schema__Trace__Response__Type                 import Schema__Trace__Response__Type
from osbot_utils.helpers.timestamp_capture.Timestamp_Collector                                           import Timestamp_Collector
from osbot_utils.helpers.timestamp_capture.actions.Timestamp_Collector__Export                           import Timestamp_Collector__Export
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__Graph__With_Traces__Request                 import Schema__Graph__With_Traces__Request
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__Graph__With_Traces__Response__Full          import Schema__Graph__With_Traces__Response__Full
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__Graph__With_Traces__Response__Summary       import Schema__Graph__With_Traces__Response__Summary
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__Graph__With_Traces__Response__Speedscope    import Schema__Graph__With_Traces__Response__Speedscope
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Schemas                 import Schema__Graph__From_Html__Request, Schema__Graph__Response__Base
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service                 import Html_Graph__Export__Service
from osbot_utils.helpers.timestamp_capture.decorators.timestamp                                          import timestamp
from osbot_utils.helpers.timestamp_capture.schemas.export.Schema__Export_Summary                         import Schema__Export_Summary

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
        response               = self.create_response__full(graph_response, request.trace_config, traces)
        return response

    @route_path("/graph/from/html/to/{engine}/{transformation}/summary")
    def from_html_with_traces_summary(self, engine        : str                                 ,
                                            transformation: str                                 ,
                                            request       : Schema__Graph__With_Traces__Request
                                     ) -> Schema__Graph__With_Traces__Response__Summary:
        graph_response, export = self._execute_with_timestamps(engine, transformation, request)
        traces                 = export.to_export_summary()
        response               = self.create_response__summary(graph_response, request.trace_config, traces)
        return response


    @route_path("/graph/from/html/to/{engine}/{transformation}/speedscope")
    def from_html_with_traces_speedscope(self, engine        : str                              ,
                                               transformation: str                              ,
                                               request       : Schema__Graph__With_Traces__Request
                                        ) -> Schema__Graph__With_Traces__Response__Speedscope:
        graph_response, export = self._execute_with_timestamps(engine, transformation, request)
        traces                 = export.to_speedscope_json()
        response               = self.create_response__speedscope(graph_response, request.trace_config, traces)
        return response
        # return Schema__Graph__With_Traces__Response__Speedscope(graph  = graph_response,
        #                                                         traces = traces        )

    # ═══════════════════════════════════════════════════════════════════════════
    # Internal Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def create_response__full(self                                        ,
                                graph_response: Schema__Graph__Response__Base,
                                trace_config  : Schema__Trace_Config         ,
                                traces        : Schema__Export_Summary
                           ) -> Schema__Graph__With_Traces__Response__Speedscope:
        if trace_config.output == Enum__Trace_Output.traces_only:
            graph = None
        else:
            graph = graph_response
        return Schema__Graph__With_Traces__Response__Full(graph         = graph                       ,
                                                          response_type = Schema__Trace__Response__Type.FULL,
                                                          traces        = traces                               )

    def create_response__summary(self                                        ,
                                graph_response: Schema__Graph__Response__Base,
                                trace_config  : Schema__Trace_Config         ,
                                traces        : Schema__Export_Summary
                           ) -> Schema__Graph__With_Traces__Response__Speedscope:
        if trace_config.output == Enum__Trace_Output.traces_only:
            graph = None
        else:
            graph = graph_response
        return Schema__Graph__With_Traces__Response__Summary(graph         = graph                       ,
                                                             response_type = Schema__Trace__Response__Type.SUMMARY,
                                                             traces        = traces                               )

        response = Schema__Graph__With_Traces__Response__Speedscope(graph         = graph ,
                                                                    response_type = Schema__Trace__Response__Type.SUMMARY,
                                                                    traces        = traces)
        return response
    def create_response__speedscope(self                                         ,
                                    graph_response: Schema__Graph__Response__Base,
                                    trace_config  : Schema__Trace_Config         ,
                                    traces        : str
                               ) -> Schema__Graph__With_Traces__Response__Speedscope:
        if trace_config.output == Enum__Trace_Output.traces_only:
            graph = None
        else:
            graph = graph_response
        response = Schema__Graph__With_Traces__Response__Speedscope(graph         = graph ,
                                                                    response_type = Schema__Trace__Response__Type.SUMMARY,
                                                                    traces        = traces)
        return response

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
