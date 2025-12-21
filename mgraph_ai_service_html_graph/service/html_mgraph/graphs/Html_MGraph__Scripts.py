from typing                                                                     import Dict, Any, List, Optional

from mgraph_ai_service_html_graph.schemas.html.Schema__Html_MGraph import Schema__Html_MGraph__Stats__Scripts
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Base  import Html_MGraph__Base
from mgraph_db.mgraph.schemas.identifiers.Node_Path                             import Node_Path
from mgraph_db.mgraph.schemas.identifiers.Edge_Path                             import Edge_Path
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id               import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id               import Safe_Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe


class Html_MGraph__Scripts(Html_MGraph__Base):                                  # Graph for JavaScript content from <script> elements
    """Stores JavaScript content from <script> elements.
    
    Structure:
        root → script_element_node → content_value_node
    
    Script element nodes:
    - Same Node_Id as in Body/Head graphs (for cross-reference)
    - Linked from root with predicate 'script'
    - Edge_path indicates order in document
    
    Content nodes:
    - Store actual JavaScript code as value
    - node_path = position (for multiple content blocks)
    - Linked from element with predicate 'content'
    
    External scripts:
    - Have no content edge (src attribute is in Html_MGraph__Attributes)
    
    Future extension:
    - Can add 'ast' predicate edges for parsed JavaScript AST
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # Constants
    # ═══════════════════════════════════════════════════════════════════════════

    PREDICATE_SCRIPT  : Safe_Id = Safe_Id('script')                             # Edge from root to script element
    PREDICATE_CONTENT : Safe_Id = Safe_Id('content')                            # Edge from element to content
    PREDICATE_AST     : Safe_Id = Safe_Id('ast')                                # Future: edge to AST subgraph
    PATH_ROOT         : str     = 'scripts'                                     # Node path for root

    # ═══════════════════════════════════════════════════════════════════════════
    # Internal State
    # ═══════════════════════════════════════════════════════════════════════════

    script_order : int = 0                                                      # Counter for script ordering

    def setup(self) -> 'Html_MGraph__Scripts':                                  # Initialize the graph with root node
        super().setup()
        self.script_order = 0

        root_node    = self.new_element_node(node_path=Node_Path(self.PATH_ROOT))  # Create root node
        self.root_id = root_node.node_id
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # Build Methods
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def register_script(self, node_id : Node_Id ,                               # Script element node_id (same as Body/Head)
                              content : str     = None                          # JavaScript content (None for external)
                       ) -> Optional[Node_Id]:                                  # Register a script element, returns content node_id
        anchor_node = self.new_element_node(node_path = Node_Path(f"script:{node_id}"),  # Create anchor with same ID
                                            node_id   = node_id                        )
        self.new_edge(from_node_id = self.root_id                  ,            # Link root → script element
                      to_node_id   = node_id                       ,
                      predicate    = self.PREDICATE_SCRIPT         ,
                      edge_path    = Edge_Path(str(self.script_order)))
        self.script_order += 1

        if content:                                                             # Add content for inline scripts
            return self._add_content(node_id, content, position=0)

        return None                                                             # External script (no content)

    def _add_content(self, node_id  : Node_Id ,                                 # Add content to a script element
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

    def get_script_content(self, node_id: Node_Id) -> Optional[str]:            # Get JavaScript content for a script element
        edges = self.outgoing_edges(node_id)
        for edge in edges:
            if self.edge_predicate(edge) == self.PREDICATE_CONTENT:
                content_node_id = edge.edge.data.to_node_id
                return self.node_value(content_node_id)
        return None                                                             # External script or no content

    def is_inline_script(self, node_id: Node_Id) -> bool:                       # Check if script has inline content
        return self.get_script_content(node_id) is not None

    def is_external_script(self, node_id: Node_Id) -> bool:                     # Check if script is external (no content)
        return self.get_script_content(node_id) is None

    def is_script_anchor(self, node_id: Node_Id) -> bool:                      # Check if node is a script anchor (registered script element)
        node_path = self.node_path(node_id)
        if node_path:
            path_str = str(node_path)
            return path_str.startswith('script:')                               # Script anchors have path like "script:{node_id}"
        return False

    def get_all_scripts(self) -> List[Node_Id]:                                 # Get all script element node_ids in order
        scripts = []
        edges   = self.outgoing_edges(self.root_id)

        scripts_with_pos = []
        for edge in edges:
            if self.edge_predicate(edge) == self.PREDICATE_SCRIPT:
                edge_path = self.edge_path(edge)
                position  = int(str(edge_path)) if edge_path else 0
                scripts_with_pos.append((position, edge.edge.data.to_node_id))

        scripts_with_pos.sort(key=lambda x: x[0])
        return [node_id for _, node_id in scripts_with_pos]

    def get_inline_scripts(self) -> List[Node_Id]:                              # Get only inline scripts (with content)
        return [node_id for node_id in self.get_all_scripts()
                if self.is_inline_script(node_id)]

    def get_external_scripts(self) -> List[Node_Id]:                            # Get only external scripts (no content)
        return [node_id for node_id in self.get_all_scripts()
                if self.is_external_script(node_id)]

    # todo: see how this can be implemented since this graph doesn't have access to the scripts attributes
    # def get_script_src(self, node_id: Node_Id) -> Optional[str]:                # Get src attribute for external script
    #     for edge in self.outgoing_edges(node_id):
    #         edge_path = self.edge_path(edge)
    #         if edge_path and str(edge_path) == 'src':                           # Edge labeled 'src' points to src value
    #             target_id = edge.edge.data.to_node_id
    #             return self.node_value(target_id)
    #     return None

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Methods (override base)
    # ═══════════════════════════════════════════════════════════════════════════

    def stats(self) -> Schema__Html_MGraph__Stats__Scripts:                     # Get statistics about the scripts graph
        total_scripts    = 0
        inline_scripts   = 0
        external_scripts = 0

        for node_id in self.nodes_ids():
            if self.is_script_anchor(node_id):
                total_scripts += 1
                if self.get_script_content(node_id):                            # Has inline content
                    inline_scripts += 1
                elif self.is_external_script(node_id):                              # Has external src
                    external_scripts += 1

        return Schema__Html_MGraph__Stats__Scripts(
            total_nodes      = len(list(self.mgraph.data().nodes_ids())) ,
            total_edges      = len(list(self.mgraph.data().edges_ids())) ,
            root_id          = self.root_id                              ,
            total_scripts    = total_scripts                             ,
            inline_scripts   = inline_scripts                            ,
            external_scripts = external_scripts                          )
