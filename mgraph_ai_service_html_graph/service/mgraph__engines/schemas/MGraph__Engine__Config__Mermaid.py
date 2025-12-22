# MGraph Engine Config - Mermaid
#
# Configuration options for Mermaid diagram export format.
# Controls diagram direction, node styling, and link types.

from typing                                                                      import Literal
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Base   import MGraph__Engine__Config__Base


class MGraph__Engine__Config__Mermaid(MGraph__Engine__Config__Base):             # Mermaid-specific configuration
    diagram_type   : Literal['flowchart', 'graph'] = 'flowchart'                 # Diagram type
    direction      : Literal['TB', 'TD', 'BT', 'LR', 'RL'] = 'TD'               # Flow direction
    node_shape     : Literal['rect', 'round', 'stadium', 'diamond', 'circle'] = 'round'  # Default node shape
    link_style     : Literal['arrow', 'open', 'dotted'] = 'arrow'               # Default link style
    max_label_len  : int  = 40                                                   # Maximum label length
    escape_special : bool = True                                                 # Escape special characters
    use_subgraphs  : bool = False                                                # Group nodes into subgraphs
