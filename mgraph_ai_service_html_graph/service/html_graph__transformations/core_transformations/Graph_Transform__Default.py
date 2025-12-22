from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base


class Graph_Transform__Default(Graph_Transformation__Base):                              # Default: body graph
    name        : str = 'default'
    label       : str = 'Default'
    description : str = 'Standard body graph visualization'
