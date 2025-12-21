from typing                                                                                            import Dict, Any, List, Optional
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document                     import Html_MGraph__Document
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document       import Html__To__Html_MGraph__Document
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html       import Html_MGraph__Document__To__Html
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html_Dict  import Html_MGraph__Document__To__Html_Dict
from mgraph_ai_service_html_graph.schemas.html.Schema__Html_MGraph                                     import Schema__Html_MGraph__Stats__Document
from mgraph_ai_service_html_graph.schemas.html.Schema__Html_MGraph                                     import Schema__Html_MGraph__Element_Info
from osbot_utils.helpers.html.transformers.Html_Dict__To__Html                                         import Html_Dict__To__Html
from osbot_utils.type_safe.Type_Safe                                                                   import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                                      import Node_Id


class Html_MGraph(Type_Safe):                                                   # Main public API for HTML Graph operations
    """Facade class providing unified access to HTML multi-graph architecture.

    This is the primary interface for working with HTML as a graph structure.
    It wraps Html_MGraph__Document and provides convenient methods for:
    - Creating graphs from HTML
    - Exporting to various formats (HTML, Dict, DOT, JSON)
    - Querying elements, attributes, scripts, styles
    - Visualization (screenshots)

    Usage:
        # From HTML string
        html_mgraph = Html_MGraph.from_html('<html>...</html>')

        # Access underlying document
        html_mgraph.document.body_graph
        html_mgraph.document.head_graph

        # Export
        html_str  = html_mgraph.to_html()
        html_dict = html_mgraph.to_html_dict()

        # Query
        tag   = html_mgraph.get_tag(node_id)
        attrs = html_mgraph.get_attributes(node_id)
    """

    document : Html_MGraph__Document = None                                     # The underlying multi-graph document

    # ═══════════════════════════════════════════════════════════════════════════
    # Factory Methods
    # ═══════════════════════════════════════════════════════════════════════════

    @classmethod
    def from_html(cls, html: str) -> 'Html_MGraph':                             # Create Html_MGraph from HTML string
        document = Html__To__Html_MGraph__Document().convert(html)
        return cls(document=document)

    @classmethod
    def from_html_dict(cls, html_dict: Dict[str, Any]) -> 'Html_MGraph':        # Create Html_MGraph from Html_Dict
        html     = Html_Dict__To__Html(root=html_dict).convert()
        document = Html__To__Html_MGraph__Document().convert(html)
        return cls(document=document)

    # ═══════════════════════════════════════════════════════════════════════════
    # Export Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def to_html(self) -> str:                                                   # Convert to HTML string
        return Html_MGraph__Document__To__Html().convert(self.document)

    def to_html_dict(self) -> Dict[str, Any]:                                   # Convert to Html_Dict format
        return Html_MGraph__Document__To__Html_Dict().convert(self.document)

    def to_json(self) -> Dict[str, Any]:                                        # Export document structure as JSON
        return self.document.to_json()

    def to_dot(self, graph: str = 'all') -> str:                                  # Convert to DOT format for visualization
        from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__To__Dot import Html_MGraph__To__Dot
        converter = Html_MGraph__To__Dot()

        if graph == 'all':
            return converter.convert(self)
        elif graph == 'head':
            return converter.head_only(self)
        elif graph == 'body':
            return converter.body_only(self)
        elif graph == 'attrs':
            return converter.attrs_only(self)
        elif graph == 'scripts':
            return converter.scripts_only(self)
        elif graph == 'styles':
            return converter.styles_only(self)
        else:
            return converter.convert(self)

    # ═══════════════════════════════════════════════════════════════════════════
    # Visualization Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def screenshot(self, output_path: str = None):                              # Generate visual screenshot of the graph
        # TODO: Implement using MGraph__Screenshot with new architecture
        raise NotImplementedError("Screenshot not yet implemented for new architecture")

    # ═══════════════════════════════════════════════════════════════════════════
    # Query Methods - Element Access
    # ═══════════════════════════════════════════════════════════════════════════

    def get_tag(self, node_id: Node_Id) -> Optional[str]:                       # Get tag name for a node
        return self.document.get_tag(node_id)

    def get_attributes(self, node_id: Node_Id) -> Dict[str, str]:               # Get all attributes for a node
        return self.document.get_attributes(node_id)

    def get_attribute(self, node_id: Node_Id, attr_name: str) -> Optional[str]: # Get specific attribute value
        attrs = self.document.get_attributes(node_id)
        return attrs.get(attr_name)

    # ═══════════════════════════════════════════════════════════════════════════
    # Query Methods - Structure Navigation
    # ═══════════════════════════════════════════════════════════════════════════

    def root_id(self) -> Node_Id:                                               # Get root <html> node ID
        return self.document.root_id

    def head_root_id(self) -> Optional[Node_Id]:                                # Get <head> root node ID
        return self.document.head_graph.root_id

    def body_root_id(self) -> Optional[Node_Id]:                                # Get <body> root node ID
        return self.document.body_graph.root_id

    def get_head_children(self) -> List[Node_Id]:                               # Get direct children of <head>
        head_root = self.document.head_graph.root_id
        if head_root:
            return self.document.get_head_children(head_root)
        return []

    def get_body_children(self) -> List[Node_Id]:                               # Get direct children of <body>
        body_root = self.document.body_graph.root_id
        if body_root:
            return self.document.get_body_children(body_root)
        return []

    # ═══════════════════════════════════════════════════════════════════════════
    # Query Methods - Content Access
    # ═══════════════════════════════════════════════════════════════════════════

    def get_script_content(self, node_id: Node_Id) -> Optional[str]:            # Get script content for a <script> element
        return self.document.get_script_content(node_id)

    def get_style_content(self, node_id: Node_Id) -> Optional[str]:             # Get style content for a <style> element
        return self.document.get_style_content(node_id)

    def get_text_content(self, node_id: Node_Id) -> str:                        # Get text content for an element
        if self.document.head_graph.root_id:                                    # Try head graph first
            text = self.document.head_graph.get_text_content(node_id)
            if text:
                return text
        if self.document.body_graph.root_id:                                    # Then body graph
            text = self.document.body_graph.get_text_content(node_id)
            if text:
                return text
        return ''

    # ═══════════════════════════════════════════════════════════════════════════
    # Query Methods - Walking/Iteration
    # ═══════════════════════════════════════════════════════════════════════════

    def walk_head(self, start_node_id: Node_Id = None):                         # Walk head graph nodes
        return self.document.walk_head(start_node_id)

    def walk_body(self, start_node_id: Node_Id = None):                         # Walk body graph nodes
        return self.document.walk_body(start_node_id)

    # ═══════════════════════════════════════════════════════════════════════════
    # Graph Access (for advanced usage)
    # ═══════════════════════════════════════════════════════════════════════════

    @property
    def head_graph(self):                                                       # Direct access to head graph
        return self.document.head_graph

    @property
    def body_graph(self):                                                       # Direct access to body graph
        return self.document.body_graph

    @property
    def attrs_graph(self):                                                      # Direct access to attributes graph
        return self.document.attrs_graph

    @property
    def scripts_graph(self):                                                    # Direct access to scripts graph
        return self.document.scripts_graph

    @property
    def styles_graph(self):                                                     # Direct access to styles graph
        return self.document.styles_graph

    # ═══════════════════════════════════════════════════════════════════════════
    # Statistics
    # ═══════════════════════════════════════════════════════════════════════════

    def stats(self) -> Schema__Html_MGraph__Stats__Document:                    # Get comprehensive statistics
        if self.document:
            return self.document.stats()
        return Schema__Html_MGraph__Stats__Document()

    # ═══════════════════════════════════════════════════════════════════════════
    # Element Info (convenience method)
    # ═══════════════════════════════════════════════════════════════════════════

    def element_info(self, node_id: Node_Id) -> Schema__Html_MGraph__Element_Info:  # Get comprehensive info about an element
        return self.document.element_info(node_id)