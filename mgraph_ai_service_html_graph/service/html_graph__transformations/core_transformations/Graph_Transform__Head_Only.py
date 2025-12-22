from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph import Html_MGraph
from mgraph_db.mgraph.MGraph import MGraph
from osbot_utils.type_safe.type_safe_core.decorators.type_safe import type_safe


class Graph_Transform__Head_Only(Graph_Transformation__Base):                            # Head graph only
    name        : str = 'head_only'
    label       : str = 'Head Only'
    description : str = 'Only the head graph (meta, title, links, etc.)'

    @type_safe
    def html_mgraph__to__mgraph(self, html_mgraph : Html_MGraph                         # Select head graph
                                ) -> MGraph:
        if html_mgraph:
            return html_mgraph.head_graph.mgraph
        return None
