from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                import Html_MGraph
from mgraph_db.mgraph.MGraph                                                                     import MGraph
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                   import type_safe


class Graph_Transform__Full_Document(Graph_Transformation__Base):                             # Full document graph
    name        : str = 'full-document'
    label       : str = 'Full Document'
    description : str = 'Complete document including head and body'

    @type_safe
    def html_mgraph__to__mgraph(self,                                                       # Expand document graph
                                html_mgraph : Html_MGraph
                                ) -> MGraph:
        return html_mgraph.document.mgraph