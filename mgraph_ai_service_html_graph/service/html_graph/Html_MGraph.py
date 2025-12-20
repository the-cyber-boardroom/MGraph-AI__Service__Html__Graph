from typing                                                                     import Dict, Any, List, Optional

from osbot_utils.helpers.html.transformers.Html_Dict__To__Html import Html_Dict__To__Html
from osbot_utils.testing.__helpers import obj
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id               import Node_Id
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph__To__Html_Dict import Html_MGraph__To__Html_Dict
from mgraph_db.mgraph.schemas.identifiers.Node_Path                             import Node_Path
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from mgraph_db.mgraph.MGraph                                                    import MGraph
from mgraph_ai_service_html_graph.service.html_graph.Html_Dict__To__Html_MGraph import Html_Dict__To__Html_MGraph, Schema__Config__Html_Dict__To__Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph__Path          import Html_MGraph__Path
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html import Safe_Str__Html


class Html_MGraph(Type_Safe):                                                   # Main interface for HTML Graph operations
    mgraph     : MGraph            = None                                       # The underlying MGraph
    path_utils : Html_MGraph__Path = None                                       # Path computation utilities
    root_id    : Node_Id           = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.path_utils is None:
            self.path_utils = Html_MGraph__Path()

    @classmethod
    def from_html_dict(cls,                                                                             # Create Html_MGraph from Html__Dict
                       html_dict: Dict[str, Any],
                       config: Schema__Config__Html_Dict__To__Html_MGraph=None
                 ) -> 'Html_MGraph':
        converter = Html_Dict__To__Html_MGraph(config=config)
        mgraph    = converter.convert(html_dict)
        return cls(mgraph=mgraph, root_id=converter.root_id)

    # todo: implement this via: Html_MGraph__To__Html
    # def to__html(self) -> Safe_Str__Html:
    #     html_dict = self.to__html_dict()
    #     html      = Html_Dict__To__Html(root=html_dict).convert()
    #     return html

    def to__html_dict(self) -> Dict[str, Any]:                                   # Convert back to Html__Dict
        converter = Html_MGraph__To__Html_Dict()
        return converter.convert(self.mgraph)

    def to__json(self):
        return self.mgraph.export().to__json()

    def to__obj(self):
        return obj(self.to__json())
    # ═══════════════════════════════════════════════════════════════════════════════
    # Query Methods
    # ═══════════════════════════════════════════════════════════════════════════════
    # todo: look at the side effects caused by the fact that we could have multiple nodes mapped to the name dom_path
    #       and this is only returning the first one
    def get_element_by_path(self, dom_path: str) -> Optional[str]:                  # Get element node ID by DOM path
        node_ids = self.mgraph.index().get_nodes_by_path(Node_Path(dom_path))
        return next(iter(node_ids), None) if node_ids else None

    def get_elements_by_tag(self, tag: str) -> List[str]:
        tag_path     = self.path_utils.value_node_path('tag', tag)
        tag_node_ids = self.mgraph.index().get_nodes_by_path(Node_Path(tag_path))

        if not tag_node_ids:
            return []

        tag_node_id = next(iter(tag_node_ids))                                  # Convert set to get first element
        element_ids = []
        edge_ids    = self.mgraph.index().get_node_id_incoming_edges(tag_node_id)

        for edge_id in edge_ids:
            edge = self.mgraph.data().edge(edge_id)
            if edge:
                predicate = self.get_edge_predicate(edge.edge.data)
                if predicate == 'tag':
                    element_ids.append(str(edge.edge.data.from_node_id))

        return element_ids

    def get_elements_with_attribute(self, attr_name  : str                  ,   # Attribute name
                                          attr_value : Optional[str] = None ) -> List[str]:  # Optional value to filter by
        element_ids = []

        for edge_id in self.mgraph.data().edges_ids():                          # Search through all edges with predicate 'attr' and edge_path matching attr_name
            edge = self.mgraph.data().edge(edge_id).edge
            if edge:
                predicate = self.get_edge_predicate(edge.data)
                edge_path = self.get_edge_path(edge.data)

                if predicate == 'attr' and edge_path == attr_name:
                    if attr_value is not None:                                  # Check value if specified
                        value = self.get_value_node_content(edge.data.to_node_id)
                        if value != attr_value:
                            continue

                    element_ids.append(str(edge.data.from_node_id))

        return element_ids

    def get_text_content(self, element_node_id : str          ,                 # Node ID of the element
                               recursive       : bool = False ) -> str:         # If True, include text from descendants
        node = self.mgraph.graph.node(element_node_id)
        if not node:
            return ''

        content_items = []                                                      # Collect content with positions
        edge_ids = self.mgraph.index().get_node_id_outgoing_edges(element_node_id)  # Use index

        for edge_id in edge_ids:

            edge = self.mgraph.data().edge(edge_id).edge
            if edge:
                predicate = self.get_edge_predicate(edge.data)

                if predicate == 'text':                                         # Only text edges have numeric position
                    edge_path = self.get_edge_path(edge.data)
                    position  = int(edge_path) if edge_path else 0
                    text      = self.get_value_node_content(edge.data.to_node_id)
                    content_items.append((position, 'text', text))

                elif predicate == 'child' and recursive:                        # Only child edges have numeric position
                    edge_path  = self.get_edge_path(edge.data)
                    position   = int(edge_path) if edge_path else 0
                    child_text = self.get_text_content(str(edge.data.to_node_id), recursive=True)
                    content_items.append((position, 'child', child_text))

        content_items.sort(key=lambda x: x[0])                                  # Sort by position and concatenate
        text_parts = [item[2] for item in content_items if item[2]]

        return ' '.join(text_parts)

    def get_element_tag(self, element_node_id: str) -> str:                     # Get the tag name of an element
        node = self.mgraph.graph.node(element_node_id)
        if not node:
            return ''
        edge_ids = self.mgraph.index().get_node_id_outgoing_edges(element_node_id)  # Use index

        for edge_id in edge_ids:
            edge = self.mgraph.data().edge(edge_id).edge
            if edge:
                predicate = self.get_edge_predicate(edge.data)
                if predicate == 'tag':
                    return self.get_value_node_content(edge.data.to_node_id)

        return ''

    def get_element_attributes(self, element_node_id: str) -> Dict[str, str]:   # Get all attributes of an element
        attrs = {}
        node  = self.mgraph.graph.node(element_node_id)

        if not node:
            return attrs

        edge_ids = self.mgraph.index().get_node_id_outgoing_edges(element_node_id)  # Use index

        for edge_id in edge_ids:
            edge = self.mgraph.data().edge(edge_id).edge
            if edge:
                predicate = self.get_edge_predicate(edge.data)
                edge_path = self.get_edge_path(edge.data)

                if predicate == 'attr' and edge_path:
                    attrs[edge_path] = self.get_value_node_content(edge.data.to_node_id)

        return attrs

    def get_children(self, element_node_id: str) -> List[str]:                  # Get child element node IDs in order
        children = []
        node     = self.mgraph.graph.node(element_node_id)

        if not node:
            return children

        children_with_pos = []

        edge_ids = self.mgraph.index().get_node_id_outgoing_edges(element_node_id)  # Use index

        for edge_id in edge_ids:
            edge = self.mgraph.data().edge(edge_id).edge
            if edge:
                predicate = self.get_edge_predicate(edge.data)
                edge_path = self.get_edge_path(edge.data)

                if predicate == 'child':
                    position = int(edge_path) if edge_path else 0
                    children_with_pos.append((position, str(edge.data.to_node_id)))

        children_with_pos.sort(key=lambda x: x[0])                              # Sort by position
        return [child_id for _, child_id in children_with_pos]

    # ═══════════════════════════════════════════════════════════════════════════════
    # Stats Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def stats(self) -> Dict[str, Any]:                                          # Get statistics about the HTML graph
        total_nodes = len(list(self.mgraph.data().nodes_ids()))
        total_edges = len(list(self.mgraph.data().edges_ids()))

        element_count = 0                                                       # Count by type
        value_count   = 0
        tag_count     = 0
        text_count    = 0
        attr_count    = 0

        for node_id in self.mgraph.data().nodes_ids():
            node = self.mgraph.data().node(node_id).node
            if node:
                node_path = str(node.data.node_path) if node.data.node_path else ''

                if node_path.startswith('tag:'):
                    tag_count   += 1
                    value_count += 1
                elif node_path.startswith('attr:'):
                    attr_count  += 1
                    value_count += 1
                elif node_path == 'text':
                    text_count  += 1
                    value_count += 1
                else:
                    element_count += 1

        return { 'total_nodes'   : total_nodes   ,
                 'total_edges'   : total_edges   ,
                 'element_nodes' : element_count ,
                 'value_nodes'   : value_count   ,
                 'tag_nodes'     : tag_count     ,
                 'text_nodes'    : text_count    ,
                 'attr_nodes'    : attr_count    }

    # ═══════════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_edge_predicate(self, edge) -> Optional[str]:                        # Get predicate from edge
        if hasattr(edge, 'edge_label') and edge.edge_label:
            label = edge.edge_label
            if hasattr(label, 'predicate') and label.predicate:
                return str(label.predicate)
        return None

    def get_edge_path(self, edge) -> Optional[str]:                             # Get edge_path from edge
        if hasattr(edge, 'edge_path') and edge.edge_path:
            return str(edge.edge_path)
        return None

    def get_value_node_content(self, node_id) -> str:                           # Get value from a value node
        node = self.mgraph.data().node(str(node_id)).node
        if node and hasattr(node.data, 'node_data'):
            node_data = node.data.node_data
            if hasattr(node_data, 'value'):
                return node_data.value
        return ''