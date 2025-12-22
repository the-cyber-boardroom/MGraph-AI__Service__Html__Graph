from typing                                                                         import Dict, Any, List, Optional, Tuple, Set
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document  import Html_MGraph__Document
from mgraph_db.mgraph.schemas.identifiers.Node_Path                                 import Node_Path
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                   import Node_Id
from osbot_utils.helpers.html.transformers.Html__To__Html_Dict                      import Html__To__Html_Dict
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                    import Obj_Id

SCRIPT_TAGS : Set = {'script'}                                              # Tags that go to Scripts graph
STYLE_TAGS  : Set = {'style', 'link'}                                       # Tags that go to Styles graph

class Html__To__Html_MGraph__Document(Type_Safe):                               # Convert HTML string to multi-graph Document structure
    """Converts raw HTML to Html_MGraph__Document with 5 component graphs.
    
    Pipeline:
        HTML String
            → Parse to Html_Dict (OSBot format)
            → Separate <html>, <head>, <body> sections
            → Build component graphs with shared Node_Ids:
                - Head graph: <head> elements + text
                - Body graph: <body> elements + text
                - Attributes graph: tags + attrs for ALL elements
                - Scripts graph: JS content
                - Styles graph: CSS content
            → Link in Document orchestrator
        Html_MGraph__Document
    
    Node_Id sharing:
    - When creating element in Head/Body, same Node_Id is used in Attributes
    - Script/Style elements also share Node_Id with their parent graph
    - This enables cross-graph lookups
    """



    # ═══════════════════════════════════════════════════════════════════════════
    # Main Conversion
    # ═══════════════════════════════════════════════════════════════════════════

    def convert(self, html: str) -> Html_MGraph__Document:                      # Convert HTML string to Document
        html_dict = Html__To__Html_Dict(html=html).convert()                    # Parse HTML to dict
        return self.convert_from_dict(html_dict)

    def convert_from_dict(self, html_dict: Dict[str, Any]                       # Convert Html_Dict to Document
                         ) -> Html_MGraph__Document:
        document = Html_MGraph__Document().setup()                              # Create document with initialized graphs

        html_attrs = html_dict.get('attrs', {})                                 # Add <html> attributes
        for position, (attr_name, attr_value) in enumerate(html_attrs.items()):
            document.attrs_graph.add_attribute(document.root_id, attr_name, attr_value, position)

        head_dict, body_dict = self._extract_head_body(html_dict)               # Find <head> and <body> sections

        if head_dict:                                                           # Process <head>
            self._process_head(document, head_dict)

        if body_dict:                                                           # Process <body>
            self._process_body(document, body_dict)

        return document

    def _extract_head_body(self, html_dict: Dict[str, Any]                      # Extract <head> and <body> from html_dict
                          ) -> Tuple[Optional[Dict], Optional[Dict]]:
        head_dict = None
        body_dict = None

        nodes = html_dict.get('nodes', [])                                      # OSBot format uses 'nodes'
        for node in nodes:
            if isinstance(node, dict) and 'tag' in node:
                tag = node.get('tag', '').lower()
                if tag == 'head':
                    head_dict = node
                elif tag == 'body':
                    body_dict = node

        return head_dict, body_dict

    # ═══════════════════════════════════════════════════════════════════════════
    # Head Processing
    # ═══════════════════════════════════════════════════════════════════════════

    def _process_head(self, document: Html_MGraph__Document, head_dict: Dict[str, Any]) -> None:
        head_node_id = self._generate_node_id()                                 # Create <head> element
        document.head_graph.create_element(node_path = Node_Path('head'),
                                           node_id   = head_node_id     )
        document.head_graph.set_root(head_node_id)
        document.attrs_graph.register_element(head_node_id, 'head')

        head_attrs = head_dict.get('attrs', {})                                 # Add <head> attributes
        for position, (attr_name, attr_value) in enumerate(head_attrs.items()):
            document.attrs_graph.add_attribute(head_node_id, attr_name, attr_value, position)

        self._process_head_children(document, head_node_id, head_dict, 'head')  # Process children

    def _process_head_children(self, document    : Html_MGraph__Document ,
                                     parent_id   : Node_Id               ,
                                     parent_dict : Dict[str, Any]        ,
                                     parent_path : str                   ) -> None:
        nodes = parent_dict.get('nodes', [])
        for position, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue

            if self._is_text_node(node):                                        # Text node
                text = node.get('data', '')
                if text.strip():                                                # Skip whitespace-only
                    document.head_graph.create_text(text      = text      ,
                                                    parent_id = parent_id ,
                                                    position  = position  )
            elif 'tag' in node:                                                 # Element node
                tag       = node.get('tag', '').lower()
                node_path = f"{parent_path}.{tag}"
                node_id   = self._generate_node_id()

                document.head_graph.create_element(node_path = Node_Path(node_path),    # Create in head graph
                                                   node_id   = node_id              )
                document.head_graph.add_child(parent_id, node_id, position)

                document.attrs_graph.register_element(node_id, tag)             # Register in attributes graph
                attrs = node.get('attrs', {})
                for attr_pos, (attr_name, attr_value) in enumerate(attrs.items()):
                    document.attrs_graph.add_attribute(node_id, attr_name, attr_value, attr_pos)

                if tag in SCRIPT_TAGS:                                     # Handle script/style content
                    content = self._extract_text_content(node)
                    document.scripts_graph.register_script(node_id, content)
                elif tag in STYLE_TAGS:
                    if tag == 'link':
                        document.styles_graph.register_link(node_id)            # External stylesheet
                    else:
                        content = self._extract_text_content(node)
                        document.styles_graph.register_style(node_id, content)
                else:
                    self._process_head_children(document, node_id, node, node_path)  # Recurse for other elements

    # ═══════════════════════════════════════════════════════════════════════════
    # Body Processing
    # ═══════════════════════════════════════════════════════════════════════════

    def _process_body(self, document: Html_MGraph__Document, body_dict: Dict[str, Any]) -> None:
        body_node_id = self._generate_node_id()                                 # Create <body> element
        document.body_graph.create_element(node_path = Node_Path('body'),
                                           node_id   = body_node_id     )
        document.body_graph.set_root(body_node_id)
        document.attrs_graph.register_element(body_node_id, 'body')

        body_attrs = body_dict.get('attrs', {})                                 # Add <body> attributes
        for position, (attr_name, attr_value) in enumerate(body_attrs.items()):
            document.attrs_graph.add_attribute(body_node_id, attr_name, attr_value, position)

        self._process_body_children(document, body_node_id, body_dict, 'body')  # Process children

    def _process_body_children(self, document    : Html_MGraph__Document ,
                                     parent_id   : Node_Id               ,
                                     parent_dict : Dict[str, Any]        ,
                                     parent_path : str                   ) -> None:
        nodes        = parent_dict.get('nodes', [])
        tag_counts   = self._count_tags(nodes)                                  # For path indexing
        tag_occurrence = {}

        for position, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue

            if self._is_text_node(node):                                        # Text node
                text = node.get('data', '')
                if text.strip():                                                # Skip whitespace-only
                    document.body_graph.create_text(text      = text      ,
                                                    parent_id = parent_id ,
                                                    position  = position  )
            elif 'tag' in node:                                                 # Element node
                tag       = node.get('tag', '').lower()
                tag_index = tag_occurrence.get(tag, 0)
                tag_occurrence[tag] = tag_index + 1

                if tag_counts.get(tag, 0) > 1:                                  # Build node_path with index if needed
                    node_path = f"{parent_path}.{tag}[{tag_index}]"
                else:
                    node_path = f"{parent_path}.{tag}"

                node_id = self._generate_node_id()

                document.body_graph.create_element(node_path = Node_Path(node_path),    # Create in body graph
                                                   node_id   = node_id              )
                document.body_graph.add_child(parent_id, node_id, position)

                document.attrs_graph.register_element(node_id, tag)             # Register in attributes graph
                attrs = node.get('attrs', {})
                for attr_pos, (attr_name, attr_value) in enumerate(attrs.items()):
                    document.attrs_graph.add_attribute(node_id, attr_name, attr_value, attr_pos)

                if tag in SCRIPT_TAGS:                                     # Handle script content
                    content = self._extract_text_content(node)
                    document.scripts_graph.register_script(node_id, content)
                else:
                    self._process_body_children(document, node_id, node, node_path)  # Recurse (skip text for scripts)

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _generate_node_id(self) -> Node_Id:                                     # Generate unique node ID
        return Node_Id(Obj_Id())

    def _is_text_node(self, node: Dict[str, Any]) -> bool:                      # Check if node is a text node (OSBot format)
        if node.get('type') == 'TEXT':
            return True
        if 'data' in node and 'tag' not in node:
            return True
        return False

    def _extract_text_content(self, node: Dict[str, Any]) -> Optional[str]:     # Extract text content from nodes list
        texts = []
        for child in node.get('nodes', []):
            if isinstance(child, dict) and self._is_text_node(child):
                text = child.get('data', '')
                if text.strip():
                    texts.append(text)
        return ''.join(texts) if texts else None

    def _count_tags(self, nodes: List[Dict[str, Any]]) -> Dict[str, int]:       # Count occurrences of each tag
        counts = {}
        for node in nodes:
            if isinstance(node, dict) and 'tag' in node:
                tag = node.get('tag', '').lower()
                counts[tag] = counts.get(tag, 0) + 1
        return counts
