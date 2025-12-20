from typing                                                                                 import Dict, List, Any
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base

INLINE_TAGS = {'a', 'abbr', 'acronym', 'b', 'bdo', 'big', 'br', 'button', 'cite', 'code',
               'dfn', 'em', 'i', 'img', 'input', 'kbd', 'label', 'map', 'object', 'q',
               'samp', 'script', 'select', 'small', 'span', 'strong', 'sub', 'sup',
               'textarea', 'time', 'tt', 'u', 'var', 'mark'}

class Graph_Transformation__Add_Consolidated_Text_Node(Graph_Transformation__Base):
    """Non-destructive consolidation: create NEW sibling node with consolidated text.
    """

    name        : str = 'add_consolidated_text_node'
    description : str = 'Add consolidated text nodes as siblings (non-destructive)'
    label       : str = 'Add Consolidated Node'

    def transform_dict(self, html_dict: Dict) -> Dict:                                      # Phase 2: Transform the Html_Dict structure
        if not html_dict:
            return html_dict
        return self._process_element(html_dict, parent=None)

    def _process_element(self, element : Dict         ,                                     # Process element and add consolidated nodes where needed
                               parent  : Dict = None  ) -> Dict:
        if not isinstance(element, dict):
            return element

        children = element.get('children', [])

        if not children:
            return element

        new_children       = []
        consolidated_nodes = []

        for child in children:
            if isinstance(child, dict) and child.get('tag'):
                processed_child = self._process_element(child, parent=element)              # Recurse first
                new_children.append(processed_child)

                if self._has_mixed_text_content(processed_child.get('children', [])):       # Check if this child needs a consolidated sibling
                    consolidated_text = self._extract_all_text(processed_child.get('children', []))
                    if consolidated_text.strip():                                           # Only add if there's actual text
                        consolidated_node = { 'tag'              : 'consolidated_text'    ,
                                              'type'             : 'synthetic'            ,
                                              'source_tag'       : processed_child.get('tag', ''),
                                              'text'             : consolidated_text      ,
                                              'children'         : []                     }
                        consolidated_nodes.append(consolidated_node)
            else:
                new_children.append(child)                                                  # Keep text nodes and other content as-is

        element['children'] = new_children + consolidated_nodes                             # Add consolidated nodes as siblings at same level
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

        return has_text and has_inline

    def _extract_all_text(self, children: List) -> str:                                     # Extract and concatenate all text from children tree
        text_parts = []

        for child in children:
            if isinstance(child, dict):
                if child.get('type') == 'text':
                    text_parts.append(child.get('text', ''))
                elif 'children' in child:
                    text_parts.append(self._extract_all_text(child['children']))
                elif 'text' in child:
                    text_parts.append(child.get('text', ''))

        return ''.join(text_parts)
