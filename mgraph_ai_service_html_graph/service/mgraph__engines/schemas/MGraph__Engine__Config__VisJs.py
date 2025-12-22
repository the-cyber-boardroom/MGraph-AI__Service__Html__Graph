# MGraph Engine Config - VisJs
#
# Configuration options for vis.js Network export format.
# Controls physics simulation, node/edge styling, and interaction.

from typing                                                                      import Literal
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Base   import MGraph__Engine__Config__Base


class MGraph__Engine__Config__VisJs(MGraph__Engine__Config__Base):               # VisJs-specific configuration
    layout_direction   : Literal['UD', 'DU', 'LR', 'RL'] = 'UD'                  # Hierarchical layout direction
    hierarchical       : bool  = True                                            # Use hierarchical layout
    physics_enabled    : bool  = False                                           # Enable physics simulation
    node_shape         : str   = 'box'                                           # Default node shape
    node_color_bg      : str   = '#e8f4f8'                                       # Node background color
    node_color_border  : str   = '#666666'                                       # Node border color
    node_color_highlight_bg    : str = '#d4edda'                                 # Highlight background
    node_color_highlight_border: str = '#28a745'                                 # Highlight border
    node_font_size     : int   = 14                                              # Node font size
    node_border_width  : int   = 1                                               # Node border width
    edge_color         : str   = '#666666'                                       # Edge color
    edge_width         : int   = 1                                               # Edge width
    edge_arrows        : str   = 'to'                                            # Arrow direction
    edge_smooth_type   : str   = 'cubicBezier'                                   # Edge smoothing
    level_separation   : int   = 150                                             # Vertical separation in hierarchy
    node_spacing       : int   = 100                                             # Horizontal node spacing
    max_label_len      : int   = 50                                              # Maximum label length
    include_stats      : bool  = True                                            # Include statistics
    include_options    : bool  = True                                            # Include vis.js options
