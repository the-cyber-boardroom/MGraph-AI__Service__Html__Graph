# MGraph Engine Config - D3 (Force-Directed)
#
# Configuration options for D3.js force-directed graph export.
# Controls physics simulation parameters and node sizing.

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Base  import MGraph__Engine__Config__Base


class MGraph__Engine__Config__D3(MGraph__Engine__Config__Base):                  # D3-specific configuration
    charge_strength  : float = -300.0                                            # Node repulsion force (negative = repel)
    link_distance    : int   = 100                                               # Default link length
    collision_radius : int   = 30                                                # Node collision detection radius
    center_strength  : float = 0.1                                               # Force toward center
    node_radius      : int   = 20                                                # Default node radius
    include_stats    : bool  = True                                              # Include graph statistics in output
    include_types    : bool  = True                                              # Include node type information
    max_label_len    : int   = 50                                                # Maximum label length
