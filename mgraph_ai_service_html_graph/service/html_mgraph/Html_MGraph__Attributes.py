from typing                                                              import Dict, Any, List, Optional
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Base  import Html_MGraph__Base
from mgraph_db.mgraph.schemas.identifiers.Node_Path                      import Node_Path
from mgraph_db.mgraph.schemas.identifiers.Edge_Path                      import Edge_Path
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id        import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id        import Safe_Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe           import type_safe


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

    PREDICATE_TAG     : Safe_Id = Safe_Id('tag')                                # Edge from root to tag node
    PREDICATE_ELEMENT : Safe_Id = Safe_Id('element')                            # Edge from tag to element node
    PREDICATE_ATTR    : Safe_Id = Safe_Id('attr')                               # Edge from element to attr value
    PATH_ROOT         : str     = 'attributes'                                  # Node path for root

    # ═══════════════════════════════════════════════════════════════════════════
    # Internal State
    # ═══════════════════════════════════════════════════════════════════════════

    tag_node_cache : Dict[str, Node_Id] = None                                  # Cache: tag_name → tag_node_id

    def setup(self) -> 'Html_MGraph__Attributes':                               # Initialize the graph with root node
        super().setup()
        self.tag_node_cache = {}

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
    def add_attribute(self, node_id    : Node_Id ,                              # Element node_id
                            attr_name  : str     ,                              # Attribute name (e.g., "class")
                            attr_value : str     ,                              # Attribute value (e.g., "container")
                            position   : int     = 0                            # Position for ordering (round-trip)
                     ) -> Node_Id:                                              # Add an attribute to an element
        attr_node = self.new_value_node(value     = attr_value         ,        # Create attr value node
                                        node_path = Node_Path(str(position)))   # Position in node_path for ordering
        self.new_edge(from_node_id = node_id               ,                    # Link element → attr value
                      to_node_id   = attr_node.node_id     ,
                      predicate    = self.PREDICATE_ATTR   ,
                      edge_path    = Edge_Path(attr_name)  )                    # Attr name in edge_path
        return attr_node.node_id

    def _get_or_create_tag_node(self, tag: str) -> Node_Id:                     # Get or create a tag node
        if self.tag_node_cache is None:
            self.tag_node_cache = {}

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

    def get_attributes(self, node_id: Node_Id) -> Dict[str, str]:               # Get all attributes for an element (ordered)
        attrs            = []
        edges            = self.outgoing_edges(node_id)

        for edge in edges:
            if self.edge_predicate(edge) == self.PREDICATE_ATTR:
                attr_name     = str(self.edge_path(edge))                       # Attr name from edge_path
                attr_node_id  = edge.edge.data.to_node_id
                attr_value    = self.node_value(attr_node_id)
                position_path = self.node_path(attr_node_id)                    # Position from node_path
                position      = int(str(position_path)) if position_path else 0

                attrs.append((position, attr_name, attr_value or ''))

        attrs.sort(key=lambda x: x[0])                                          # Sort by position for round-trip
        return {name: value for _, name, value in attrs}

    def get_attribute(self, node_id  : Node_Id ,                                # Get specific attribute value
                            attr_name: str
                     ) -> Optional[str]:
        edges = self.outgoing_edges(node_id)
        for edge in edges:
            if self.edge_predicate(edge) == self.PREDICATE_ATTR:
                if str(self.edge_path(edge)) == attr_name:
                    attr_node_id = edge.edge.data.to_node_id
                    return self.node_value(attr_node_id)
        return None

    def get_elements_with_attribute(self, attr_name  : str             ,        # Find elements with specific attribute
                                          attr_value : str      = None          # Optionally filter by value
                                   ) -> List[Node_Id]:
        elements = []
        for node_id in self.nodes_ids():
            if self._is_element_anchor(node_id):
                for edge in self.outgoing_edges(node_id):
                    if self.edge_predicate(edge) == self.PREDICATE_ATTR:
                        if str(self.edge_path(edge)) == attr_name:
                            if attr_value is None:
                                elements.append(node_id)
                            else:
                                value = self.node_value(edge.edge.data.to_node_id)
                                if value == attr_value:
                                    elements.append(node_id)
                            break                                               # Found attribute, check next element
        return elements

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

    def stats(self) -> Dict[str, Any]:                                          # Get statistics about the attributes graph
        base_stats     = super().stats()
        tag_count      = 0
        element_count  = 0
        attr_count     = 0

        for node_id in self.nodes_ids():
            if self._is_tag_node(node_id):
                tag_count += 1
            elif self._is_element_anchor(node_id):
                element_count += 1
            elif self._is_attr_value_node(node_id):
                attr_count += 1

        base_stats['tag_nodes']     = tag_count
        base_stats['element_nodes'] = element_count
        base_stats['attr_nodes']    = attr_count
        return base_stats
