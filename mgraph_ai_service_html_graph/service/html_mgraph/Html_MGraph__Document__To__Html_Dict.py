from typing                                                                     import Dict, Any, List, Optional
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Document     import Html_MGraph__Document
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id               import Node_Id


class Html_MGraph__Document__To__Html_Dict(Type_Safe):                          # Convert Html_MGraph__Document to OSBot Html_Dict format
    """Converts Html_MGraph__Document to Html_Dict (OSBot format).

    Pipeline:
        Html_MGraph__Document
            → Build root dict with tag='html' and attributes
            → Recursively build <head> nodes
            → Recursively build <body> nodes
            → For each element:
                - Get tag from attrs_graph
                - Get attributes from attrs_graph
                - Get children (text + elements) ordered by position
                - Get script/style content from respective graphs
        Html_Dict

    Output format:
        {
            'tag': 'html',
            'attrs': {'lang': 'en'},
            'nodes': [
                {'tag': 'head', 'attrs': {}, 'nodes': [...]},
                {'tag': 'body', 'attrs': {}, 'nodes': [...]}
            ]
        }

    Text nodes format:
        {'type': 'TEXT', 'data': 'text content'}
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Conversion
    # ═══════════════════════════════════════════════════════════════════════════

    def convert(self, document: Html_MGraph__Document) -> Dict[str, Any]:       # Convert Document to Html_Dict
        html_dict = { 'tag'   : 'html'                                  ,
                      'attrs' : document.get_attributes(document.root_id),
                      'nodes' : []                                       }

        if document.head_graph.root_id:                                         # Add <head>
            head_dict = self._build_head_dict(document, document.head_graph.root_id)
            if head_dict:
                html_dict['nodes'].append(head_dict)

        if document.body_graph.root_id:                                         # Add <body>
            body_dict = self._build_body_dict(document, document.body_graph.root_id)
            if body_dict:
                html_dict['nodes'].append(body_dict)

        return html_dict

    # ═══════════════════════════════════════════════════════════════════════════
    # Head Building
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_head_dict(self, document : Html_MGraph__Document ,
                               node_id  : Node_Id
                        ) -> Optional[Dict[str, Any]]:                          # Build dict for head element
        tag = document.get_tag(node_id)
        if not tag:
            return None

        element_dict = { 'tag'   : tag                               ,
                         'attrs' : document.get_attributes(node_id)  ,
                         'nodes' : []                                 }

        children = self._get_ordered_children(document, node_id, in_head=True)

        for child_type, child_id, _ in children:
            if child_type == 'text':
                text = document.head_graph.node_value(child_id)
                if text:
                    element_dict['nodes'].append({'type': 'TEXT', 'data': text})
            elif child_type == 'element':
                child_tag = document.get_tag(child_id)
                if child_tag == 'script':
                    child_dict = self._build_script_dict(document, child_id)
                elif child_tag == 'style':
                    child_dict = self._build_style_dict(document, child_id)
                else:
                    child_dict = self._build_head_dict(document, child_id)
                if child_dict:
                    element_dict['nodes'].append(child_dict)

        return element_dict

    # ═══════════════════════════════════════════════════════════════════════════
    # Body Building
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_body_dict(self, document : Html_MGraph__Document ,
                               node_id  : Node_Id
                        ) -> Optional[Dict[str, Any]]:                          # Build dict for body element
        tag = document.get_tag(node_id)
        if not tag:
            return None

        element_dict = { 'tag'   : tag                               ,
                         'attrs' : document.get_attributes(node_id)  ,
                         'nodes' : []                                 }

        children = self._get_ordered_children(document, node_id, in_head=False)

        for child_type, child_id, _ in children:
            if child_type == 'text':
                text = document.body_graph.node_value(child_id)
                if text:
                    element_dict['nodes'].append({'type': 'TEXT', 'data': text})
            elif child_type == 'element':
                child_tag = document.get_tag(child_id)
                if child_tag == 'script':
                    child_dict = self._build_script_dict(document, child_id)
                else:
                    child_dict = self._build_body_dict(document, child_id)
                if child_dict:
                    element_dict['nodes'].append(child_dict)

        return element_dict

    # ═══════════════════════════════════════════════════════════════════════════
    # Script/Style Building
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_script_dict(self, document : Html_MGraph__Document ,
                                 node_id  : Node_Id
                          ) -> Dict[str, Any]:                                  # Build dict for script element
        script_dict = { 'tag'   : 'script'                           ,
                        'attrs' : document.get_attributes(node_id)   ,
                        'nodes' : []                                  }

        content = document.get_script_content(node_id)
        if content:
            script_dict['nodes'].append({'type': 'TEXT', 'data': content})

        return script_dict

    def _build_style_dict(self, document : Html_MGraph__Document ,
                                node_id  : Node_Id
                         ) -> Dict[str, Any]:                                   # Build dict for style element
        style_dict = { 'tag'   : 'style'                            ,
                       'attrs' : document.get_attributes(node_id)   ,
                       'nodes' : []                                  }

        content = document.get_style_content(node_id)
        if content:
            style_dict['nodes'].append({'type': 'TEXT', 'data': content})

        return style_dict

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _get_ordered_children(self, document : Html_MGraph__Document ,
                                    node_id  : Node_Id               ,
                                    in_head  : bool = False
                             ) -> List[tuple]:                                  # Get children (text + elements) ordered by position
        graph = document.head_graph if in_head else document.body_graph

        all_children = []
        for edge in graph.outgoing_edges(node_id):
            predicate = graph.edge_predicate(edge)
            edge_path = graph.edge_path(edge)
            position  = int(str(edge_path)) if edge_path else 0
            target_id = edge.edge.data.to_node_id

            if predicate == graph.PREDICATE_TEXT:
                all_children.append(('text', target_id, position))
            elif predicate == graph.PREDICATE_CHILD:
                all_children.append(('element', target_id, position))

        all_children.sort(key=lambda x: x[2])                                   # Sort by position
        return all_children