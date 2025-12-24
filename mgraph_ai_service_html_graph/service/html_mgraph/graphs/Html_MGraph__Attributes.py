from typing                                                                     import Dict, Any, List, Optional
from mgraph_ai_service_html_graph.schemas.html.Schema__Html_MGraph              import Schema__Html_MGraph__Stats__Attributes
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Base  import Html_MGraph__Base
from mgraph_db.mgraph.schemas.identifiers.Node_Path                             import Node_Path
from osbot_utils.helpers.timestamp_capture.context_managers.timestamp_block     import timestamp_block
from osbot_utils.helpers.timestamp_capture.decorators.timestamp_args            import timestamp_args
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id               import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id               import Safe_Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe


class Html_MGraph__Attributes(Html_MGraph__Base):                               # Graph for tags and attributes of all elements
    """Stores tags and attributes for ALL elements in the document.
    
    Hierarchical structure:
        root → tag_node → element_node → attr_value_node
    
    This structure:
    - Groups elements by tag type (all <div>s under one tag node)
    - Enables "get tag for element" via single parent traversal
    - Enables "get all elements by tag" via children of tag node
    - Stores attribute values with ordering preserved
    
    Node types:
    - Root node: node_path = "attributes"
    - Tag nodes: node_path = "tag:{name}", value = tag name
    - Element nodes: Same Node_Id as in Body/Head graphs (anchor nodes)
    - Attr value nodes: node_path = position (for ordering), value = attr value
    
    Edge structure:
    - root → tag: predicate = 'tag'
    - tag → element: predicate = 'element'
    - element → attr: predicate = 'attr', edge_path = attr_name
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # Constants
    # ═══════════════════════════════════════════════════════════════════════════

    PATH_ROOT         : str     = 'attributes'                                  # Node path for root
    PREDICATE_TAG     : Safe_Id = Safe_Id('tag')                                # Edge from root to tag node
    PREDICATE_ELEMENT : Safe_Id = Safe_Id('element')                            # Edge from tag to element node
    PREDICATE_ATTR    : Safe_Id = Safe_Id('attr')                               # Edge from element to attr value
    PREDICATE_NAME    : Safe_Id = 'name'                                        # instance → name node
    PREDICATE_VALUE   : Safe_Id = 'value'                                       # instance → value node
    NODE_PATH_NAME    : Safe_Id = 'name'                                        # node_path marker for name nodes
    NODE_PATH_VALUE   : Safe_Id = 'value'                                       # node_path marker for value nodes


    # ═══════════════════════════════════════════════════════════════════════════
    # Internal State
    # ═══════════════════════════════════════════════════════════════════════════

    tag_node_cache   : Dict                                                 # Cache: tag_name → tag_node_id
    value_node_cache : Dict                                                 # Cache: attr_value → node_id
    name_node_cache  : Dict

    def setup(self) -> 'Html_MGraph__Attributes':                               # Initialize the graph with root node
        super().setup()

        root_node    = self.new_element_node(node_path=Node_Path(self.PATH_ROOT)) # Create root node
        self.root_id = root_node.node_id
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # Build Methods
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def register_element(self, node_id : Node_Id ,                              # Element node_id (same as in Body/Head)
                               tag     : str                                    # HTML tag name
                        ) -> None:                                              # Register an element with its tag
        tag_node_id = self._get_or_create_tag_node(tag)                         # Get or create tag node

        anchor_node = self.new_element_node(node_path = Node_Path(f"element:{node_id}"),  # Create anchor node with same ID
                                            node_id   = node_id                        )
        self.new_edge(from_node_id = tag_node_id           ,                    # Link tag → element
                      to_node_id   = node_id               ,
                      predicate    = self.PREDICATE_ELEMENT)

    @type_safe
    def add_attribute(self,                                               # Add an attribute to an element using three-node model.
                      node_id    : Node_Id       ,                        # Element node_id
                      attr_name  : str           ,                        # Attribute name (e.g., "class")
                      attr_value : str     = None,                        # Attribute value (e.g., "container")
                      position   : int     = 0                            # Position for ordering (round-trip)
               ) -> Node_Id:                                              # Return Node_Id created


        with timestamp_block(name='html_mgraph.attributes.add_attribute | new_element_node'):

            instance_node = self.new_element_node(node_path = Node_Path(str(position)))         # 1. Create instance node (always new, stores position)

        with timestamp_block(name='html_mgraph.attributes.add_attribute | new_edge'):
            self.new_edge(from_node_id = node_id              ,                                 # 2. Link element → instance
                          to_node_id   = instance_node.node_id,
                          predicate    = self.PREDICATE_ATTR  )

        with timestamp_block(name='html_mgraph.attributes.add_attribute | _get_or_create_name_node'):
            name_node = self._get_or_create_name_node(attr_name)                                # 3. Get or create name node (reused)

        with timestamp_block(name='html_mgraph.attributes.add_attribute | new_edge'):
            self.new_edge(from_node_id = instance_node.node_id,                                 # 4. Link instance → name
                          to_node_id   = name_node.node_id    ,
                          predicate    = self.PREDICATE_NAME  )

        if attr_value is not None:                                                          # 5. Only create value node if value is not None
            with timestamp_block(name='html_mgraph.attributes.add_attribute | _get_or_create_value_node'):
                value_node = self._get_or_create_value_node(attr_value)
                self.new_edge(from_node_id = instance_node.node_id,
                              to_node_id   = value_node.node_id   ,
                              predicate    = self.PREDICATE_VALUE )

        return instance_node.node_id


    def _get_or_create_name_node(self, attr_name: str):                     # Get existing name node or create new one (for reuse). O(1) lookup."""
        if attr_name in self.name_node_cache:
            return self.node(self.name_node_cache[attr_name])

        node = self.new_value_node(
            value     = attr_name,
            node_path = Node_Path(self.NODE_PATH_NAME)
        )
        self.name_node_cache[attr_name] = node.node_id
        return node
        # """Get existing name node or create new one (for reuse)."""
        # for node_id in self.nodes_ids():
        #     node_path = self.node_path(node_id)
        #     if node_path and str(node_path) == self.NODE_PATH_NAME:
        #         if self.node_value(node_id) == attr_name:
        #             return self.node(node_id)
        #
        # return self.new_value_node(
        #     value     = attr_name,
        #     node_path = Node_Path(self.NODE_PATH_NAME)
        # )


    @timestamp_args(name='html_mgraph.attributes._get_or_create_value_node| {attr_value}')
    def _get_or_create_value_node(self, attr_value: str):
        # O(1) lookup instead of O(n) scan
        if attr_value in self.value_node_cache:
            return self.node(self.value_node_cache[attr_value])

        # Create new value node
        node = self.new_value_node(value=attr_value, node_path=Node_Path(self.NODE_PATH_VALUE))
        self.value_node_cache[attr_value] = node.node_id
        return node

    #     """Get existing value node or create new one (for reuse)."""
    #     for node_id in self.nodes_ids():
    #         node_path = self.node_path(node_id)
    #         if node_path and str(node_path) == self.NODE_PATH_VALUE:
    #             if self.node_value(node_id) == attr_value:
    #                 return self.node(node_id)
    #
    #     return self.new_value_node(
    #         value     = attr_value,
    #         node_path = Node_Path(self.NODE_PATH_VALUE)
    #     )

    def _get_or_create_tag_node(self, tag: str) -> Node_Id:                     # Get or create a tag node

        if tag in self.tag_node_cache:
            return self.tag_node_cache[tag]

        tag_path    = f"tag:{tag}"                                              # Create tag node
        tag_node    = self.new_value_node(value     = tag                  ,
                                          node_path = Node_Path(tag_path)  )
        tag_node_id = tag_node.node_id

        self.new_edge(from_node_id = self.root_id       ,                       # Link root → tag
                      to_node_id   = tag_node_id        ,
                      predicate    = self.PREDICATE_TAG )

        self.tag_node_cache[tag] = tag_node_id
        return tag_node_id

    # ═══════════════════════════════════════════════════════════════════════════
    # Query Methods - Tag Lookups
    # ═══════════════════════════════════════════════════════════════════════════

    def get_tag(self, node_id: Node_Id) -> Optional[str]:                       # Get HTML tag for an element node
        edges = self.incoming_edges(node_id)                                    # Find incoming edge from tag node
        for edge in edges:
            if self.edge_predicate(edge) == self.PREDICATE_ELEMENT:
                tag_node_id = edge.edge.data.from_node_id
                return self.node_value(tag_node_id)
        return None

    def get_elements_by_tag(self, tag: str) -> List[Node_Id]:                   # Get all elements with a specific tag
        if self.tag_node_cache and tag in self.tag_node_cache:
            tag_node_id = self.tag_node_cache[tag]
        else:
            tag_path    = f"tag:{tag}"                                          # Find tag node by path
            tag_nodes   = self.nodes_by_path(Node_Path(tag_path))
            if not tag_nodes:
                return []
            tag_node_id = tag_nodes[0]

        return self.get_children(tag_node_id, self.PREDICATE_ELEMENT)

    def get_all_tags(self) -> List[str]:                                        # Get all unique tags in the document
        tags = []
        for edge in self.outgoing_edges(self.root_id):
            if self.edge_predicate(edge) == self.PREDICATE_TAG:
                tag_node_id = edge.edge.data.to_node_id
                tag_value   = self.node_value(tag_node_id)
                if tag_value:
                    tags.append(tag_value)
        return tags

    # ═══════════════════════════════════════════════════════════════════════════
    # Query Methods - Attribute Lookups
    # ═══════════════════════════════════════════════════════════════════════════

    def get_attributes(self, node_id: Node_Id) -> Dict[str, Optional[str]]:         # Get all attributes for an element (ordered). Returns None for boolean attrs.
        attrs = []

        for edge in self.outgoing_edges(node_id):
            if self.edge_predicate(edge) == self.PREDICATE_ATTR:
                instance_id = edge.edge.data.to_node_id

                # Get position from instance node's path
                position_path = self.node_path(instance_id)
                position = int(str(position_path)) if position_path else 0

                # Find name and value from instance's outgoing edges
                attr_name = None
                attr_value = None  # Will stay None for boolean attrs

                for inner_edge in self.outgoing_edges(instance_id):
                    inner_pred = self.edge_predicate(inner_edge)
                    inner_target = inner_edge.edge.data.to_node_id

                    if inner_pred == self.PREDICATE_NAME:
                        attr_name = self.node_value(inner_target)
                    elif inner_pred == self.PREDICATE_VALUE:
                        attr_value = self.node_value(inner_target)

                if attr_name:
                    attrs.append((position, attr_name, attr_value))

        attrs.sort(key=lambda x: x[0])
        return {name: value for _, name, value in attrs}

    def get_attribute(self, node_id  : Node_Id ,                                # Get specific attribute value
                        attr_name: str
                 ) -> Optional[str]:
        return self.get_attributes(node_id).get(attr_name)

    def get_elements_with_attribute(self, attr_name: str, attr_value: Optional[str] = None) -> List[Node_Id]:   # Find all elements that have a specific attribute (optionally with specific value).
        result = []

        # Get all element nodes (those that have been registered via register_element)
        for node_id in self.nodes_ids():
            # Check if this node has attributes
            attrs = self.get_attributes(node_id)

            if attr_name in attrs:
                if attr_value is None:
                    # Just checking for presence of attribute
                    result.append(node_id)
                elif attrs[attr_name] == attr_value:
                    # Checking for specific value
                    result.append(node_id)

        return result

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _is_element_anchor(self, node_id: Node_Id) -> bool:                     # Check if node is an element anchor node
        path = self.node_path(node_id)
        if not path:
            return False
        path_str = str(path)
        return path_str.startswith('element:')

    def _is_tag_node(self, node_id: Node_Id) -> bool:                           # Check if node is a tag node
        path = self.node_path(node_id)
        if not path:
            return False
        path_str = str(path)
        return path_str.startswith('tag:')

    def _is_attr_value_node(self, node_id: Node_Id) -> bool:                    # Check if node is an attr value node
        path = self.node_path(node_id)
        if not path:
            return False
        path_str = str(path)
        return path_str.isdigit()                                               # Position is numeric

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Methods (override base)
    # ═══════════════════════════════════════════════════════════════════════════

    def stats(self) -> Schema__Html_MGraph__Stats__Attributes:                  # Get statistics about the attributes graph
        tag_count      = 0
        element_count  = 0
        attr_count     = 0
        unique_tags    = set()

        for node_id in self.nodes_ids():
            if self._is_tag_node(node_id):
                tag_count += 1
                tag_value = self.node_value(node_id)
                if tag_value:
                    unique_tags.add(tag_value)
            elif self._is_element_anchor(node_id):
                element_count += 1
            elif self._is_attr_value_node(node_id):
                attr_count += 1

        return Schema__Html_MGraph__Stats__Attributes(
            total_nodes         = len(list(self.mgraph.data().nodes_ids())) ,
            total_edges         = len(list(self.mgraph.data().edges_ids())) ,
            root_id             = self.root_id                              ,
            registered_elements = element_count                             ,
            total_attributes    = attr_count                                ,
            unique_tags         = len(unique_tags)                          )
