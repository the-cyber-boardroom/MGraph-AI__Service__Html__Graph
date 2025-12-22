# MGraph Engine Config - Tree
#
# Configuration options for Tree view export format.
# Controls indentation, node formatting, and output style.

from typing                                                                      import Literal
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Base   import MGraph__Engine__Config__Base

# todo: refactor to start with Schema__
class MGraph__Engine__Config__Tree(MGraph__Engine__Config__Base):                # Tree-specific configuration
    output_format  : Literal['text', 'json', 'nested_dict'] = 'text'             # Output format type
    indent_size    : int  = 2                                                    # Spaces per indent level
    indent_char    : str  = ' '                                                  # Character for indentation
    show_node_ids  : bool = False                                                # Include node IDs
    show_edge_types: bool = False                                                # Show edge predicate types
    max_label_len  : int  = 60                                                   # Maximum label length
    tree_chars     : bool = True                                                 # Use tree drawing characters
    prefix_leaf    : str  = '└── '                                               # Prefix for last child
    prefix_branch  : str  = '├── '                                               # Prefix for non-last child
    prefix_pipe    : str  = '│   '                                               # Vertical continuation
    prefix_space   : str  = '    '                                               # Space after last child
    include_stats  : bool = False                                                # Include statistics in JSON
    compact_json   : bool = False                                                # Compact JSON output