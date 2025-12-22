from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                import Html_MGraph
from mgraph_db.mgraph.MGraph                                                                     import MGraph
from osbot_utils.type_safe.type_safe_core.decorators.type_safe import type_safe


class Graph_Transform__Styles(Graph_Transformation__Base):                               # Styles graph
    name        : str = 'styles'
    label       : str = 'Styles'
    description : str = 'Style elements and their content'

    @type_safe
    def html_mgraph__to__mgraph(self, html_mgraph : Html_MGraph                         # Select styles graph
                                ) -> MGraph:
        return html_mgraph.styles_graph.mgraph