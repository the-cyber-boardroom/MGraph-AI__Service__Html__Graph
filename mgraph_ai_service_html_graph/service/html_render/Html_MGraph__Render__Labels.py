from typing                          import Optional
from osbot_utils.type_safe.Type_Safe import Type_Safe


class Html_MGraph__Render__Labels(Type_Safe):                                               # Label generation utilities for HTML-aware MGraph visualization
    max_text_length : int  = 30                                                             # Maximum length for text content display
    show_tag_brackets: bool = True                                                          # Whether to show <tag> vs tag

    # ═══════════════════════════════════════════════════════════════════════════════
    # Public Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def label_for_node(self, node_path: str, value: Optional[str] = None) -> str:           # Generate appropriate label based on node_path
        if not node_path:
            return value or ''

        if node_path.startswith('tag:'):
            return self.label_for_tag_node(node_path, value)
        elif node_path.startswith('attr:'):
            return self.label_for_attr_node(node_path, value)
        elif node_path == 'text':
            return self.label_for_text_node(value)
        else:
            return self.label_for_element_node(node_path)

    def label_for_element_node(self, node_path: str) -> str:                                # Generate label for element node showing tag from path
        if not node_path:
            return ''

        last_segment = node_path.split('.')[-1]                                             # Get last segment of path (e.g., 'div.p[0]' -> 'p[0]')

        if '[' in last_segment:                                                             # Remove index if present (e.g., 'p[0]' -> 'p')
            tag = last_segment[:last_segment.index('[')]
        else:
            tag = last_segment

        if self.show_tag_brackets:
            return f'<{tag}>'
        return tag

    def label_for_tag_node(self, node_path: str, value: Optional[str] = None) -> str:       # Generate label for tag value node
        if value:
            tag_name = value
        elif node_path and node_path.startswith('tag:'):
            tag_name = node_path[4:]                                                        # Remove 'tag:' prefix
        else:
            tag_name = 'unknown'

        if self.show_tag_brackets:
            return f'<{tag_name}>'
        return tag_name

    def label_for_attr_node(self, node_path: str, value: Optional[str] = None) -> str:      # Generate label for attribute value node
        attr_name = ''
        if node_path and node_path.startswith('attr:'):
            attr_name = node_path[5:]                                                       # Remove 'attr:' prefix

        if value is not None:
            truncated_value = self._truncate(str(value), self.max_text_length)
            if attr_name:
                return f'{attr_name}="{truncated_value}"'
            return f'"{truncated_value}"'

        return attr_name or 'attr'

    def label_for_text_node(self, value: Optional[str] = None, max_length: Optional[int] = None) -> str:  # Generate label for text value node
        if value is None:
            return '[text]'

        max_len = max_length if max_length is not None else self.max_text_length
        return self._truncate(str(value), max_len)

    def get_path_depth(self, node_path: str) -> int:                                        # Calculate depth of a DOM path
        if not node_path:
            return 0
        if node_path.startswith(('tag:', 'attr:', 'text')):                                 # Value nodes don't have depth in DOM sense
            return 0
        return node_path.count('.') + 1

    def extract_tag_from_path(self, node_path: str) -> str:                                 # Extract the tag name from an element node path
        if not node_path:
            return ''

        if node_path.startswith(('tag:', 'attr:', 'text')):                                 # Not an element path
            return ''

        last_segment = node_path.split('.')[-1]

        if '[' in last_segment:
            return last_segment[:last_segment.index('[')]
        return last_segment

    # ═══════════════════════════════════════════════════════════════════════════════
    # Private Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def _truncate(self, text: str, max_length: int) -> str:                                 # Truncate text with ellipsis if too long
        if not text:
            return ''

        text = text.strip()                                                                 # Clean up whitespace
        text = ' '.join(text.split())                                                       # Normalize whitespace

        if len(text) <= max_length:
            return text

        return text[:max_length - 3] + '...'
