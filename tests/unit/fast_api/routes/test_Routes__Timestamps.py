"""Tests for Routes__Timestamps"""

from unittest                                                                                            import TestCase
from mgraph_ai_service_html_graph.fast_api.routes.Routes__Timestamps                                     import Routes__Timestamps, ROUTES_PATHS__TIMESTAMPS, TAG__ROUTES_TIMESTAMPS
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service                 import Html_Graph__Export__Service
from osbot_utils.helpers.timestamp_capture.schemas.export.Schema__Export_Full                            import Schema__Export_Full
from osbot_utils.helpers.timestamp_capture.schemas.export.Schema__Export_Summary                         import Schema__Export_Summary
from osbot_utils.helpers.timestamp_capture.schemas.speedscope.Schema__Speedscope                         import Schema__Speedscope
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__Trace_Config                                import Schema__Trace_Config
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__Graph__With_Traces__Request                 import Schema__Graph__With_Traces__Request
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__Graph__With_Traces__Response__Full          import Schema__Graph__With_Traces__Response__Full
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__Graph__With_Traces__Response__Summary       import Schema__Graph__With_Traces__Response__Summary
from mgraph_ai_service_html_graph.schemas.timestamps.Schema__Graph__With_Traces__Response__Speedscope    import Schema__Graph__With_Traces__Response__Speedscope
from mgraph_ai_service_html_graph.schemas.timestamps.enums.Enum__Trace_Output                            import Enum__Trace_Output
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Schemas                 import Schema__Graph__From_Html__Request, Schema__Graph__Response__Base, Schema__Graph__Dot__Response
from osbot_utils.testing.__ import __


class test_Routes__Timestamps(TestCase):

    @classmethod
    def setUpClass(cls):                                                                             # Setup shared test objects
        cls.graph_service = Html_Graph__Export__Service()

    def setUp(self):                                                                                 # Create routes instance
        self.routes = Routes__Timestamps(graph_service=self.graph_service)

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                          # Test routes initialization
        with self.routes as _:
            assert _.tag           == TAG__ROUTES_TIMESTAMPS
            assert _.graph_service == self.graph_service

    def test__routes_paths(self):                                                                    # Test route paths are defined
        assert len(ROUTES_PATHS__TIMESTAMPS) == 3
        assert '/timestamps/graph/from/html/to/{engine}/{transformation}/full'       in ROUTES_PATHS__TIMESTAMPS
        assert '/timestamps/graph/from/html/to/{engine}/{transformation}/summary'    in ROUTES_PATHS__TIMESTAMPS
        assert '/timestamps/graph/from/html/to/{engine}/{transformation}/speedscope' in ROUTES_PATHS__TIMESTAMPS

    # ═══════════════════════════════════════════════════════════════════════════
    # Route Handler Tests - Full Format
    # ═══════════════════════════════════════════════════════════════════════════

    def test_from_html_with_traces_full(self):                                                       # Test full trace route
        request = Schema__Graph__With_Traces__Request(
            graph_request = Schema__Graph__From_Html__Request(html           = '<html></html>',
                                                              transformation = 'default'      ),
            trace_config  = Schema__Trace_Config(output=Enum__Trace_Output.both)
        )

        response = self.routes.from_html_with_traces_full(engine         = 'dot'    ,
                                                          transformation = 'default',
                                                          request        = request  )

        assert type(response)        is Schema__Graph__With_Traces__Response__Full
        assert type(response.graph)  is Schema__Graph__Dot__Response
        assert type(response.traces) is Schema__Export_Full
        assert response.graph.engine == 'dot'

    # ═══════════════════════════════════════════════════════════════════════════
    # Route Handler Tests - Summary Format
    # ═══════════════════════════════════════════════════════════════════════════

    def test_from_html_with_traces_summary(self):                                                    # Test summary trace route
        request = Schema__Graph__With_Traces__Request(
            graph_request = Schema__Graph__From_Html__Request(html           = '<p>Test</p>',
                                                              transformation = 'custom'     ),
            trace_config  = Schema__Trace_Config(output=Enum__Trace_Output.traces_only)
        )

        response = self.routes.from_html_with_traces_summary(engine         = 'visjs' ,
                                                             transformation = 'custom',
                                                             request        = request )

        assert type(response)        is Schema__Graph__With_Traces__Response__Summary
        assert type(response.traces) is Schema__Export_Summary
        assert response.traces.name  == 'custom.visjs'                                               # Collector name from params

    # ═══════════════════════════════════════════════════════════════════════════
    # Route Handler Tests - Speedscope Format
    # ═══════════════════════════════════════════════════════════════════════════

    def test_from_html_with_traces_speedscope(self):                                                 # Test speedscope trace route
        request = Schema__Graph__With_Traces__Request(
            graph_request = Schema__Graph__From_Html__Request(html           = '<div></div>',
                                                              transformation = 'perf'       ),
            trace_config  = Schema__Trace_Config(output=Enum__Trace_Output.traces_only)
        )

        response = self.routes.from_html_with_traces_speedscope(engine         = 'd3'  ,
                                                                transformation = 'perf',
                                                                request        = request)

        assert type(response)        is Schema__Graph__With_Traces__Response__Speedscope
        assert type(response.traces) is str

    # ═══════════════════════════════════════════════════════════════════════════
    # Engine Method Resolution Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__get_render_method__dot(self):                                                          # Test dot engine resolution
        method = self.routes._get_render_method('dot')
        assert method == self.graph_service.to_dot

    def test__get_render_method__default(self):                                                      # Test default engine resolution
        method = self.routes._get_render_method('default')
        assert method == self.graph_service.to_dot

    def test__get_render_method__visjs(self):                                                        # Test visjs engine resolution
        method = self.routes._get_render_method('visjs')
        assert method == self.graph_service.to_visjs

    def test__get_render_method__d3(self):                                                           # Test d3 engine resolution
        method = self.routes._get_render_method('d3')
        assert method == self.graph_service.to_d3

    def test__get_render_method__cytoscape(self):                                                    # Test cytoscape engine resolution
        method = self.routes._get_render_method('cytoscape')
        assert method == self.graph_service.to_cytoscape

    def test__get_render_method__mermaid(self):                                                      # Test mermaid engine resolution
        method = self.routes._get_render_method('mermaid')
        assert method == self.graph_service.to_mermaid

    def test__get_render_method__tree(self):                                                         # Test tree engine resolution
        method = self.routes._get_render_method('tree')
        assert method == self.graph_service.to_tree

    def test__get_render_method__unknown(self):                                                      # Test unknown engine raises error
        with self.assertRaises(ValueError) as context:
            self.routes._get_render_method('unknown_engine')
        assert 'Unknown graph engine: unknown_engine' in str(context.exception)

    # ═══════════════════════════════════════════════════════════════════════════
    # Route Setup Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_setup_routes(self):                                                                     # Test route registration
        with Routes__Timestamps(graph_service=self.graph_service) as _:
            result = _.setup_routes()
            assert result is _                                                                       # Returns self for chaining

    # ═══════════════════════════════════════════════════════════════════════════
    # Tests with bigger HTML
    # ═══════════════════════════════════════════════════════════════════════════
