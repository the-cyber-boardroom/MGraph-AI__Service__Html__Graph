from typing                                                              import Dict, Any, List
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Base  import Html_MGraph__Base
from mgraph_db.mgraph.schemas.identifiers.Node_Path                      import Node_Path
from mgraph_db.mgraph.schemas.identifiers.Edge_Path                      import Edge_Path
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id        import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id        import Safe_Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe           import type_safe


class Html_MGraph__Head(Html_MGraph__Base):                                     # Graph for <head> element structure and text content
    """Represents the <head> section of an HTML document.
    
    Contains:
    - Element nodes (meta, title, link, script, style) with node_path like "head.meta"
    - Text value nodes for title content (node_path "text")
    - Child edges (predicate: 'child', edge_path: position)
    - Text edges (predicate: 'text', edge_path: position)
    
    Does NOT contain:
    - Tag nodes (those are in Html_MGraph__Attributes)
    - Attribute nodes (those are in Html_MGraph__Attributes)
    - Script content (those are in Html_MGraph__Scripts)
    - Style content (those are in Html_MGraph__Styles)
    
    Script and style elements exist as nodes (for DOM structure)
    but their content is stored in their respective graphs.
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # Constants
    # ═══════════════════════════════════════════════════════════════════════════

    PREDICATE_CHILD : Safe_Id = Safe_Id('child')                                # Edge predicate for child elements
    PREDICATE_TEXT  : Safe_Id = Safe_Id('text')                                 # Edge predicate for text content
    PATH_TEXT       : str     = 'text'                                          # Node path for text value nodes

    # ═══════════════════════════════════════════════════════════════════════════
    # Build Methods
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def create_element(self, node_path : Node_Path         ,                    # DOM path for element (e.g., "head.meta")
                             node_id   : Node_Id    = None                      # Optional specific node_id (for shared IDs)
                      ) -> Node_Id:                                             # Create an element node
        node = self.new_element_node(node_path = node_path ,
                                     node_id   = node_id   )
        return node.node_id

    @type_safe
    def create_text(self, text       : str            ,                         # Text content (typically for <title>)
                          parent_id  : Node_Id        ,                         # Parent element node_id
                          position   : int      = 0                             # Position among siblings
                   ) -> Node_Id:                                                # Create a text value node and link to parent
        unique_key = f"{parent_id}:{position}"                                  # Unique key based on parent and position
        text_node  = self.new_value_node(value     = text                  ,
                                         node_path = Node_Path(self.PATH_TEXT) ,
                                         key       = unique_key            )
        self.new_edge(from_node_id = parent_id                 ,
                      to_node_id   = text_node.node_id         ,
                      predicate    = self.PREDICATE_TEXT       ,
                      edge_path    = Edge_Path(str(position))  )
        return text_node.node_id

    @type_safe
    def add_child(self, parent_id : Node_Id ,                                   # Parent element node_id
                        child_id  : Node_Id ,                                   # Child element node_id
                        position  : int     = 0                                 # Position among siblings
                 ) -> None:                                                     # Link parent to child element
        self.new_edge(from_node_id = parent_id                ,
                      to_node_id   = child_id                 ,
                      predicate    = self.PREDICATE_CHILD     ,
                      edge_path    = Edge_Path(str(position)) )

    @type_safe
    def set_root(self, node_id: Node_Id) -> None:                               # Set the root node (should be <head> element)
        self.root_id = node_id

    # ═══════════════════════════════════════════════════════════════════════════
    # Query Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def get_element_children(self, node_id: Node_Id) -> List[Node_Id]:          # Get child element nodes in order
        return self.get_children_ordered(node_id, self.PREDICATE_CHILD)

    def get_text_nodes(self, node_id: Node_Id) -> List[Node_Id]:                # Get text nodes for an element in order
        return self.get_children_ordered(node_id, self.PREDICATE_TEXT)

    def get_text_content(self, node_id: Node_Id) -> str:                        # Get concatenated text content for an element
        text_node_ids = self.get_text_nodes(node_id)
        texts         = []
        for text_id in text_node_ids:
            value = self.node_value(text_id)
            if value:
                texts.append(value)
        return ''.join(texts)

    def is_text_node(self, node_id: Node_Id) -> bool:                           # Check if node is a text value node
        path = self.node_path(node_id)
        return path and str(path) == self.PATH_TEXT

    def is_element_node(self, node_id: Node_Id) -> bool:                        # Check if node is an element node
        path = self.node_path(node_id)
        return path and str(path) != self.PATH_TEXT

    # ═══════════════════════════════════════════════════════════════════════════
    # Element Iteration
    # ═══════════════════════════════════════════════════════════════════════════

    def all_element_nodes(self) -> List[Node_Id]:                               # Get all element nodes (non-text)
        elements = []
        for node_id in self.nodes_ids():
            if self.is_element_node(node_id):
                elements.append(node_id)
        return elements

    def all_text_nodes(self) -> List[Node_Id]:                                  # Get all text value nodes
        text_nodes = []
        for node_id in self.nodes_ids():
            if self.is_text_node(node_id):
                text_nodes.append(node_id)
        return text_nodes

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Methods (override base)
    # ═══════════════════════════════════════════════════════════════════════════

    def stats(self) -> Dict[str, Any]:                                          # Get statistics about the head graph
        base_stats     = super().stats()
        element_count  = len(self.all_element_nodes())
        text_count     = len(self.all_text_nodes())

        base_stats['element_nodes'] = element_count
        base_stats['text_nodes']    = text_count
        return base_stats
