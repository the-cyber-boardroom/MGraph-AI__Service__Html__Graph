# Html Graph Export Schemas
#
# Request and response schema classes for the export service.
# Uses Type_Safe for type validation.

from typing                              import Optional, Dict, Any, List, Literal
from osbot_utils.type_safe.Type_Safe     import Type_Safe


# ═══════════════════════════════════════════════════════════════════════════════════════
# Request Schemas
# ═══════════════════════════════════════════════════════════════════════════════════════

# todo: rename this since the name is clashing with 'mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Html__Request.Schema__Graph__From_Html__Request'
class Schema__Graph__From_Html__Request(Type_Safe):                              # Request to convert HTML to graph
    html           : str  = ''                                                   # HTML content to parse
    transformation : str  = 'default'                                            # Transformation name to apply


class Schema__Graph__Export__Request(Type_Safe):                                 # Request for graph export
    html           : str  = ''                                                   # HTML content to parse
    transformation : str  = 'default'                                            # Transformation name
    engine         : str  = 'dot'                                                # Engine name (dot, d3, cytoscape, visjs, mermaid, tree)


# ═══════════════════════════════════════════════════════════════════════════════════════
# Response Schemas - Base
# ═══════════════════════════════════════════════════════════════════════════════════════

class Schema__Graph__Response__Base(Type_Safe):                                  # Base response fields
    duration       : float = 0.0                                                 # Export duration in seconds
    transformation : str   = 'default'                                           # Transformation applied
    engine         : str   = ''                                                  # Engine used
    node_count     : int   = 0                                                   # Number of nodes
    edge_count     : int   = 0                                                   # Number of edges


# ═══════════════════════════════════════════════════════════════════════════════════════
# Response Schemas - Engine-Specific
# ═══════════════════════════════════════════════════════════════════════════════════════

class Schema__Graph__Dot__Response(Schema__Graph__Response__Base):               # DOT format response
    dot            : str   = ''                                                  # DOT string content
    dot_size       : int   = 0                                                   # Size in bytes


class Schema__Graph__D3__Response(Schema__Graph__Response__Base):                # D3.js format response
    nodes          : List[Dict[str, Any]] = None                                 # D3 nodes array
    links          : List[Dict[str, Any]] = None                                 # D3 links array
    config         : Dict[str, Any]       = None                                 # D3 force config

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.nodes  is None: self.nodes  = []
        if self.links  is None: self.links  = []
        if self.config is None: self.config = {}


class Schema__Graph__Cytoscape__Response(Schema__Graph__Response__Base):         # Cytoscape.js format response
    elements       : Dict[str, List]      = None                                 # {nodes: [...], edges: [...]}
    layout         : Dict[str, Any]       = None                                 # Layout configuration
    style          : List[Dict[str, Any]] = None                                 # Style definitions

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.elements is None: self.elements = {'nodes': [], 'edges': []}
        if self.layout   is None: self.layout   = {}
        if self.style    is None: self.style    = []


class Schema__Graph__VisJs__Response(Schema__Graph__Response__Base):             # vis.js format response
    nodes          : List[Dict[str, Any]] = None                                 # VisJs nodes array
    edges          : List[Dict[str, Any]] = None                                 # VisJs edges array
    options        : Dict[str, Any]       = None                                 # VisJs options

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.nodes   is None: self.nodes   = []
        if self.edges   is None: self.edges   = []
        if self.options is None: self.options = {}


class Schema__Graph__Mermaid__Response(Schema__Graph__Response__Base):           # Mermaid format response
    mermaid        : str   = ''                                                  # Mermaid diagram string
    mermaid_size   : int   = 0                                                   # Size in bytes


class Schema__Graph__Tree__Response(Schema__Graph__Response__Base):              # Tree format response
    tree           : Any   = None                                                # Tree data (dict or str)
    output_format  : str   = 'text'                                              # 'text', 'json', or 'nested_dict'


# ═══════════════════════════════════════════════════════════════════════════════════════
# Transformation Info Schema
# ═══════════════════════════════════════════════════════════════════════════════════════

class Schema__Transformation__Info(Type_Safe):                                   # Transformation metadata
    name           : str = ''                                                    # Transformation name
    description    : str = ''                                                    # Description


class Schema__Transformations__List__Response(Type_Safe):                        # List of available transformations
    transformations: List[Schema__Transformation__Info]
    count          : int = 0


# ═══════════════════════════════════════════════════════════════════════════════════════
# Engine Info Schema
# ═══════════════════════════════════════════════════════════════════════════════════════

class Schema__Engine__Info(Type_Safe):                                           # Engine metadata
    name           : str = ''                                                    # Engine name
    output_type    : str = ''                                                    # 'string' or 'dict'
    description    : str = ''                                                    # Description


class Schema__Engines__List__Response(Type_Safe):                                # List of available engines
    engines        : List[Schema__Engine__Info] = None
    count          : int = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.engines is None:
            self.engines = []
