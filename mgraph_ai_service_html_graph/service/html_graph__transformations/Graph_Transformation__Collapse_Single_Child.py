from typing                                                                                 import Dict, List, Any
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base

class Graph_Transformation__Collapse_Single_Child(Graph_Transformation__Base):
    """Collapse single-child chains: when a parent has exactly one child element.

    Use case: <div> -> <div> -> <p> -> <ul> (each with only one child)
              Collapse to show meaningful structure without wrapper noise.

    Behavior:
    - Find chains where each node has exactly one element child
    - Collapse intermediate nodes, connecting grandparent to meaningful descendant
    - Preserve nodes with multiple children or with direct text content
    - Optionally annotate collapsed depth for debugging
    """

    name        : str = 'collapse_single_child'
    description : str = 'Collapse single-child element chains'
    label       : str = 'Collapse Single Child'

    def transform_dict(self, html_dict: Dict) -> Dict:                                      # Phase 2: Transform the Html_Dict structure
        if not html_dict:
            return html_dict
        return self._collapse_element(html_dict)

    def _collapse_element(self, element: Dict) -> Dict:                                     # Recursively collapse single-child chains
        if not isinstance(element, dict):
            return element

        children = element.get('children', [])

        if not children:
            return element

        element_children = self._get_element_children(children)                             # Get only element children (not text nodes)

        if len(element_children) == 1 and not self._has_direct_text(children):              # Single element child with no direct text
            single_child = element_children[0]

            if single_child.get('tag'):                                                     # Only collapse if it's an actual element
                collapsed      = self._collapse_element(single_child)                       # Recurse first to collapse nested chains
                collapsed_path = element.get('collapsed_path', [])                          # Track the collapsed path for debugging
                collapsed_path.append(element.get('tag', ''))

                if 'collapsed_path' in collapsed:                                           # Merge paths if child was also collapsed
                    collapsed['collapsed_path'] = collapsed_path + collapsed['collapsed_path']
                else:
                    collapsed['collapsed_path'] = collapsed_path

                return collapsed

        new_children = []                                                                   # Multiple children or has text: process each child
        for child in children:
            if isinstance(child, dict) and child.get('tag'):
                new_children.append(self._collapse_element(child))
            else:
                new_children.append(child)

        element['children'] = new_children
        return element

    def _get_element_children(self, children: List) -> List[Dict]:                          # Filter to get only element children (with tags)
        return [child for child in children
                if isinstance(child, dict) and child.get('tag')]

    def _has_direct_text(self, children: List) -> bool:                                     # Check if children include direct text nodes with content
        for child in children:
            if isinstance(child, dict):
                if child.get('type') == 'text':
                    text = child.get('text', '').strip()
                    if text:
                        return True
        return False
