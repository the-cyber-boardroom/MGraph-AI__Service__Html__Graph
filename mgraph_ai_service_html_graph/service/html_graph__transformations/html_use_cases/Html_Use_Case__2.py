from typing                                                                                      import Dict, Any
from mgraph_ai_service_html_graph.service.html_graph.Html_Dict__To__Html_MGraph                  import Schema__Config__Html_Dict__To__Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph                                 import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base


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
        edit  = html_mgraph.mgraph.edit()
        index = html_mgraph.mgraph.index()

        nodes_to_delete = []


        for node in self.text_nodes(html_mgraph):
            node_id              = node.node_id
            parent_node_id       = self.get_parent_node_id(html_mgraph, node_id)
            grand_parent_node_id = self.get_parent_node_id(html_mgraph, parent_node_id)

            parent_outgoing_edges = index.get_node_id_outgoing_edges(parent_node_id)

            if parent_outgoing_edges and len(parent_outgoing_edges) == 1:
                # Get the edge_path from grandparent -> parent edge
                parent_incoming_edges = index.get_node_id_incoming_edges(parent_node_id)
                edge_path = None
                if parent_incoming_edges:
                    edge_id = next(iter(parent_incoming_edges))
                    edge = html_mgraph.mgraph.data().edge(edge_id)
                    edge_path = edge.edge_path

                # Create shortcut with preserved edge_path
                edit.new_edge(
                    from_node_id = grand_parent_node_id,
                    to_node_id   = node_id,
                    edge_path    = edge_path
                )
                nodes_to_delete.append(parent_node_id)

        for node_id in set(nodes_to_delete):
            edit.delete_node(node_id)

        for node in self.text_nodes(html_mgraph):
            node.node_path = ''

        return html_mgraph



    # helpers

    def nodes(self, html_mgraph):
        return html_mgraph.mgraph.graph.model.data.nodes.values()

    def text_nodes(self, html_mgraph):
        return [node for node in self.nodes(html_mgraph) if node.node_path=='text']

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