from typing                                                                                 import Dict, List, Any
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base

class Graph_Transformation__Text_Blocks_Only(Graph_Transformation__Base):
    """Show only elements that contain direct text content (text-bearing elements).

    Use case: Quick view of "where is the actual content?"
              Filters out structural wrappers that have no text.

    Behavior:
    - Keep only elements with text node children
    - Keep parent chain to root (for context)
    - Remove purely structural nodes with no text descendants
    - Useful for content analysis and extraction
    """

    name         : str = 'text_blocks_only'
    description  : str = 'Show only elements containing direct text content'
    label        : str = 'Text Blocks Only'

    def transform_dict(self, html_dict: Dict) -> Dict:                                      # Phase 2: Transform the Html_Dict structure
        if not html_dict:
            return html_dict
        return self._filter_element(html_dict)

    def _filter_element(self, element: Dict) -> Dict:                                       # Recursively filter to keep only text-bearing elements
        if not isinstance(element, dict):
            return element

        children = element.get('children', [])

        if not children:
            return element

        has_direct_text = self._has_direct_text(children)                                   # Check if this element has direct text
        new_children    = []

        for child in children:                                                              # Process children
            if isinstance(child, dict):
                if child.get('type') == 'text':
                    if has_direct_text:                                                     # Keep text nodes only if parent has direct text
                        new_children.append(child)
                elif child.get('tag'):
                    filtered_child = self._filter_element(child)                            # Recurse into element children
                    if self._has_text_descendant(filtered_child):                           # Only keep if it or descendants have text
                        new_children.append(filtered_child)
            else:
                new_children.append(child)

        element['children'] = new_children

        if has_direct_text:                                                                 # Mark element as text-bearing for visualization
            element['has_text'] = True

        return element

    def _has_direct_text(self, children: List) -> bool:                                     # Check if children include direct text nodes with content
        for child in children:
            if isinstance(child, dict) and child.get('type') == 'text':
                text = child.get('text', '').strip()
                if text:
                    return True
        return False

    def _has_text_descendant(self, element: Dict) -> bool:                                  # Check if element or any descendant has text content
        if not isinstance(element, dict):
            return False

        if element.get('has_text'):                                                         # Already marked as having text
            return True

        children = element.get('children', [])

        for child in children:
            if isinstance(child, dict):
                if child.get('type') == 'text':
                    text = child.get('text', '').strip()
                    if text:
                        return True
                elif self._has_text_descendant(child):                                      # Recurse
                    return True

        return False
