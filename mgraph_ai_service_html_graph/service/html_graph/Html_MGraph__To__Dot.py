from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from mgraph_db.mgraph.MGraph                                                      import MGraph
from mgraph_db.mgraph.actions.MGraph__Screenshot                                  import MGraph__Screenshot
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config import Html_MGraph__Render__Config
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors import Html_MGraph__Render__Colors
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Labels import Html_MGraph__Render__Labels


class Html_MGraph__To__Dot(Type_Safe):                                                            # Exporter to convert Html_MGraph to DOT format
    mgraph : MGraph                                                                               # The MGraph to export
    config : Html_MGraph__Render__Config                                                   # Rendering configuration

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.config is None:
            self.config = Html_MGraph__Render__Config(colors = Html_MGraph__Render__Colors() ,
                                                      labels = Html_MGraph__Render__Labels() )

    def to_string(self) -> str:                                                                   # Convert MGraph to DOT string
        screenshot = MGraph__Screenshot(graph=self.mgraph.graph)                                  # Create screenshot instance

        with screenshot.export().export_dot() as dot:                                             # Get DOT exporter
            self.config.configure_dot_export(dot)                                                 # Apply HTML-aware configuration
            return dot.process_graph()                                                                # Return DOT string

    def to_dot(self) -> str:                                                                      # Alias for to_string
        return self.to_string()