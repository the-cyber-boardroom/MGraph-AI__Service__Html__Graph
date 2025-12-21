# ═══════════════════════════════════════════════════════════════════════════════
# Html_MGraph__Export__Base - Base class for all Html_MGraph exporters
#
# Provides common functionality:
# - Html_MGraph input (facade)
# - Config management
# - Extractor access
# - Common conversion utilities
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                               import Any, List, Dict, Optional
from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from osbot_utils.decorators.methods.cache_on_self                                         import cache_on_self
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                         import Html_MGraph
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config         import Html_MGraph__Render__Config
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Data__Extractor import Html_MGraph__Data__Extractor


class Html_MGraph__Export__Base(Type_Safe):                                               # Base class for Html_MGraph exporters
    html_mgraph : Html_MGraph                    = None                                   # The Html_MGraph facade to export from
    config      : Html_MGraph__Render__Config    = None                                   # Render configuration

    # ═══════════════════════════════════════════════════════════════════════════
    # Extractor Access
    # ═══════════════════════════════════════════════════════════════════════════

    @cache_on_self
    def extractor(self) -> Html_MGraph__Data__Extractor:                                  # Get or create the data extractor
        extractor = Html_MGraph__Data__Extractor(html_mgraph = self.html_mgraph ,
                                                  config      = self.config      )
        extractor.extract()
        return extractor

    @property
    def nodes(self) -> List:                                                              # Shortcut to extracted nodes
        return self.extractor().nodes

    @property
    def edges(self) -> List:                                                              # Shortcut to extracted edges
        return self.extractor().edges

    @property
    def root_id(self) -> Optional[str]:                                                   # Shortcut to root node ID
        return self.extractor().root_id

    # ═══════════════════════════════════════════════════════════════════════════
    # Export Method - Override in subclasses
    # ═══════════════════════════════════════════════════════════════════════════

    def export(self) -> Any:                                                              # Export to target format - override in subclasses
        raise NotImplementedError("Subclasses must implement export()")

    # ═══════════════════════════════════════════════════════════════════════════
    # Common Utility Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def lighten_color(self, hex_color: str, amount: int = 30) -> str:                     # Lighten a hex color
        if not hex_color or len(hex_color) != 7 or not hex_color.startswith('#'):
            return '#FFFFFF'
        try:
            r = min(255, int(hex_color[1:3], 16) + amount)
            g = min(255, int(hex_color[3:5], 16) + amount)
            b = min(255, int(hex_color[5:7], 16) + amount)
            return f'#{r:02x}{g:02x}{b:02x}'
        except ValueError:
            return '#FFFFFF'

    def darken_color(self, hex_color: str, amount: int = 30) -> str:                      # Darken a hex color
        if not hex_color or len(hex_color) != 7 or not hex_color.startswith('#'):
            return '#CCCCCC'
        try:
            r = max(0, int(hex_color[1:3], 16) - amount)
            g = max(0, int(hex_color[3:5], 16) - amount)
            b = max(0, int(hex_color[5:7], 16) - amount)
            return f'#{r:02x}{g:02x}{b:02x}'
        except ValueError:
            return '#CCCCCC'

    def escape_label(self, label: str, max_length: int = 30) -> str:                      # Escape and truncate label
        if not label:
            return ''
        label = label.replace('\\', '\\\\').replace('"', "'")
        label = label.replace('\n', ' ').replace('\r', '')
        return label[:max_length] + '...' if len(label) > max_length else label