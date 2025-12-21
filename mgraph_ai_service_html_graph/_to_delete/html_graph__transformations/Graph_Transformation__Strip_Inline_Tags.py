from typing                                                                                 import Dict, List, Any
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base

INLINE_TAGS = {'a', 'abbr', 'acronym', 'b', 'bdo', 'big', 'cite', 'code',
               'dfn', 'em', 'i', 'kbd', 'label', 'mark', 'q',
               'samp', 'small', 'span', 'strong', 'sub', 'sup',
               'time', 'tt', 'u', 'var'}                                                    # Note: excludes br, img, input, button, etc.

class Graph_Transformation__Strip_Inline_Tags(Graph_Transformation__Base):
    """Remove inline formatting/link tags but preserve their text content.

    Use case: <p>Click <a href="#">here</a> to continue</p>
              Becomes: <p>Click here to continue</p> (single text run)

    Target tags: a, b, i, em, strong, span, code, mark, small, sub, sup, etc.
    This flattens inline markup while preserving the text flow.
    """

    name        : str = 'strip_inline_tags'
    description : str = 'Remove inline formatting tags, preserve text content'
    label       : str = 'Strip Inline Tags'

    def transform_dict(self, html_dict: Dict) -> Dict:                                      # Phase 2: Transform the Html_Dict structure
        if not html_dict:
            return html_dict
        return self._strip_element(html_dict)

    def _strip_element(self, element: Dict) -> Dict:                                        # Recursively strip inline tags from element
        if not isinstance(element, dict):
            return element

        children = element.get('children', [])

        if not children:
            return element

        new_children = self._flatten_children(children)                                     # Flatten and merge text nodes
        new_children = self._merge_adjacent_text(new_children)

        element['children'] = new_children
        return element

    def _flatten_children(self, children: List) -> List:                                    # Flatten inline elements, keeping their text
        result = []

        for child in children:
            if not isinstance(child, dict):
                result.append(child)
                continue

            tag = child.get('tag', '').lower()

            if child.get('type') == 'text':                                                 # Text node: keep as-is
                result.append(child)

            elif tag in INLINE_TAGS:                                                        # Inline tag: extract children (unwrap the tag)
                child_children = child.get('children', [])
                if child_children:
                    flattened = self._flatten_children(child_children)                      # Recurse into inline's children
                    result.extend(flattened)
                elif child.get('text'):                                                     # Handle inline element with direct text attribute
                    result.append({'type': 'text', 'text': child.get('text', '')})

            else:                                                                           # Non-inline tag: recurse normally
                processed = self._strip_element(child)
                result.append(processed)

        return result

    def _merge_adjacent_text(self, children: List) -> List:                                 # Merge consecutive text nodes into single nodes
        if not children:
            return children

        result     = []
        text_buffer = []

        for child in children:
            if isinstance(child, dict) and child.get('type') == 'text':
                text_buffer.append(child.get('text', ''))                                   # Accumulate text
            else:
                if text_buffer:                                                             # Flush accumulated text
                    result.append({'type': 'text', 'text': ''.join(text_buffer)})
                    text_buffer = []
                result.append(child)

        if text_buffer:                                                                     # Flush any remaining text
            result.append({'type': 'text', 'text': ''.join(text_buffer)})

        return result
