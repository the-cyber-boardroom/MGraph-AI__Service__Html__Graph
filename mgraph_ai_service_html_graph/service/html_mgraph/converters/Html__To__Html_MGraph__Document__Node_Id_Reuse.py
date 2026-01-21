# ═══════════════════════════════════════════════════════════════════════════════
# Html → Html_MGraph Document Converter (Node_Id Reuse Variant)
# Subclass that reuses node_id values from Html_Dict when present
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                             import Dict, Any
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids    import Html__To__Html_Dict__With__Node_Ids
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document        import Html__To__Html_MGraph__Document, SCRIPT_TAGS, STYLE_TAGS
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document                      import Html_MGraph__Document
from mgraph_db.mgraph.schemas.identifiers.Node_Path                                                     import Node_Path
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                                       import Node_Id

STRING__NODE_ID = 'node_id'                                                                       # Html_Dict node id key

"""Parse HTML to Html_MGraph__Document with unique node_id on every node.

Part of "html_roundtrip_of_node_consolidation" Phased development.
See: PHASE_B__brief.md
"""
# todo: see best way to refactor this with main Html__To__Html_MGraph__Document

class Html__To__Html_MGraph__Document__Node_Id_Reuse(
        Html__To__Html_MGraph__Document):                                                         # Html → MGraph (node_id reuse)

    # ═══════════════════════════════════════════════════════════════════════════
    # Convert html using the new Html__To__Html_Dict__With__Node_Ids
    # ═══════════════════════════════════════════════════════════════════════════

    def convert(self, html: str) -> Html_MGraph__Document:                  # Convert HTML string to Document
        html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()                # Parse HTML to dict
        return self.convert_from_dict(html_dict)

    # ═══════════════════════════════════════════════════════════════════════════
    # Node_Id Generation Policy
    # ═══════════════════════════════════════════════════════════════════════════

    def _generate_node_id(self, node_dict: Dict[str, Any] = None) -> Node_Id:                     # Generate or reuse Node_Id
        if node_dict and STRING__NODE_ID in node_dict:
            return Node_Id(node_dict[STRING__NODE_ID])                                            # Reuse from Html_Dict
        return super()._generate_node_id()                                                        # Fallback to base behavior

    # ═══════════════════════════════════════════════════════════════════════════
    # Head Processing (Node_Id Aware)
    # ═══════════════════════════════════════════════════════════════════════════

    def _process_head(self, document, head_dict):                                                 # Process <head> element
        head_node_id = self._generate_node_id(head_dict)

        document.head_graph.create_element(node_path = Node_Path('head'),
                                           node_id   = head_node_id     )
        document.head_graph.set_root(head_node_id)
        document.attrs_graph.register_element(head_node_id, 'head')

        for position, (key, value) in enumerate(head_dict.get('attrs', {}).items()):
            document.attrs_graph.add_attribute(head_node_id, key, value, position)

        self._process_head_children(document, head_node_id, head_dict, 'head')

    def _process_head_children(self,
                               document                     ,
                               parent_id   : Node_Id        ,
                               parent_dict : Dict[str, Any] ,
                               parent_path : str            ,
                               node_id     : Node_Id = None ):                                          # Recurse head children
        for position, node in enumerate(parent_dict.get('nodes', [])):
            if isinstance(node, dict) is False:
                continue

            if self._is_text_node(node):
                text = node.get('data', '')
                if text.strip():
                    document.head_graph.create_text(text      = text,
                                                    parent_id = parent_id,
                                                    position  = position,
                                                    node_id   = self._generate_node_id(node))
            elif 'tag' in node:
                tag       = node.get('tag', '').lower()
                if node_id is None:
                    node_id   = self._generate_node_id(node)
                node_path = f"{parent_path}.{tag}"

                document.head_graph.create_element(node_path = Node_Path(node_path),
                                                   node_id   = node_id              )
                document.head_graph.add_child(parent_id, node_id, position)

                document.attrs_graph.register_element(node_id, tag)
                for attr_pos, (key, value) in enumerate(node.get('attrs', {}).items()):
                    document.attrs_graph.add_attribute(node_id, key, value, attr_pos)

                if tag in SCRIPT_TAGS:
                    document.scripts_graph.register_script(node_id,
                                                            self._extract_text_content(node))
                elif tag in STYLE_TAGS:
                    if tag == 'link':
                        document.styles_graph.register_link(node_id)
                    else:
                        document.styles_graph.register_style(node_id,
                                                             self._extract_text_content(node))
                else:
                    self._process_head_children(document, node_id, node, node_path)

    # ═══════════════════════════════════════════════════════════════════════════
    # Body Processing (Node_Id Aware)
    # ═══════════════════════════════════════════════════════════════════════════

    def _process_body(self, document, body_dict):                                                 # Process <body> element
        body_node_id = self._generate_node_id(body_dict)

        document.body_graph.create_element(node_path = Node_Path('body'),
                                           node_id   = body_node_id     )
        document.body_graph.set_root(body_node_id)
        document.attrs_graph.register_element(body_node_id, 'body')

        for position, (key, value) in enumerate(body_dict.get('attrs', {}).items()):
            document.attrs_graph.add_attribute(body_node_id, key, value, position)

        self._process_body_children(document, body_node_id, body_dict, 'body')

    def _process_body__text_node(self,
                                 document  ,
                                 parent_id : Node_Id ,
                                 node      : Dict[str, Any],
                                 position  : int      ):                                         # Body text node
        text = node.get('data', '')
        if text.strip():
            node_id = self._generate_node_id(node)
            document.body_graph.create_text(text      = text     ,
                                            parent_id = parent_id,
                                            position  = position ,
                                            node_id   = node_id  )

    def _process_body__element(self,
                               document  ,
                               parent_id : Node_Id ,
                               node      : Dict[str, Any],
                               position  : int      ,
                               tag       : str      ,
                               node_path : str      ):                                         # Body element node
        node_id = self._generate_node_id(node)

        self._process_body__create_in_graph(document, parent_id, node_id, position, node_path)
        self._process_body__register_attrs(document, node_id, tag, node)

        if tag in SCRIPT_TAGS:
            self._process_body__handle_script(document, node_id, node)
        else:
            self._process_body_children(document, node_id, node, node_path)
