from typing                          import Dict, Any, List
from osbot_utils.type_safe.Type_Safe import Type_Safe


class Html_Dict__OSBot__To__Html_Dict(Type_Safe):                                           # Adapter to convert OSBot-Utils Html__To__Html_Dict format to Html_MGraph format
    """
    Converts from OSBot-Utils format:
        {
            'tag': 'div',
            'attrs': {'class': 'main'},
            'nodes': [
                {'tag': 'p', 'attrs': {}, 'nodes': [...]},
                {'data': 'text content', 'type': 'TEXT'}
            ]
        }

    To Html_MGraph format:
        {
            'tag': 'div',
            'attrs': {'class': 'main'},
            'child_nodes': [
                {'tag': 'p', 'attrs': {}, 'child_nodes': [], 'text_nodes': [], 'position': 0}
            ],
            'text_nodes': [
                {'data': 'text content', 'position': 1}
            ]
        }
    """

    def convert(self, osbot_dict: Dict[str, Any]) -> Dict[str, Any]:                        # Convert OSBot-Utils Html_Dict to Html_MGraph format
        if not osbot_dict:
            return {}

        return self._convert_element(osbot_dict)

    def _convert_element(self, element: Dict[str, Any]) -> Dict[str, Any]:                  # Convert a single element from OSBot format to Html_MGraph format
        tag         = element.get('tag', 'unknown')
        attrs       = element.get('attrs', {})
        nodes       = element.get('nodes', [])

        child_nodes = []                                                                    # Separate nodes into child_nodes and text_nodes
        text_nodes  = []

        for position, node in enumerate(nodes):
            if self._is_text_node(node):
                text_data = node.get('data', '')
                if self._has_meaningful_content(text_data):                                 # Skip whitespace-only text nodes
                    text_nodes.append({ 'data'    : text_data ,
                                        'position': position  })
            else:
                child_dict = self._convert_element(node)                                    # Recursively convert child element
                child_dict['position'] = position
                child_nodes.append(child_dict)

        return { 'tag'        : tag         ,
                 'attrs'      : attrs       ,
                 'child_nodes': child_nodes ,
                 'text_nodes' : text_nodes  }

    def _is_text_node(self, node: Dict[str, Any]) -> bool:                                  # Check if a node is a text node (has 'type': 'TEXT' or has 'data' without 'tag')
        if node.get('type') == 'TEXT':
            return True
        if 'data' in node and 'tag' not in node:
            return True
        return False

    def _has_meaningful_content(self, text: str) -> bool:                                   # Check if text has meaningful content (not just whitespace/newlines)
        if not text:
            return False
        stripped = text.strip()
        if not stripped:                                                                    # Pure whitespace only
            return False
        return True                                                                         # Has some non-whitespace content