# MGraph Engine Config - Cytoscape
#
# Configuration options for Cytoscape.js export format.
# Controls layout, node/edge styling, and interaction options.

from typing                                                                      import Literal
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Base   import MGraph__Engine__Config__Base


class MGraph__Engine__Config__Cytoscape(MGraph__Engine__Config__Base):           # Cytoscape-specific configuration
    layout_name      : str   = 'dagre'                                           # Layout algorithm: dagre, cose, breadthfirst
    layout_direction : Literal['TB', 'LR', 'BT', 'RL'] = 'TB'                    # Direction for hierarchical layouts
    node_width       : int   = 100                                               # Default node width
    node_height      : int   = 40                                                # Default node height
    node_shape       : str   = 'roundrectangle'                                  # Default node shape
    node_bg_color    : str   = '#e8f4f8'                                         # Default node background
    node_border_color: str   = '#666666'                                         # Default node border
    node_border_width: int   = 1                                                 # Default border width
    edge_color       : str   = '#666666'                                         # Default edge color
    edge_width       : int   = 2                                                 # Default edge width
    edge_arrow_shape : str   = 'triangle'                                        # Arrow shape
    font_size        : int   = 12                                                # Default font size
    max_label_len    : int   = 50                                                # Maximum label length
    include_stats    : bool  = True                                              # Include statistics
    include_style    : bool  = True                                              # Include style definitions
