from typing                                                                     import Dict, Any, List, Optional
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Attributes   import Html_MGraph__Attributes
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Base         import Html_MGraph__Base
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Body         import Html_MGraph__Body
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Head         import Html_MGraph__Head
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Scripts      import Html_MGraph__Scripts
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Styles       import Html_MGraph__Styles
from mgraph_db.mgraph.MGraph                                                    import MGraph
from mgraph_db.mgraph.schemas.identifiers.Node_Path                             import Node_Path
from mgraph_db.mgraph.schemas.identifiers.Edge_Path                             import Edge_Path
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id               import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id               import Safe_Id


class Html_MGraph__Document(Html_MGraph__Base):                                 # Orchestrator graph holding references to all component graphs
    mgraph : MGraph                                                             # this is the only class that initialises this
    """Represents a complete HTML document as multiple interconnected graphs.
    
    The Document graph:
    - Has root_id = d0 representing the <html> element
    - Contains value nodes storing root_ids of component graphs
    - Links to Head, Body, Attributes, Scripts, Styles graphs
    
    Structure:
        d0 (<html> element)
        ├──[graph:head]──► h1 (root of Html_MGraph__Head)
        ├──[graph:body]──► n1 (root of Html_MGraph__Body)
        ├──[graph:attrs]──► a0 (root of Html_MGraph__Attributes)
        ├──[graph:scripts]──► s0 (root of Html_MGraph__Scripts)
        └──[graph:styles]──► t0 (root of Html_MGraph__Styles)
    
    Shared Node_Ids:
    - Element nodes in Body/Head use same IDs as in Attributes/Scripts/Styles
    - Enables cross-graph lookups: get_tag(node_id), get_attributes(node_id)
    
    This class provides:
    - Unified access to all component graphs
    - Convenience methods that span multiple graphs
    - Round-trip conversion to/from HTML
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # Constants
    # ═══════════════════════════════════════════════════════════════════════════

    PREDICATE_GRAPH : Safe_Id = Safe_Id('graph')                                # Edge predicate for graph references
    PATH_HTML       : str     = 'html'                                          # Node path for <html> element

    # ═══════════════════════════════════════════════════════════════════════════
    # Component Graphs
    # ═══════════════════════════════════════════════════════════════════════════

    head_graph   : Html_MGraph__Head       = None                               # <head> element structure + text
    body_graph   : Html_MGraph__Body       = None                               # <body> element structure + text
    attrs_graph  : Html_MGraph__Attributes = None                               # Tags and attributes for all elements
    scripts_graph: Html_MGraph__Scripts    = None                               # JavaScript content
    styles_graph : Html_MGraph__Styles     = None                               # CSS content

    def setup(self) -> 'Html_MGraph__Document':                                 # Initialize all component graphs
        self.mgraph = MGraph()
        root_node    = self.new_element_node(node_path=Node_Path(self.PATH_HTML))  # Create <html> root node
        self.root_id = root_node.node_id

        self.head_graph    = Html_MGraph__Head      ().setup()                  # Initialize component graphs
        self.body_graph    = Html_MGraph__Body      ().setup()
        self.attrs_graph   = Html_MGraph__Attributes().setup()
        self.scripts_graph = Html_MGraph__Scripts   ().setup()
        self.styles_graph  = Html_MGraph__Styles    ().setup()

        self._link_component_graph('head'   , self.head_graph   .root_id)       # Create graph reference edges
        self._link_component_graph('body'   , self.body_graph   .root_id)
        self._link_component_graph('attrs'  , self.attrs_graph  .root_id)
        self._link_component_graph('scripts', self.scripts_graph.root_id)
        self._link_component_graph('styles' , self.styles_graph .root_id)

        self.attrs_graph.register_element(self.root_id, 'html')                 # Register <html> in attributes

        return self

    def _link_component_graph(self, name: str, component_root_id: Node_Id) -> None:  # Create edge from document root to component graph root
        ref_node = self.new_value_node(value     = str(component_root_id) ,
                                       node_path = Node_Path(f"graph:{name}"))
        self.new_edge(from_node_id = self.root_id          ,
                      to_node_id   = ref_node.node_id      ,
                      predicate    = self.PREDICATE_GRAPH  ,
                      edge_path    = Edge_Path(name)       )

    # ═══════════════════════════════════════════════════════════════════════════
    # Cross-Graph Query Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def get_tag(self, node_id: Node_Id) -> Optional[str]:                       # Get HTML tag for any element node
        return self.attrs_graph.get_tag(node_id)

    def get_attributes(self, node_id: Node_Id) -> Dict[str, str]:               # Get all attributes for any element
        return self.attrs_graph.get_attributes(node_id)

    def get_attribute(self, node_id: Node_Id, attr_name: str) -> Optional[str]: # Get specific attribute value
        return self.attrs_graph.get_attribute(node_id, attr_name)

    def get_elements_by_tag(self, tag: str) -> List[Node_Id]:                   # Get all elements with a specific tag
        return self.attrs_graph.get_elements_by_tag(tag)

    def get_script_content(self, node_id: Node_Id) -> Optional[str]:            # Get JavaScript content for a script element
        return self.scripts_graph.get_script_content(node_id)

    def get_style_content(self, node_id: Node_Id) -> Optional[str]:             # Get CSS content for a style element
        return self.styles_graph.get_style_content(node_id)

    def get_text_content(self, node_id  : Node_Id      ,                        # Get text content for an element
                               in_head  : bool = False
                        ) -> str:
        if in_head:
            return self.head_graph.get_text_content(node_id)
        return self.body_graph.get_text_content(node_id)

    # ═══════════════════════════════════════════════════════════════════════════
    # Element Information Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def element_info(self, node_id: Node_Id) -> Dict[str, Any]:                 # Get complete info for an element
        tag        = self.get_tag(node_id)
        attributes = self.get_attributes(node_id)

        info = { 'node_id'    : str(node_id) ,
                 'tag'        : tag          ,
                 'attributes' : attributes   }

        if tag == 'script':                                                     # Add content for special elements
            content = self.get_script_content(node_id)
            if content:
                info['script_content'] = content
        elif tag == 'style':
            content = self.get_style_content(node_id)
            if content:
                info['style_content'] = content

        return info

    # ═══════════════════════════════════════════════════════════════════════════
    # Tree Traversal Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def get_body_children(self, node_id: Node_Id) -> List[Node_Id]:             # Get child elements in body
        return self.body_graph.get_element_children(node_id)

    def get_head_children(self, node_id: Node_Id) -> List[Node_Id]:             # Get child elements in head
        return self.head_graph.get_element_children(node_id)

    def walk_body(self, node_id: Node_Id = None) -> List[Dict[str, Any]]:       # Walk body tree and collect element info
        if node_id is None:
            node_id = self.body_graph.root_id

        result  = [self.element_info(node_id)]
        children = self.get_body_children(node_id)

        for child_id in children:
            result.extend(self.walk_body(child_id))

        return result

    def walk_head(self, node_id: Node_Id = None) -> List[Dict[str, Any]]:       # Walk head tree and collect element info
        if node_id is None:
            node_id = self.head_graph.root_id

        result   = [self.element_info(node_id)]
        children = self.get_head_children(node_id)

        for child_id in children:
            result.extend(self.walk_head(child_id))

        return result

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Methods (override base)
    # ═══════════════════════════════════════════════════════════════════════════

    def stats(self) -> Dict[str, Any]:                                          # Get comprehensive statistics
        return { 'document'   : super().stats()                    ,
                 'head'       : self.head_graph   .stats()         ,
                 'body'       : self.body_graph   .stats()         ,
                 'attributes' : self.attrs_graph  .stats()         ,
                 'scripts'    : self.scripts_graph.stats()         ,
                 'styles'     : self.styles_graph .stats()         }

    # ═══════════════════════════════════════════════════════════════════════════
    # Serialization Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def to_json(self) -> Dict[str, Any]:                                        # Export all graphs to JSON
        return { 'document'   : super().to_json()                  ,
                 'head'       : self.head_graph   .to_json()       ,
                 'body'       : self.body_graph   .to_json()       ,
                 'attributes' : self.attrs_graph  .to_json()       ,
                 'scripts'    : self.scripts_graph.to_json()       ,
                 'styles'     : self.styles_graph .to_json()       }
