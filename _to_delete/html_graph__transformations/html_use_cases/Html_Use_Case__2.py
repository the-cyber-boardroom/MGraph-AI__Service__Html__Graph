from typing import Dict, Any, List
from mgraph_ai_service_html_graph.service.html_graph.Html_Dict__To__Html_MGraph                  import Schema__Config__Html_Dict__To__Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph                                 import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base
from mgraph_db.mgraph.schemas.Schema__MGraph__Node import Schema__MGraph__Node
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id import Node_Id
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict import Type_Safe__Dict
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List import Type_Safe__List
from osbot_utils.type_safe.type_safe_core.decorators.type_safe import type_safe


class Html_Use_Case__2(Graph_Transformation__Base):
    name        : str = "html_use_case__2"
    label       : str = "Html Use Case 2"
    description : str = "This is the Html Use Case 2"

    # Phase 3: MGraph Creation
    def create_mgraph(self, html_dict: Dict[str, Any], config: Any):                # Create Html_MGraph from dict
        with Schema__Config__Html_Dict__To__Html_MGraph() as config:
            config.add_tag_nodes       = False
            config.add_attribute_nodes = False

        return Html_MGraph.from_html_dict(html_dict=html_dict, config=config)

    # Phase 4: MGraph Transformation
    # def transform_mgraph(self, html_mgraph):
    #     print()
    #     # index = html_mgraph.mgraph.index()
    #     # index.print_obj()
    #     edit = html_mgraph.mgraph.edit()
    #     for node in self.text_nodes(html_mgraph):
    #         node_id = node.node_id
    #         parent_node_id       = self.get_parent_node_id(html_mgraph,node_id       )
    #         grand_parent_node_id = self.get_parent_node_id(html_mgraph,parent_node_id)
    #         print(node_id, ' -> ', parent_node_id , ' -> ', grand_parent_node_id)
    #
    #         #edit.new_edge(from_node_id=grand_parent_node_id, to_node_id=node_id)
    #
    #     #     node.node_path = node.node_id
    #
    #     return html_mgraph

    def transform_mgraph(self, html_mgraph):
        self.collapse_single_child_parents(html_mgraph)
        self.merge_text_children(html_mgraph)
        # self.clear_text_node_paths(html_mgraph)
        return html_mgraph

    # ---- Graph Traversal Utilities ----

    # def get_parent_node_id(self, html_mgraph, node_id):
    #     index = html_mgraph.mgraph.index()
    #     incoming_edges = index.get_node_id_incoming_edges(node_id)
    #     if incoming_edges:
    #         edge_id = next(iter(incoming_edges))
    #         from_node_id, _ = index.edges_to_nodes()[edge_id]
    #         return from_node_id
    #     return None

    def get_incoming_edge_path(self, html_mgraph, node_id):
        index = html_mgraph.mgraph.index()
        incoming_edges = index.get_node_id_incoming_edges(node_id)
        if incoming_edges:
            edge_id = next(iter(incoming_edges))
            edge = html_mgraph.mgraph.data().edge(edge_id)
            return edge.edge_path
        return None

    def get_outgoing_edge_count(self, html_mgraph, node_id):
        index = html_mgraph.mgraph.index()
        outgoing_edges = index.get_node_id_outgoing_edges(node_id)
        return len(outgoing_edges) if outgoing_edges else 0

    def is_single_child_parent(self, html_mgraph, node_id):
        return self.get_outgoing_edge_count(html_mgraph, node_id) == 1

    # ---- Graph Modification Utilities ----

    def create_edge_with_path(self, html_mgraph, from_node_id, to_node_id, edge_path):
        edit = html_mgraph.mgraph.edit()
        edit.new_edge(
            from_node_id = from_node_id,
            to_node_id   = to_node_id,
            edge_path    = edge_path
        )

    def delete_nodes(self, html_mgraph, node_ids):
        edit = html_mgraph.mgraph.edit()
        for node_id in set(node_ids):
            edit.delete_node(node_id)

    # ---- Text Node Utilities ----

    def clear_text_node_paths(self, html_mgraph):
        for node in self.text_nodes(html_mgraph):
            node.node_path = ''

    # ---- Transform Operations ----

    def collapse_single_child_parents(self, html_mgraph):
        """Remove pass-through parent nodes that have only one child,
           connecting grandparent directly to text node."""
        nodes_to_delete = []

        for node in self.text_nodes(html_mgraph):
            node_id              = node.node_id
            parent_node_id       = self.get_parent_node_id(html_mgraph, node_id)
            grand_parent_node_id = self.get_parent_node_id(html_mgraph, parent_node_id)

            if self.is_single_child_parent(html_mgraph, parent_node_id):
                edge_path = self.get_incoming_edge_path(html_mgraph, parent_node_id)
                self.create_edge_with_path(html_mgraph, grand_parent_node_id, node_id, edge_path)
                nodes_to_delete.append(parent_node_id)

        self.delete_nodes(html_mgraph, nodes_to_delete)


    # ---- New Utilities ----

    def get_text_children_ordered(self, html_mgraph, parent_node_id):
        """Get all text child nodes of a parent, sorted by edge_path."""
        index = html_mgraph.mgraph.index()
        outgoing_edges = index.get_node_id_outgoing_edges(parent_node_id)

        if not outgoing_edges:
            return []

        children = []
        for edge_id in outgoing_edges:
            edge = html_mgraph.mgraph.data().edge(edge_id)
            _, to_node_id = index.edges_to_nodes()[edge_id]
            node = html_mgraph.mgraph.data().node(to_node_id)

            # Check if it's a text/value node
            if hasattr(node, 'node_data') and hasattr(node.node_data, 'value'):
                edge_path = edge.edge_path or '0'
                children.append({
                    'node_id'  : to_node_id,
                    'node'     : node,
                    'value'    : node.node_data.value,
                    'edge_path': int(edge_path) if edge_path.isdigit() else 0
                })

        return sorted(children, key=lambda x: x['edge_path'])

    def get_parent_nodes_with_text_children(self, html_mgraph):
        """Find all non-text nodes that have text children."""
        parent_ids = set()
        for node in self.text_nodes(html_mgraph):
            parent_id = self.get_parent_node_id(html_mgraph, node.node_id)
            if parent_id:
                parent_ids.add(parent_id)
        return sorted(parent_ids)

    def create_merged_text_node(self, html_mgraph, parent_node_id, merged_value):
        """Create a new text node with merged value and link to parent."""
        edit = html_mgraph.mgraph.edit()
        node_path = 'text'
        edge_path = '0'
        new_node = edit.new_value(merged_value, node_path=node_path)
        edit.new_edge(
            from_node_id = parent_node_id,
            to_node_id   = new_node.node_id,
            edge_path    = edge_path
        )
        return new_node

    # ---- Transform Operation ----

    def merge_text_children(self, html_mgraph):
        """Merge all text children of each parent into a single concatenated text node."""
        parent_ids = self.get_parent_nodes_with_text_children(html_mgraph)

        for parent_id in parent_ids:
            children = self.get_text_children_ordered(html_mgraph, parent_id)

            if len(children) <= 1:
                continue  # Nothing to merge

            # Concatenate values in order
            merged_value = ''.join(child['value'] for child in children)
            merged_value  = merged_value.strip()                                     # todo: see if we should make this configurable (the trimming of the new text value)

            # Collect node IDs to delete
            nodes_to_delete = [child['node_id'] for child in children]

            # Delete old text nodes
            self.delete_nodes(html_mgraph, nodes_to_delete)

            # Create new merged node
            self.create_merged_text_node(html_mgraph, parent_id, merged_value)



    # helpers

    def nodes(self, html_mgraph):
        return html_mgraph.mgraph.graph.model.data.nodes.values()

    @type_safe
    def text_nodes(self, html_mgraph) -> List[Schema__MGraph__Node]:        # todo: BUG is OSBot_Utils , this should be: Type_Safe__List[Schema__MGraph__Node]
        text_nodes = Type_Safe__List(expected_type=Schema__MGraph__Node)
        for node in self.nodes(html_mgraph):
            if node.node_path=='text':
                text_nodes.append(node)
        return text_nodes

    def get_parent_node_id(self, html_mgraph, text_node_id):
        index = html_mgraph.mgraph.index()

        # Get incoming edges to this text node
        incoming_edges = index.get_node_id_incoming_edges(text_node_id)

        if incoming_edges:
            # Get the first incoming edge (text nodes typically have one parent)
            edge_id = next(iter(incoming_edges))

            # Get from_node_id from edge
            edges_to_nodes = index.edges_to_nodes()
            from_node_id, to_node_id = edges_to_nodes[edge_id]
            return from_node_id

        return None