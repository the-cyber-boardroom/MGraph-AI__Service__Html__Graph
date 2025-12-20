from unittest                                                            import TestCase
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Base  import Html_MGraph__Base
from mgraph_db.mgraph.schemas.identifiers.Node_Path                      import Node_Path
from mgraph_db.mgraph.schemas.identifiers.Edge_Path                      import Edge_Path
from mgraph_db.mgraph.domain.Domain__MGraph__Node                        import Domain__MGraph__Node
from mgraph_db.mgraph.domain.Domain__MGraph__Edge                        import Domain__MGraph__Edge
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id        import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id         import Obj_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id        import Safe_Id
from osbot_utils.type_safe.Type_Safe                                     import Type_Safe
from osbot_utils.utils.Objects                                           import base_classes

class test_Html_MGraph__Base(TestCase):                                         # Test base class for Html_MGraph

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                     # Test default initialization
        with Html_MGraph__Base() as _:
            assert type(_)       is Html_MGraph__Base
            assert Type_Safe     in base_classes(_)
            assert _.mgraph      is None
            assert _.root_id     is None

    def test_setup(self):                                                       # Test setup creates MGraph
        with Html_MGraph__Base().setup() as _:
            assert _.mgraph  is not None
            assert _.root_id is not None                                        # Base sets root

    # ═══════════════════════════════════════════════════════════════════════════
    # Node Creation Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_new_element_node(self):                                            # Test element node creation without node_id
        with Html_MGraph__Base().setup() as _:
            node_path = Node_Path('test.element')
            node      = _.new_element_node(node_path=node_path)

            assert type(node)   is Domain__MGraph__Node
            assert node.node_id is not None
            assert node.node.data.node_path == node_path

    def test_new_element_node__with_node_id(self):                              # Test element node creation with specific node_id
        with Html_MGraph__Base().setup() as _:
            node_path  = Node_Path('test.element')
            custom_id  = Node_Id(Obj_Id())
            node       = _.new_element_node(node_path=node_path, node_id=custom_id)

            assert node.node_id == custom_id
            assert node.node.data.node_path == node_path

    def test_new_value_node(self):                                              # Test value node creation with minimal params
        with Html_MGraph__Base().setup() as _:
            node = _.new_value_node(value='test_value')

            assert type(node)   is Domain__MGraph__Node
            assert node.node_id is not None

    def test_new_value_node__with_path_and_key(self):                           # Test value node with path and key
        with Html_MGraph__Base().setup() as _:
            node_path = Node_Path('value.path')
            node      = _.new_value_node(value     = 'my_value'  ,
                                         node_path = node_path   ,
                                         key       = 'unique_key')

            assert node.node_id is not None
            assert node.node.data.node_path == node_path

    # ═══════════════════════════════════════════════════════════════════════════
    # Edge Creation Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_new_edge(self):                                                    # Test edge creation without predicate
        with Html_MGraph__Base().setup() as _:
            node1 = _.new_element_node(node_path=Node_Path('node1'))
            node2 = _.new_element_node(node_path=Node_Path('node2'))

            edge = _.new_edge(from_node_id=node1.node_id, to_node_id=node2.node_id)

            assert type(edge)                  is Domain__MGraph__Edge
            assert edge.edge.data.from_node_id == node1.node_id
            assert edge.edge.data.to_node_id   == node2.node_id

    def test_new_edge__with_predicate(self):                                    # Test edge creation with predicate
        with Html_MGraph__Base().setup() as _:
            node1     = _.new_element_node(node_path=Node_Path('node1'))
            node2     = _.new_element_node(node_path=Node_Path('node2'))
            predicate = Safe_Id('child')

            edge = _.new_edge(from_node_id = node1.node_id ,
                              to_node_id   = node2.node_id ,
                              predicate    = predicate     )

            assert edge.edge.data.edge_label is not None
            assert edge.edge.data.edge_label.predicate == predicate

    def test_new_edge__with_edge_path(self):                                    # Test edge creation with edge_path
        with Html_MGraph__Base().setup() as _:
            node1     = _.new_element_node(node_path=Node_Path('node1'))
            node2     = _.new_element_node(node_path=Node_Path('node2'))
            edge_path = Edge_Path('0')

            edge = _.new_edge(from_node_id = node1.node_id ,
                              to_node_id   = node2.node_id ,
                              edge_path    = edge_path     )

            assert edge.edge.data.edge_path == edge_path

    def test_new_edge__with_predicate_and_path(self):                           # Test edge with both predicate and path
        with Html_MGraph__Base().setup() as _:
            node1     = _.new_element_node(node_path=Node_Path('parent'))
            node2     = _.new_element_node(node_path=Node_Path('child'))
            predicate = Safe_Id('contains')
            edge_path = Edge_Path('position:0')

            edge = _.new_edge(from_node_id = node1.node_id ,
                              to_node_id   = node2.node_id ,
                              predicate    = predicate     ,
                              edge_path    = edge_path     )

            assert edge.edge.data.edge_label.predicate == predicate
            assert edge.edge.data.edge_path            == edge_path

    # ═══════════════════════════════════════════════════════════════════════════
    # Node Query Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_node(self):                                                        # Test getting node by ID
        with Html_MGraph__Base().setup() as _:
            created_node = _.new_element_node(node_path=Node_Path('test'))
            fetched_node = _.node(created_node.node_id)

            assert fetched_node is not None
            assert fetched_node.node_id == created_node.node_id

    def test_node__not_found(self):                                             # Test getting non-existent node
        with Html_MGraph__Base().setup() as _:
            fake_id = Node_Id(Obj_Id())
            result  = _.node(fake_id)

            assert result is None

    def test_node_value(self):                                                  # Test getting value from value node
        with Html_MGraph__Base().setup() as _:
            value_node = _.new_value_node(value='hello_world')
            result     = _.node_value(value_node.node_id)

            assert result == 'hello_world'

    def test_node_value__element_node(self):                                    # Test getting value from non-value node returns None
        with Html_MGraph__Base().setup() as _:
            element_node = _.new_element_node(node_path=Node_Path('element'))
            result       = _.node_value(element_node.node_id)

            assert result is None                                               # Element nodes don't have values

    def test_node_value__not_found(self):                                       # Test getting value from non-existent node
        with Html_MGraph__Base().setup() as _:
            fake_id = Node_Id(Obj_Id())
            result  = _.node_value(fake_id)

            assert result is None

    def test_node_path(self):                                                   # Test getting path from node
        with Html_MGraph__Base().setup() as _:
            node_path = Node_Path('my.test.path')
            node      = _.new_element_node(node_path=node_path)
            result    = _.node_path(node.node_id)

            assert result == node_path

    def test_node_path__not_found(self):                                        # Test getting path from non-existent node
        with Html_MGraph__Base().setup() as _:
            fake_id = Node_Id(Obj_Id())
            result  = _.node_path(fake_id)

            assert result is None

    def test_nodes_ids(self):                                                   # Test getting all node IDs
        with Html_MGraph__Base().setup() as _:
            node1 = _.new_element_node(node_path=Node_Path('node1'))
            node2 = _.new_element_node(node_path=Node_Path('node2'))
            node3 = _.new_value_node(value='value')

            all_ids = _.nodes_ids()

            assert len(all_ids) == 4
            assert node1.node_id in all_ids
            assert node2.node_id in all_ids
            assert node3.node_id in all_ids

    def test_nodes_ids__empty(self):                                            # Test getting IDs from empty graph
        with Html_MGraph__Base().setup() as _:
            all_ids = _.nodes_ids()

            assert len(all_ids) == 1

    def test_nodes_by_path(self):                                               # Test getting nodes by path
        with Html_MGraph__Base().setup() as _:
            path  = Node_Path('shared.path')
            node1 = _.new_element_node(node_path=path)
            node2 = _.new_element_node(node_path=path)
            node3 = _.new_element_node(node_path=Node_Path('different.path'))

            result = _.nodes_by_path(path)

            assert len(result) == 2
            assert node1.node_id in result
            assert node2.node_id in result
            assert node3.node_id not in result

    def test_nodes_by_path__empty(self):                                        # Test getting nodes by non-existent path
        with Html_MGraph__Base().setup() as _:
            _.new_element_node(node_path=Node_Path('existing.path'))
            result = _.nodes_by_path(Node_Path('non.existent.path'))

            assert result == []

    # ═══════════════════════════════════════════════════════════════════════════
    # Edge Query Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_outgoing_edges(self):                                              # Test getting outgoing edges
        with Html_MGraph__Base().setup() as _:
            parent = _.new_element_node(node_path=Node_Path('parent'))
            child1 = _.new_element_node(node_path=Node_Path('child1'))
            child2 = _.new_element_node(node_path=Node_Path('child2'))

            edge1 = _.new_edge(from_node_id=parent.node_id, to_node_id=child1.node_id)
            edge2 = _.new_edge(from_node_id=parent.node_id, to_node_id=child2.node_id)

            outgoing = _.outgoing_edges(parent.node_id)

            assert len(outgoing) == 2

    def test_outgoing_edges__empty(self):                                       # Test getting outgoing edges from leaf node
        with Html_MGraph__Base().setup() as _:
            leaf     = _.new_element_node(node_path=Node_Path('leaf'))
            outgoing = _.outgoing_edges(leaf.node_id)

            assert outgoing == []

    def test_outgoing_edges__non_existent(self):                                # Test getting outgoing edges from non-existent node
        with Html_MGraph__Base().setup() as _:
            fake_id  = Node_Id(Obj_Id())
            outgoing = _.outgoing_edges(fake_id)

            assert outgoing == []

    def test_incoming_edges(self):                                              # Test getting incoming edges
        with Html_MGraph__Base().setup() as _:
            child   = _.new_element_node(node_path=Node_Path('child'))
            parent1 = _.new_element_node(node_path=Node_Path('parent1'))
            parent2 = _.new_element_node(node_path=Node_Path('parent2'))

            _.new_edge(from_node_id=parent1.node_id, to_node_id=child.node_id)
            _.new_edge(from_node_id=parent2.node_id, to_node_id=child.node_id)

            incoming = _.incoming_edges(child.node_id)

            assert len(incoming) == 2

    def test_incoming_edges__empty(self):                                       # Test getting incoming edges to root node
        with Html_MGraph__Base().setup() as _:
            root     = _.new_element_node(node_path=Node_Path('root'))
            incoming = _.incoming_edges(root.node_id)

            assert incoming == []

    def test_edge_predicate(self):                                              # Test getting predicate from edge
        with Html_MGraph__Base().setup() as _:
            node1     = _.new_element_node(node_path=Node_Path('node1'))
            node2     = _.new_element_node(node_path=Node_Path('node2'))
            predicate = Safe_Id('relationship')

            edge      = _.new_edge(from_node_id = node1.node_id ,
                                   to_node_id   = node2.node_id ,
                                   predicate    = predicate     )
            outgoing  = _.outgoing_edges(node1.node_id)
            result    = _.edge_predicate(outgoing[0])

            assert result == predicate

    def test_edge_predicate__no_predicate(self):                                # Test getting predicate from edge without one
        with Html_MGraph__Base().setup() as _:
            node1 = _.new_element_node(node_path=Node_Path('node1'))
            node2 = _.new_element_node(node_path=Node_Path('node2'))

            _.new_edge(from_node_id=node1.node_id, to_node_id=node2.node_id)

            outgoing = _.outgoing_edges(node1.node_id)
            result   = _.edge_predicate(outgoing[0])

            assert result is None

    def test_edge_path_method(self):                                            # Test getting edge_path from edge
        with Html_MGraph__Base().setup() as _:
            node1     = _.new_element_node(node_path=Node_Path('node1'))
            node2     = _.new_element_node(node_path=Node_Path('node2'))
            edge_path = Edge_Path('position:5')

            _.new_edge(from_node_id = node1.node_id ,
                       to_node_id   = node2.node_id ,
                       edge_path    = edge_path     )

            outgoing = _.outgoing_edges(node1.node_id)
            result   = _.edge_path(outgoing[0])

            assert result == edge_path

    def test_edge_path_method__no_path(self):                                   # Test getting edge_path when not set
        with Html_MGraph__Base().setup() as _:
            node1 = _.new_element_node(node_path=Node_Path('node1'))
            node2 = _.new_element_node(node_path=Node_Path('node2'))

            _.new_edge(from_node_id=node1.node_id, to_node_id=node2.node_id)

            outgoing = _.outgoing_edges(node1.node_id)
            result   = _.edge_path(outgoing[0])

            assert result is None or result == Node_Path('')                    # Depends on MGraph default behavior

    # ═══════════════════════════════════════════════════════════════════════════
    # Traversal Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_parent(self):                                                  # Test getting parent node
        with Html_MGraph__Base().setup() as _:
            parent = _.new_element_node(node_path=Node_Path('parent'))
            child  = _.new_element_node(node_path=Node_Path('child'))

            _.new_edge(from_node_id=parent.node_id, to_node_id=child.node_id)

            result = _.get_parent(child.node_id)

            assert result == parent.node_id

    def test_get_parent__no_parent(self):                                       # Test getting parent of root node
        with Html_MGraph__Base().setup() as _:
            root   = _.new_element_node(node_path=Node_Path('root'))
            result = _.get_parent(root.node_id)

            assert result is None

    def test_get_children(self):                                                # Test getting children without predicate filter
        with Html_MGraph__Base().setup() as _:
            parent = _.new_element_node(node_path=Node_Path('parent'))
            child1 = _.new_element_node(node_path=Node_Path('child1'))
            child2 = _.new_element_node(node_path=Node_Path('child2'))

            _.new_edge(from_node_id=parent.node_id, to_node_id=child1.node_id)
            _.new_edge(from_node_id=parent.node_id, to_node_id=child2.node_id)

            children = _.get_children(parent.node_id)

            assert len(children)       == 2
            assert child1.node_id      in children
            assert child2.node_id      in children

    def test_get_children__with_predicate_filter(self):                         # Test getting children with predicate filter
        with Html_MGraph__Base().setup() as _:
            parent  = _.new_element_node(node_path=Node_Path('parent'))
            element = _.new_element_node(node_path=Node_Path('element'))
            text    = _.new_value_node(value='text content')

            child_pred = Safe_Id('child')
            text_pred  = Safe_Id('text')

            _.new_edge(from_node_id=parent.node_id, to_node_id=element.node_id, predicate=child_pred)
            _.new_edge(from_node_id=parent.node_id, to_node_id=text.node_id   , predicate=text_pred )

            element_children = _.get_children(parent.node_id, predicate=child_pred)
            text_children    = _.get_children(parent.node_id, predicate=text_pred)

            assert element_children == [element.node_id]
            assert text_children    == [text.node_id]

    def test_get_children__empty(self):                                         # Test getting children from leaf node
        with Html_MGraph__Base().setup() as _:
            leaf     = _.new_element_node(node_path=Node_Path('leaf'))
            children = _.get_children(leaf.node_id)

            assert children == []

    def test_get_children_ordered(self):                                        # Test getting children in edge_path order
        with Html_MGraph__Base().setup() as _:
            parent = _.new_element_node(node_path=Node_Path('parent'))
            child0 = _.new_element_node(node_path=Node_Path('child0'))
            child1 = _.new_element_node(node_path=Node_Path('child1'))
            child2 = _.new_element_node(node_path=Node_Path('child2'))

            _.new_edge(from_node_id=parent.node_id, to_node_id=child2.node_id, edge_path=Edge_Path('2'))  # Add out of order
            _.new_edge(from_node_id=parent.node_id, to_node_id=child0.node_id, edge_path=Edge_Path('0'))
            _.new_edge(from_node_id=parent.node_id, to_node_id=child1.node_id, edge_path=Edge_Path('1'))

            ordered = _.get_children_ordered(parent.node_id)

            assert ordered == [child0.node_id, child1.node_id, child2.node_id]  # Sorted by position

    def test_get_children_ordered__with_predicate(self):                        # Test ordered children with predicate filter
        with Html_MGraph__Base().setup() as _:
            parent = _.new_element_node(node_path=Node_Path('parent'))
            elem1  = _.new_element_node(node_path=Node_Path('elem1'))
            elem2  = _.new_element_node(node_path=Node_Path('elem2'))
            text1  = _.new_value_node(value='text1')

            child_pred = Safe_Id('child')
            text_pred  = Safe_Id('text')

            _.new_edge(from_node_id=parent.node_id, to_node_id=elem2.node_id, predicate=child_pred, edge_path=Edge_Path('1'))
            _.new_edge(from_node_id=parent.node_id, to_node_id=elem1.node_id, predicate=child_pred, edge_path=Edge_Path('0'))
            _.new_edge(from_node_id=parent.node_id, to_node_id=text1.node_id, predicate=text_pred , edge_path=Edge_Path('0'))

            ordered_elements = _.get_children_ordered(parent.node_id, predicate=child_pred)
            ordered_text     = _.get_children_ordered(parent.node_id, predicate=text_pred)

            assert ordered_elements == [elem1.node_id, elem2.node_id]
            assert ordered_text     == [text1.node_id]

    def test_get_children_ordered__no_edge_path(self):                          # Test ordered children when edge_path not set
        with Html_MGraph__Base().setup() as _:
            parent = _.new_element_node(node_path=Node_Path('parent'))
            child  = _.new_element_node(node_path=Node_Path('child'))

            _.new_edge(from_node_id=parent.node_id, to_node_id=child.node_id)   # No edge_path

            ordered = _.get_children_ordered(parent.node_id)

            assert child.node_id in ordered                                     # Should still work with default position 0

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_stats(self):                                                       # Test statistics with populated graph
        with Html_MGraph__Base().setup() as _:
            node1 = _.new_element_node(node_path=Node_Path('node1'))
            node2 = _.new_element_node(node_path=Node_Path('node2'))
            _.new_edge(from_node_id=node1.node_id, to_node_id=node2.node_id)

            _.root_id = node1.node_id
            stats     = _.stats()

            assert stats['total_nodes'] == 3
            assert stats['total_edges'] == 1
            assert stats['root_id']     == str(node1.node_id)

    def test_stats__empty_graph(self):                                          # Test statistics with empty graph (and root_id)
        with Html_MGraph__Base().setup() as _:
            stats = _.stats()

            assert stats['total_nodes'] == 1
            assert stats['total_edges'] == 0
            assert stats['root_id'    ] is not None

    def test_stats__with_root_id(self):                                           # Test statistics without root_id set
        with Html_MGraph__Base().setup() as _:
            _.new_element_node(node_path=Node_Path('node'))
            stats = _.stats()

            assert stats['total_nodes'] == 2
            assert stats['root_id']     is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # Serialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_to_json(self):                                                     # Test JSON export
        with Html_MGraph__Base().setup() as _:
            node1 = _.new_element_node(node_path=Node_Path('node1'))
            node2 = _.new_element_node(node_path=Node_Path('node2'))
            _.new_edge(from_node_id=node1.node_id, to_node_id=node2.node_id)

            json_data = _.to_json()

            assert type(json_data) is dict
            assert 'nodes' in json_data or 'graph' in json_data                 # Depends on MGraph export format

    def test_to_json__empty_graph(self):                                        # Test JSON export of empty graph
        with Html_MGraph__Base().setup() as _:
            json_data = _.to_json()

            assert type(json_data) is dict