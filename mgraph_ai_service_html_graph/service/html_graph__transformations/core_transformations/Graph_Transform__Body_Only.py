from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base

class Graph_Transform__Body_Only(Graph_Transformation__Base):                            # Body graph only
    name        : str = 'body_only'
    label       : str = 'Body Only'
    description : str = 'Only the body graph, excludes head elements'
