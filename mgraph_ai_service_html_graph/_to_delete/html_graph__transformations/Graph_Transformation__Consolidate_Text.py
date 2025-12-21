from typing                                                                                      import Dict, List, Any
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base

INLINE_TAGS = {'a', 'abbr', 'acronym', 'b', 'bdo', 'big', 'br', 'button', 'cite', 'code',
               'dfn', 'em', 'i', 'img', 'input', 'kbd', 'label', 'map', 'object', 'q',
               'samp', 'script', 'select', 'small', 'span', 'strong', 'sub', 'sup',
               'textarea', 'time', 'tt', 'u', 'var', 'mark'}

class Graph_Transformation__Consolidate_Text(Graph_Transformation__Base):   # Destructive consolidation: merge multiple text fragments under a parent into single text node.

    name         : str = 'consolidate_text'
    description  : str = 'Merge fragmented text nodes into single consolidated text (destructive)'
    label        : str = 'Consolidate Text'

    def transform_dict(self, html_dict: Dict) -> Dict:                                      # Phase 2: Transform the Html_Dict structure
        if not html_dict:
            return html_dict
        return self._consolidate_element(html_dict)

    def _consolidate_element(self, element: Dict) -> Dict:                                  # Recursively process element and consolidate text
        if not isinstance(element, dict):
            return element

        tag      = element.get('tag', '')
        children = element.get('children', [])

        if not children:
            return element

        if self._has_mixed_text_content(children):                                          # Check if this element has mixed text/inline content
            consolidated_text = self._extract_all_text(children)                            # Extract all text and merge
            element['children'] = [{'type': 'text', 'text': consolidated_text}]             # Replace children with single text node
        else:
            element['children'] = [self._consolidate_element(child)                         # Recurse into non-text children
                                   for child in children]

        return element

    def _has_mixed_text_content(self, children: List) -> bool:                              # Check if children contain mix of text and inline elements
        has_text   = False
        has_inline = False

        for child in children:
            if isinstance(child, dict):
                if child.get('type') == 'text':
                    has_text = True
                elif child.get('tag', '').lower() in INLINE_TAGS:
                    has_inline = True

        return has_text and has_inline                                                      # Only consolidate if we have both text and inline

    def _extract_all_text(self, children: List) -> str:                                     # Extract and concatenate all text from children tree
        text_parts = []

        for child in children:
            if isinstance(child, dict):
                if child.get('type') == 'text':
                    text_parts.append(child.get('text', ''))
                elif 'children' in child:
                    text_parts.append(self._extract_all_text(child['children']))            # Recurse into child elements
                elif 'text' in child:
                    text_parts.append(child.get('text', ''))

        return ''.join(text_parts)
