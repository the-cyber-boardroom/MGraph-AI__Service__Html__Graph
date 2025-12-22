from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                import Html_MGraph
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Dot    import MGraph__Engine__Config__Dot
from mgraph_db.mgraph.MGraph                                                                     import MGraph
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                   import type_safe


class Graph_Transform__Attributes(Graph_Transformation__Base):                           # Attributes view
    name        : str = 'attributes'
    label       : str = 'Attributes View'
    description : str = 'Focus on element attributes'

    @type_safe
    def html_mgraph__to__mgraph(self,                                                    # Select attributes graph
                                html_mgraph: Html_MGraph
                            )-> MGraph:
        return html_mgraph.attrs_graph.mgraph

    # Phase 3: MGraph → MGraph (transformation)

    # # todo: debug workflow and see why .export_dot()  is not being used in the configuration
    # def transform_mgraph(self, mgraph):                                                  # Transform the graph
    #     export : MGraph__Export = mgraph.export()
    #     with export.export_dot() as _:
    #         _.set_graph__rank_dir__lr()
    #     return mgraph                                                                    # Default: no-op passthrough

    def configure_dot(self, config: MGraph__Engine__Config__Dot                          # Horizontal layout for attrs
                     ) -> MGraph__Engine__Config__Dot:
        with config as _:
            #_.rankdir        = 'LR'
            _.node_shape     = 'ellipse'
            _.node_fillcolor = '#e8f0e8'
        return config