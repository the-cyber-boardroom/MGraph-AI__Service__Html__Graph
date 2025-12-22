# MGraph Engine Config - DOT (Graphviz)
#
# Configuration options for DOT/Graphviz export format.
# Controls layout direction, spacing, colors, and node styling.

from typing                                                              import Literal
from osbot_utils.type_safe.Type_Safe                                     import Type_Safe
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Base import MGraph__Engine__Config__Base


class MGraph__Engine__Config__Dot(MGraph__Engine__Config__Base):         # DOT-specific configuration
    rankdir        : Literal['TB', 'LR', 'BT', 'RL'] = 'TB'              # Graph direction: TB=top-bottom, LR=left-right
    splines        : Literal['true', 'false', 'ortho', 'polyline', 'curved'] = 'true'  # Edge routing style
    node_sep       : float                           = 0.5               # Minimum space between nodes (inches)
    rank_sep       : float                           = 0.5               # Minimum space between ranks (inches)
    nodesep        : float                           = 0.25              # Node separation within rank
    font_name      : str                             = 'Arial'           # Default font family
    font_size      : int                             = 10                # Default font size (points)
    node_shape     : str                             = 'box'             # Default node shape
    node_style     : str                             = 'rounded,filled'  # Default node style
    node_fillcolor : str                             = '#e8f4f8'         # Default node fill color
    node_fontcolor : str                             = '#333333'         # Default node font color
    edge_color     : str                             = '#666666'         # Default edge color
    edge_arrowsize : float                           = 0.7               # Arrow head size
    bgcolor        : str                             = 'transparent'     # Background color
    max_label_len  : int                             = 50                # Maximum label length before truncation
    show_node_ids  : bool                            = False             # Include node IDs in labels
    concentrate    : bool                            = False             # Merge parallel edges
