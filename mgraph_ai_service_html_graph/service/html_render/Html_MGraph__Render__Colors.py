from typing                                                                     import Dict
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from mgraph_ai_service_html_graph.schemas.enums.Enum__Html_Render__Color_Scheme import Enum__Html_Render__Color_Scheme


class Html_MGraph__Render__Colors(Type_Safe):                                               # Color definitions for HTML-aware MGraph visualization
    scheme : Enum__Html_Render__Color_Scheme = Enum__Html_Render__Color_Scheme.DEFAULT

    # ═══════════════════════════════════════════════════════════════════════════════
    # Element Node Colors (by DOM depth)
    # ═══════════════════════════════════════════════════════════════════════════════

    ELEMENT_COLORS_DEFAULT = ['#FFFFFF',                                                    # Depth 0 - root
                              '#F5F5F5',                                                    # Depth 1
                              '#EEEEEE',                                                    # Depth 2
                              '#E0E0E0',                                                    # Depth 3
                              '#D0D0D0',                                                    # Depth 4
                              '#C0C0C0',                                                    # Depth 5+
                              '#B0B0B0']

    ELEMENT_COLORS_MONOCHROME = ['#FFFFFF',
                                 '#F0F0F0',
                                 '#E0E0E0',
                                 '#D0D0D0',
                                 '#C0C0C0',
                                 '#B0B0B0',
                                 '#A0A0A0']

    ELEMENT_COLORS_HIGH_CONTRAST = ['#FFFFFF',
                                    '#E8E8E8',
                                    '#D0D0D0',
                                    '#B8B8B8',
                                    '#A0A0A0',
                                    '#888888',
                                    '#707070']

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tag Categories and Colors
    # ═══════════════════════════════════════════════════════════════════════════════

    TAG_CATEGORIES = { 'structural' : ['html', 'head', 'body', 'div', 'span', 'section',
                                       'article', 'aside', 'header', 'footer', 'main', 'nav'],
                       'text'       : ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a',
                                       'strong', 'em', 'b', 'i', 'u', 'small', 'mark',
                                       'del', 'ins', 'sub', 'sup', 'blockquote', 'pre', 'code'],
                       'list'       : ['ul', 'ol', 'li', 'dl', 'dt', 'dd'],
                       'table'      : ['table', 'tr', 'td', 'th', 'thead', 'tbody',
                                       'tfoot', 'caption', 'colgroup', 'col'],
                       'form'       : ['form', 'input', 'button', 'select', 'textarea',
                                       'label', 'fieldset', 'legend', 'option', 'optgroup'],
                       'media'      : ['img', 'video', 'audio', 'canvas', 'svg', 'picture',
                                       'source', 'track', 'iframe', 'embed', 'object'],
                       'meta'       : ['meta', 'link', 'title', 'style', 'script', 'base', 'noscript']}

    TAG_CATEGORY_COLORS_DEFAULT = { 'structural' : '#4A90D9',                               # Blue
                                    'text'       : '#5CB85C',                               # Green
                                    'list'       : '#5BC0DE',                               # Cyan
                                    'table'      : '#F0AD4E',                               # Orange
                                    'form'       : '#D9534F',                               # Red
                                    'media'      : '#9B59B6',                               # Purple
                                    'meta'       : '#607D8B',                               # Blue-gray
                                    'unknown'    : '#777777'}                               # Gray

    TAG_CATEGORY_COLORS_MONOCHROME = { 'structural' : '#505050',
                                       'text'       : '#606060',
                                       'list'       : '#707070',
                                       'table'      : '#808080',
                                       'form'       : '#909090',
                                       'media'      : '#A0A0A0',
                                       'meta'       : '#B0B0B0',
                                       'unknown'    : '#888888'}

    TAG_CATEGORY_COLORS_HIGH_CONTRAST = { 'structural' : '#1565C0',                         # Dark blue
                                          'text'       : '#2E7D32',                         # Dark green
                                          'list'       : '#00838F',                         # Dark cyan
                                          'table'      : '#E65100',                         # Dark orange
                                          'form'       : '#C62828',                         # Dark red
                                          'media'      : '#6A1B9A',                         # Dark purple
                                          'meta'       : '#37474F',                         # Dark blue-gray
                                          'unknown'    : '#424242'}                         # Dark gray

    # ═══════════════════════════════════════════════════════════════════════════════
    # Attribute and Text Node Colors
    # ═══════════════════════════════════════════════════════════════════════════════

    ATTR_COLORS = { 'default'       : '#B39DDB',                                            # Muted purple
                    'monochrome'    : '#C0C0C0',
                    'high_contrast' : '#7B1FA2'}

    TEXT_COLORS = { 'default'       : '#FFF9C4',                                            # Light yellow
                    'monochrome'    : '#F5F5F5',
                    'high_contrast' : '#FFEB3B'}

    # ═══════════════════════════════════════════════════════════════════════════════
    # Edge Colors by Predicate
    # ═══════════════════════════════════════════════════════════════════════════════

    EDGE_COLORS_DEFAULT = { 'child' : '#333333',                                            # Dark - structural
                            'tag'   : '#888888',                                            # Light gray - reference
                            'attr'  : '#B39DDB',                                            # Match attr nodes
                            'text'  : '#FFC107'}                                            # Amber

    EDGE_COLORS_MONOCHROME = { 'child' : '#404040',
                               'tag'   : '#808080',
                               'attr'  : '#A0A0A0',
                               'text'  : '#606060'}

    EDGE_COLORS_HIGH_CONTRAST = { 'child' : '#000000',
                                  'tag'   : '#555555',
                                  'attr'  : '#7B1FA2',
                                  'text'  : '#FF6F00'}

    # ═══════════════════════════════════════════════════════════════════════════════
    # Font Colors
    # ═══════════════════════════════════════════════════════════════════════════════

    FONT_COLORS = { 'default'       : { 'element' : '#333333',
                                        'tag'     : '#FFFFFF',
                                        'attr'    : '#333333',
                                        'text'    : '#333333'},
                    'monochrome'    : { 'element' : '#333333',
                                        'tag'     : '#FFFFFF',
                                        'attr'    : '#333333',
                                        'text'    : '#333333'},
                    'high_contrast' : { 'element' : '#000000',
                                        'tag'     : '#FFFFFF',
                                        'attr'    : '#000000',
                                        'text'    : '#000000'}}

    # ═══════════════════════════════════════════════════════════════════════════════
    # Public Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_element_color(self, depth: int) -> str:                                         # Get color for element node based on DOM depth
        colors = self._get_element_colors()
        index  = min(depth, len(colors) - 1)
        return colors[index]

    def get_tag_color(self, tag_name: str) -> str:                                          # Get color for tag value node based on tag category
        category = self._get_tag_category(tag_name.lower())
        colors   = self._get_tag_category_colors()
        return colors.get(category, colors['unknown'])

    def get_tag_category(self, tag_name: str) -> str:                                       # Get the category name for a tag
        return self._get_tag_category(tag_name.lower())

    def get_attr_color(self) -> str:                                                        # Get color for attribute value nodes
        return self.ATTR_COLORS.get(self.scheme.value, self.ATTR_COLORS['default'])

    def get_text_color(self) -> str:                                                        # Get color for text value nodes
        return self.TEXT_COLORS.get(self.scheme.value, self.TEXT_COLORS['default'])

    def get_edge_color(self, predicate: str) -> str:                                        # Get color for edge based on predicate
        colors = self._get_edge_colors()
        return colors.get(predicate, colors.get('child', '#333333'))

    def get_font_color(self, node_type: str) -> str:                                        # Get font color for node type (element, tag, attr, text)
        fonts = self.FONT_COLORS.get(self.scheme.value, self.FONT_COLORS['default'])
        return fonts.get(node_type, fonts['element'])

    # ═══════════════════════════════════════════════════════════════════════════════
    # Private Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def _get_element_colors(self) -> list:
        if self.scheme == Enum__Html_Render__Color_Scheme.MONOCHROME:
            return self.ELEMENT_COLORS_MONOCHROME
        elif self.scheme == Enum__Html_Render__Color_Scheme.HIGH_CONTRAST:
            return self.ELEMENT_COLORS_HIGH_CONTRAST
        return self.ELEMENT_COLORS_DEFAULT

    def _get_tag_category_colors(self) -> Dict[str, str]:
        if self.scheme == Enum__Html_Render__Color_Scheme.MONOCHROME:
            return self.TAG_CATEGORY_COLORS_MONOCHROME
        elif self.scheme == Enum__Html_Render__Color_Scheme.HIGH_CONTRAST:
            return self.TAG_CATEGORY_COLORS_HIGH_CONTRAST
        return self.TAG_CATEGORY_COLORS_DEFAULT

    def _get_edge_colors(self) -> Dict[str, str]:
        if self.scheme == Enum__Html_Render__Color_Scheme.MONOCHROME:
            return self.EDGE_COLORS_MONOCHROME
        elif self.scheme == Enum__Html_Render__Color_Scheme.HIGH_CONTRAST:
            return self.EDGE_COLORS_HIGH_CONTRAST
        return self.EDGE_COLORS_DEFAULT

    def _get_tag_category(self, tag_name: str) -> str:                                      # Determine which category a tag belongs to
        for category, tags in self.TAG_CATEGORIES.items():
            if tag_name in tags:
                return category
        return 'unknown'
