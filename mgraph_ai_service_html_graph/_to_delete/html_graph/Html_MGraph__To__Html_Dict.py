from typing                                                            import Dict, Any, Optional, List
from osbot_utils.type_safe.Type_Safe                                   import Type_Safe
from mgraph_db.mgraph.MGraph                                           import MGraph
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph__Path import Html_MGraph__Path


class Html_MGraph__To__Html_Dict(Type_Safe):                                    # Convert Html_MGraph back to Html__Dict for round-trip capability
    mgraph     : MGraph            = None                                       # The MGraph to convert
    path_utils : Html_MGraph__Path = None                                       # Path computation utilities

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.path_utils is None:
            self.path_utils = Html_MGraph__Path()

    def convert(self, mgraph: MGraph) -> Dict[str, Any]:                        # Convert Html_MGraph to Html__Dict
        self.mgraph = mgraph

        root_node_id = self.find_root_element()                                 # Find root element node
        if not root_node_id:
            return {}

        return self.convert_node(root_node_id)                                  # Recursively convert from root

    def find_root_element(self) -> Optional[str]:                               # Find the root element node (node with shortest path / no parent)
        element_nodes = []

        for node_id in self.mgraph.data().nodes_ids():                          # Get all element nodes (non-value nodes)
            node = self.mgraph.data().node(node_id).node
            if node:
                node_type = type(node.data).__name__                            # Element nodes are Schema__MGraph__Node but not Schema__MGraph__Node__Value
                if 'Value' not in node_type:
                    node_path = node.data.node_path
                    if node_path:
                        element_nodes.append((node_id, str(node_path)))

        if not element_nodes:
            return None

        element_nodes.sort(key=lambda x: self.path_utils.get_depth(x[1]))       # Find node with shortest path (root)
        return element_nodes[0][0]

    def convert_node(self, node_id: str) -> Dict[str, Any]:                     # Convert a single element node to Html__Dict format
        result = { 'tag'        : self.get_tag(node_id)        ,
                   'attrs'      : self.get_attributes(node_id) ,
                   'child_nodes': []                           ,
                   'text_nodes' : []                           }

        edges             = self.get_outgoing_edges(node_id)                    # Get all outgoing edges from this element
        children_with_pos = []                                                  # Collect children and text with positions
        text_with_pos     = []

        for edge in edges:
            predicate = self.get_edge_predicate(edge)
            edge_path = self.get_edge_path(edge)
            to_node   = edge.to_node_id

            if predicate == 'child':                                            # Child element - recurse
                position   = int(edge_path) if edge_path else 0
                child_dict = self.convert_node(str(to_node))
                child_dict['position'] = position
                children_with_pos.append((position, child_dict))

            elif predicate == 'text':                                           # Text content
                position  = int(edge_path) if edge_path else 0
                text_data = self.get_value(to_node)
                text_with_pos.append((position, {'data': text_data, 'position': position}))

        children_with_pos.sort(key=lambda x: x[0])                              # Sort by position and add to result
        text_with_pos.sort(key=lambda x: x[0])

        result['child_nodes'] = [child for _, child in children_with_pos]
        result['text_nodes']  = [text for _, text in text_with_pos]

        return result

    def get_tag(self, node_id: str) -> str:                                     # Get the HTML tag for an element node
        edges = self.get_outgoing_edges(node_id)

        for edge in edges:
            predicate = self.get_edge_predicate(edge)
            if predicate == 'tag':
                return self.get_value(edge.to_node_id)

        return 'unknown'

    def get_attributes(self, node_id: str) -> Dict[str, str]:                   # Get all attributes for an element node
        attrs = {}
        edges = self.get_outgoing_edges(node_id)

        for edge in edges:
            predicate = self.get_edge_predicate(edge)
            if predicate == 'attr':
                attr_name  = self.get_edge_path(edge)
                attr_value = self.get_value(edge.to_node_id)
                if attr_name:
                    attrs[attr_name] = attr_value

        return attrs

    def get_outgoing_edges(self, node_id: str) -> List:
        edges = []
        edge_ids = self.mgraph.index().get_node_id_outgoing_edges(node_id)

        for edge_id in edge_ids:
            edge = self.mgraph.data().edge(edge_id)
            if edge:
                edges.append(edge.edge.data)

        return edges

    def get_edge_predicate(self, edge) -> Optional[str]:                        # Get the predicate from an edge
        if hasattr(edge, 'edge_label') and edge.edge_label:
            label = edge.edge_label
            if hasattr(label, 'predicate') and label.predicate:
                return str(label.predicate)
        return None

    def get_edge_path(self, edge) -> Optional[str]:                             # Get the edge_path from an edge
        if hasattr(edge, 'edge_path') and edge.edge_path:
            return str(edge.edge_path)
        return None

    def get_value(self, node_id) -> str:                                        # Get the value from a value node
        node_id_str = str(node_id)
        node        = self.mgraph.data().node(node_id_str).node

        if node and hasattr(node.data, 'node_data'):
            node_data = node.data.node_data
            if hasattr(node_data, 'value'):
                return node_data.value

        return ''