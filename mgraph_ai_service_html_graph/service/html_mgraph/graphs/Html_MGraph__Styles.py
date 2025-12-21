from typing                                                                     import Dict, Any, List, Optional

from mgraph_ai_service_html_graph.schemas.html.Schema__Html_MGraph import Schema__Html_MGraph__Stats__Styles
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Base  import Html_MGraph__Base
from mgraph_db.mgraph.schemas.identifiers.Node_Path                             import Node_Path
from mgraph_db.mgraph.schemas.identifiers.Edge_Path                             import Edge_Path
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id               import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id               import Safe_Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe

class Html_MGraph__Styles(Html_MGraph__Base):                                   # Graph for CSS content from <style> and <link> elements
    """Stores CSS content from <style> elements and <link rel="stylesheet">.
    
    Structure:
        root → style_element_node → content_value_node
    
    Style element nodes:
    - Same Node_Id as in Head graph (for cross-reference)
    - Linked from root with predicate 'style'
    - Edge_path indicates order in document
    
    Content nodes:
    - Store actual CSS code as value
    - node_path = position (for multiple content blocks)
    - Linked from element with predicate 'content'
    
    External stylesheets (<link>):
    - Have no content edge (href attribute is in Html_MGraph__Attributes)
    
    Future extension:
    - Can add 'ast' predicate edges for parsed CSS AST
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # Constants
    # ═══════════════════════════════════════════════════════════════════════════

    PREDICATE_STYLE   : Safe_Id = Safe_Id('style')                              # Edge from root to style element
    PREDICATE_CONTENT : Safe_Id = Safe_Id('content')                            # Edge from element to content
    PREDICATE_AST     : Safe_Id = Safe_Id('ast')                                # Future: edge to CSS AST subgraph
    PATH_ROOT         : str     = 'styles'                                      # Node path for root

    # ═══════════════════════════════════════════════════════════════════════════
    # Internal State
    # ═══════════════════════════════════════════════════════════════════════════

    style_order : int = 0                                                       # Counter for style ordering

    def setup(self) -> 'Html_MGraph__Styles':                                   # Initialize the graph with root node
        super().setup()
        self.style_order = 0

        root_node    = self.new_element_node(node_path=Node_Path(self.PATH_ROOT))  # Create root node
        self.root_id = root_node.node_id
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # Build Methods
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def register_style(self, node_id : Node_Id ,                                # Style element node_id (same as Head graph)
                             content : str     = None                           # CSS content (None for external)
                      ) -> Optional[Node_Id]:                                   # Register a style element, returns content node_id
        anchor_node = self.new_element_node(node_path = Node_Path(f"style:{node_id}"),  # Create anchor with same ID
                                            node_id   = node_id                       )
        self.new_edge(from_node_id = self.root_id                 ,             # Link root → style element
                      to_node_id   = node_id                      ,
                      predicate    = self.PREDICATE_STYLE         ,
                      edge_path    = Edge_Path(str(self.style_order)))
        self.style_order += 1

        if content:                                                             # Add content for inline styles
            return self._add_content(node_id, content, position=0)

        return None                                                             # External stylesheet (no content)

    @type_safe
    def register_link(self, node_id: Node_Id) -> None:                          # Register an external stylesheet (<link>)
        self.register_style(node_id=node_id, content=None)                      # Same as style without content

    def _add_content(self, node_id  : Node_Id ,                                 # Add content to a style element
                           content  : str     ,
                           position : int     = 0
                    ) -> Node_Id:
        content_node = self.new_value_node(value     = content                 ,
                                           node_path = Node_Path(str(position)))
        self.new_edge(from_node_id = node_id                     ,
                      to_node_id   = content_node.node_id        ,
                      predicate    = self.PREDICATE_CONTENT      ,
                      edge_path    = Edge_Path(str(position))    )
        return content_node.node_id

    # ═══════════════════════════════════════════════════════════════════════════
    # Query Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def get_style_content(self, node_id: Node_Id) -> Optional[str]:             # Get CSS content for a style element
        edges = self.outgoing_edges(node_id)
        for edge in edges:
            if self.edge_predicate(edge) == self.PREDICATE_CONTENT:
                content_node_id = edge.edge.data.to_node_id
                return self.node_value(content_node_id)
        return None                                                             # External stylesheet or no content

    def is_inline_style(self, node_id: Node_Id) -> bool:                        # Check if style has inline content
        return self.get_style_content(node_id) is not None

    def is_external_style(self, node_id: Node_Id) -> bool:                      # Check if style is external (no content)
        return self.get_style_content(node_id) is None

    def is_style_anchor(self, node_id: Node_Id) -> bool:                       # Check if node is a style anchor
        node_path = self.node_path(node_id)
        if node_path:
            path_str = str(node_path)
            return path_str.startswith('style:')
        return False

    def get_all_styles(self) -> List[Node_Id]:                                  # Get all style element node_ids in order
        styles = []
        edges  = self.outgoing_edges(self.root_id)

        styles_with_pos = []
        for edge in edges:
            if self.edge_predicate(edge) == self.PREDICATE_STYLE:
                edge_path = self.edge_path(edge)
                position  = int(str(edge_path)) if edge_path else 0
                styles_with_pos.append((position, edge.edge.data.to_node_id))

        styles_with_pos.sort(key=lambda x: x[0])
        return [node_id for _, node_id in styles_with_pos]

    def get_inline_styles(self) -> List[Node_Id]:                               # Get only inline styles (with content)
        return [node_id for node_id in self.get_all_styles()
                if self.is_inline_style(node_id)]

    def get_external_styles(self) -> List[Node_Id]:                             # Get only external stylesheets (no content)
        return [node_id for node_id in self.get_all_styles()
                if self.is_external_style(node_id)]

    # todo: see how this can be done
    # def get_style_href(self, node_id: Node_Id) -> Optional[str]:                # Get href attribute for external stylesheet
    #     for edge in self.outgoing_edges(node_id):
    #         edge_path = self.edge_path(edge)
    #         if edge_path and str(edge_path) == 'href':
    #             target_id = edge.edge.data.to_node_id
    #             return self.node_value(target_id)
    #     return None

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Methods (override base)
    # ═══════════════════════════════════════════════════════════════════════════

    def stats(self) -> Schema__Html_MGraph__Stats__Styles:                      # Get statistics about the styles graph
        total_styles    = 0
        inline_styles   = 0
        external_styles = 0

        for node_id in self.nodes_ids():
            if self.is_style_anchor(node_id):
                total_styles += 1
                if self.get_style_content(node_id):                             # Has inline content
                    inline_styles += 1
                elif self.is_external_style(node_id):                              # Has external href
                    external_styles += 1

        return Schema__Html_MGraph__Stats__Styles(
            total_nodes     = len(list(self.mgraph.data().nodes_ids())) ,
            total_edges     = len(list(self.mgraph.data().edges_ids())) ,
            root_id         = self.root_id                              ,
            total_styles    = total_styles                              ,
            inline_styles   = inline_styles                             ,
            external_styles = external_styles                           )