from typing                                                                         import Dict, Any, List, Optional, Type
from mgraph_ai_service_html_graph.schemas.html.Schema__Html_MGraph                  import Schema__Html_MGraph__Stats__Base, Schema__Html_MGraph__Json__Base
from mgraph_db.mgraph.MGraph                                                        import MGraph
from mgraph_db.mgraph.schemas.Schema__MGraph__Node                                  import Schema__MGraph__Node
from mgraph_db.mgraph.schemas.Schema__MGraph__Edge__Label                           import Schema__MGraph__Edge__Label
from mgraph_db.mgraph.schemas.identifiers.Node_Path                                 import Node_Path
from mgraph_db.mgraph.schemas.identifiers.Edge_Path                                 import Edge_Path
from mgraph_db.mgraph.domain.Domain__MGraph__Edge                                   import Domain__MGraph__Edge
from mgraph_db.mgraph.domain.Domain__MGraph__Node                                   import Domain__MGraph__Node
from osbot_utils.helpers.timestamp_capture.decorators.timestamp                     import timestamp
from osbot_utils.helpers.timestamp_capture.decorators.timestamp_args import timestamp_args
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                   import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id                   import Safe_Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                      import type_safe


class Html_MGraph__Base(Type_Safe):                                             # Base class for all Html_MGraph specialized graphs
    mgraph  : MGraph  = None                                                    # The underlying MGraph
    root_id : Node_Id = None                                                    # Root node ID for this graph

    @timestamp_args(name="html_mgraph.{self.__class__.__name__}.setup")
    def setup(self) -> 'Html_MGraph__Base':                                     # Initialize the graph with a fresh MGraph instance
        self.mgraph = MGraph()
        root_node   = self.new_element_node(node_path='')                       # Create root node for this graph
        self.root_id = root_node.node_id
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # Node Creation Methods
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def new_element_node(self, node_path : Node_Path         ,                  # DOM path for element
                               node_id   : Node_Id    = None                    # Optional specific node_id
                        ) -> Domain__MGraph__Node:                              # Create element node with path
        if node_id:
            return self.mgraph.edit().new_node(node_type = Schema__MGraph__Node ,
                                               node_path = node_path            ,
                                               node_id   = node_id              )
        return self.mgraph.edit().new_node(node_type = Schema__MGraph__Node ,
                                           node_path = node_path            )

    @type_safe
    def new_value_node(self, value     : str                ,                   # Value to store
                             node_path : Node_Path   = None ,                   # Optional path
                             key       : str         = ''                       # Optional unique key
                      ) -> Domain__MGraph__Node:                                # Create value node
        return self.mgraph.edit().new_value(value     = value     ,
                                            node_path = node_path ,
                                            key       = key       )

    # ═══════════════════════════════════════════════════════════════════════════
    # Edge Creation Methods
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def new_edge(self, from_node_id : Node_Id             ,                     # Source node
                       to_node_id   : Node_Id             ,                     # Target node
                       predicate    : Safe_Id      = None ,                     # Semantic relationship type
                       edge_path    : Edge_Path    = None                       # Optional position/path
                ) -> Domain__MGraph__Edge:                                      # Create edge with optional predicate
        edge = self.mgraph.edit().new_edge(from_node_id = from_node_id ,
                                           to_node_id   = to_node_id   ,
                                           edge_path    = edge_path    )
        if predicate:
            edge.edge.data.edge_label = Schema__MGraph__Edge__Label(predicate=predicate)
        return edge

    # ═══════════════════════════════════════════════════════════════════════════
    # Node Query Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def node(self, node_id: Node_Id) -> Optional[Domain__MGraph__Node]:         # Get node by ID
        return self.mgraph.data().node(str(node_id))

    def node_value(self, node_id: Node_Id) -> Optional[str]:                    # Get value from a value node
        node = self.node(node_id)
        if node and hasattr(node.node, 'data'):
            node_data = node.node.data
            if hasattr(node_data, 'node_data') and hasattr(node_data.node_data, 'value'):
                return node_data.node_data.value
        return None

    def node_path(self, node_id: Node_Id) -> Optional[Node_Path]:               # Get path from a node
        node = self.node(node_id)
        if node and hasattr(node.node, 'data'):
            return node.node.data.node_path
        return None

    def nodes_ids(self) -> List[Node_Id]:                                       # Get all node IDs
        return list(self.mgraph.data().nodes_ids())

    def nodes_by_path(self, path: Node_Path) -> List[Node_Id]:                  # Get nodes by path
        node_ids = self.mgraph.index().get_nodes_by_path(path)
        return list(node_ids) if node_ids else []

    # ═══════════════════════════════════════════════════════════════════════════
    # Edge Query Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def outgoing_edges(self, node_id: Node_Id) -> List[Domain__MGraph__Edge]:   # Get outgoing edges from a node
        edge_ids = self.mgraph.index().get_node_id_outgoing_edges(str(node_id))
        edges    = []
        for edge_id in (edge_ids or []):
            edge = self.mgraph.data().edge(edge_id)
            if edge:
                edges.append(edge)
        return edges

    def incoming_edges(self, node_id: Node_Id) -> List[Domain__MGraph__Edge]:   # Get incoming edges to a node
        edge_ids = self.mgraph.index().get_node_id_incoming_edges(str(node_id))
        edges    = []
        for edge_id in (edge_ids or []):
            edge = self.mgraph.data().edge(edge_id)
            if edge:
                edges.append(edge)
        return edges

    def edge_predicate(self, edge: Domain__MGraph__Edge) -> Optional[Safe_Id]:  # Get predicate from edge
        if hasattr(edge.edge, 'data') and hasattr(edge.edge.data, 'edge_label'):
            label = edge.edge.data.edge_label
            if label and hasattr(label, 'predicate'):
                return label.predicate
        return None

    def edge_path(self, edge: Domain__MGraph__Edge) -> Optional[Edge_Path]:     # Get edge_path from edge
        if hasattr(edge.edge, 'data') and hasattr(edge.edge.data, 'edge_path'):
            return edge.edge.data.edge_path
        return None

    # ═══════════════════════════════════════════════════════════════════════════
    # Traversal Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def get_parent(self, node_id: Node_Id) -> Optional[Node_Id]:                # Get parent node ID (first incoming edge source)
        edges = self.incoming_edges(node_id)
        if edges:
            return edges[0].edge.data.from_node_id
        return None

    def get_children(self, node_id  : Node_Id             ,                     # Get child node IDs with optional predicate filter
                           predicate: Safe_Id      = None
                    ) -> List[Node_Id]:
        children = []
        edges    = self.outgoing_edges(node_id)
        for edge in edges:
            if predicate is None or self.edge_predicate(edge) == predicate:
                children.append(edge.edge.data.to_node_id)
        return children

    def get_children_ordered(self, node_id  : Node_Id             ,             # Get children ordered by edge_path (position)
                                   predicate: Safe_Id      = None
                            ) -> List[Node_Id]:
        children_with_pos = []
        edges             = self.outgoing_edges(node_id)

        for edge in edges:
            if predicate is None or self.edge_predicate(edge) == predicate:
                edge_path = self.edge_path(edge)
                position  = int(str(edge_path)) if edge_path else 0
                children_with_pos.append((position, edge.edge.data.to_node_id))

        children_with_pos.sort(key=lambda x: x[0])
        return [child_id for _, child_id in children_with_pos]

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Methods - Returns Type_Safe Schema
    # ═══════════════════════════════════════════════════════════════════════════

    def stats(self) -> Schema__Html_MGraph__Stats__Base:                        # Get basic statistics about the graph
        return Schema__Html_MGraph__Stats__Base(total_nodes = len(list(self.mgraph.data().nodes_ids())) ,
                                                total_edges = len(list(self.mgraph.data().edges_ids())) ,
                                                root_id     = self.root_id                              )

    # ═══════════════════════════════════════════════════════════════════════════
    # Serialization Methods - Returns Type_Safe Schema
    # ═══════════════════════════════════════════════════════════════════════════
    def to_json(self) -> Dict:
        return self.to_json_base().json()

    def to_json_base(self) -> Schema__Html_MGraph__Json__Base:                       # Export graph to JSON Schema
        raw_json  = self.mgraph.export().to__json()
        json_base = Schema__Html_MGraph__Json__Base(nodes   = raw_json.get('nodes', {})     ,
                                                    edges   = raw_json.get('edges', {})     ,
                                                    root_id = str(self.root_id) if self.root_id else None)
        return json_base