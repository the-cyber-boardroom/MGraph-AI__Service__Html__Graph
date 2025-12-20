# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Core Data Extractor (v2)
# Extracts semantic data from Html_MGraph using MGraph-DB APIs
#
# Uses MGraph-DB v1.4.7 features:
# - node_path / edge_path for DOM path identification
# - edge_label.predicate for semantic relationships
# - mgraph.data() for node/edge access
# - mgraph.index() for efficient lookups
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                       import Dict, List, Optional, Set
from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from mgraph_db.mgraph.MGraph                                                      import MGraph
from mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value                         import Schema__MGraph__Node__Value
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config import Html_MGraph__Render__Config
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors import Html_MGraph__Render__Colors
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Labels import Html_MGraph__Render__Labels


# ═══════════════════════════════════════════════════════════════════════════════
# Data Classes for Extracted Nodes and Edges
# ═══════════════════════════════════════════════════════════════════════════════

class Extracted__Node(Type_Safe):                                                 # Extracted node with all semantic data
    id           : str                                                            # Node ID
    label        : str              = ''                                          # Display label
    node_type    : str              = 'element'                                   # element, tag, attr, text
    dom_path     : str              = ''                                          # DOM path (e.g., "html.body.div")
    value        : Optional[str]    = None                                        # Value for value nodes
    depth        : int              = 0                                           # DOM depth level
    category     : str              = ''                                          # Tag category (structural, text, form, etc.)
    fill_color   : str              = '#E8E8E8'                                   # Node background color
    font_color   : str              = '#333333'                                   # Node text color
    border_color : str              = '#CCCCCC'                                   # Node border color
    shape        : str              = 'box'                                       # Node shape


class Extracted__Edge(Type_Safe):                                                 # Extracted edge with semantic data
    id           : str                                                            # Edge ID
    source       : str                                                            # Source node ID
    target       : str                                                            # Target node ID
    predicate    : str              = ''                                          # Relationship type: child, tag, attr, text
    position     : Optional[int]    = None                                        # Position among siblings
    color        : str              = '#888888'                                   # Edge color
    dashed       : bool             = False                                       # Whether edge is dashed


# ═══════════════════════════════════════════════════════════════════════════════
# Main Extractor Class
# ═══════════════════════════════════════════════════════════════════════════════

class Html_MGraph__Data__Extractor(Type_Safe):                                    # Extracts structured data from Html_MGraph
    mgraph          : MGraph                                                      # The MGraph to extract from
    config          : Html_MGraph__Render__Config = None                          # Render configuration
    colors          : Html_MGraph__Render__Colors = None                          # Color scheme
    labels          : Html_MGraph__Render__Labels = None                          # Label utilities

    # Results
    nodes           : List[Extracted__Node]       = None
    edges           : List[Extracted__Edge]       = None
    root_id         : Optional[str]               = None

    # Internal state
    _excluded_nodes : Set[str]                    = None                          # Node IDs to exclude from edges

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_defaults()

    def _init_defaults(self):                                                     # Initialize default values
        if self.colors is None:
            self.colors = Html_MGraph__Render__Colors()
        if self.labels is None:
            self.labels = Html_MGraph__Render__Labels()
        if self.config is None:
            self.config = Html_MGraph__Render__Config(colors=self.colors, labels=self.labels)
        if self.nodes is None:
            self.nodes = []
        if self.edges is None:
            self.edges = []
        if self._excluded_nodes is None:
            self._excluded_nodes = set()

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Extraction Method
    # ═══════════════════════════════════════════════════════════════════════════

    def extract(self) -> 'Html_MGraph__Data__Extractor':                          # Extract all data from the MGraph
        self.nodes = []
        self.edges = []
        self._excluded_nodes = set()

        self._extract_nodes()                                                     # Extract nodes first
        self._extract_edges()                                                     # Then extract edges
        self._find_root()                                                         # Find root node

        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # Node Extraction - Using MGraph-DB APIs
    # ═══════════════════════════════════════════════════════════════════════════

    def _extract_nodes(self):                                                     # Extract all nodes using MGraph data access
        mgraph_data = self.mgraph.data()

        for node_id in mgraph_data.nodes_ids():
            domain_node = mgraph_data.node(node_id)
            if not domain_node:
                continue

            extracted = self._extract_single_node(domain_node, node_id)

            if extracted:
                if self._should_include_node(extracted):
                    self.nodes.append(extracted)
                else:
                    self._excluded_nodes.add(str(node_id))                        # Track excluded nodes

    def _extract_single_node(self, domain_node, node_id) -> Optional[Extracted__Node]:
        """Extract data from a single MGraph node using proper accessors"""
        node_id_str = str(node_id)

        # Get node_path from the schema data
        node_path = self._get_node_path(domain_node)

        # Check if this is a value node (has value data)
        value = self._get_node_value(domain_node)

        # Determine node type from path pattern
        if node_path.startswith('tag:'):
            return self._create_tag_node(node_id_str, node_path, value)
        elif node_path.startswith('attr:'):
            return self._create_attr_node(node_id_str, node_path, value)
        elif node_path == 'text':
            return self._create_text_node(node_id_str, value)
        else:
            return self._create_element_node(node_id_str, node_path)

    def _get_node_path(self, domain_node) -> str:                                 # Extract node_path using MGraph-DB pattern
        try:
            # MGraph-DB: domain_node.node.data.node_path
            if hasattr(domain_node, 'node') and domain_node.node:
                node_data = domain_node.node.data
                if hasattr(node_data, 'node_path') and node_data.node_path:
                    return str(node_data.node_path)
        except Exception:
            pass
        return ''

    def _get_node_value(self, domain_node) -> Optional[str]:                      # Extract value from value nodes
        try:
            # Check if it's a value node (Schema__MGraph__Node__Value)
            if hasattr(domain_node, 'node') and domain_node.node:
                node_data = domain_node.node.data
                if hasattr(node_data, 'node_data'):
                    value_data = node_data.node_data
                    if hasattr(value_data, 'value'):
                        return str(value_data.value)
        except Exception:
            pass
        return None

    # ═══════════════════════════════════════════════════════════════════════════
    # Node Type Factories
    # ═══════════════════════════════════════════════════════════════════════════

    def _create_element_node(self, node_id: str, node_path: str) -> Extracted__Node:
        depth      = self._calculate_depth(node_path)
        tag        = self._extract_tag(node_path)
        category   = self.colors.get_tag_category(tag) if tag else ''
        fill_color = self.colors.get_element_color(depth)
        font_color = self.colors.get_font_color('element')
        label      = self.labels.label_for_element_node(node_path) if self.labels else node_path

        return Extracted__Node(id           = node_id                     ,
                               label        = label                       ,
                               node_type    = 'element'                   ,
                               dom_path     = node_path                   ,
                               depth        = depth                       ,
                               category     = category                    ,
                               fill_color   = fill_color                  ,
                               font_color   = font_color                  ,
                               border_color = self._darken(fill_color)    ,
                               shape        = self.config.element_shape   )

    def _create_tag_node(self, node_id: str, node_path: str, value: Optional[str]) -> Extracted__Node:
        tag_name   = node_path[4:] if node_path.startswith('tag:') else ''
        category   = self.colors.get_tag_category(tag_name)
        fill_color = self.colors.get_tag_color(tag_name)
        font_color = self.colors.get_font_color('tag')
        label      = self.labels.label_for_tag_node(node_path, value) if self.labels else f'<{tag_name}>'

        return Extracted__Node(id           = node_id                     ,
                               label        = label                       ,
                               node_type    = 'tag'                       ,
                               dom_path     = node_path                   ,
                               value        = value                       ,
                               category     = category                    ,
                               fill_color   = fill_color                  ,
                               font_color   = font_color                  ,
                               border_color = self._darken(fill_color)    ,
                               shape        = self.config.tag_shape       )

    def _create_attr_node(self, node_id: str, node_path: str, value: Optional[str]) -> Extracted__Node:
        fill_color = self.colors.get_attr_color()
        font_color = self.colors.get_font_color('attr')
        label      = self.labels.label_for_attr_node(node_path, value) if self.labels else node_path

        return Extracted__Node(id           = node_id                     ,
                               label        = label                       ,
                               node_type    = 'attr'                      ,
                               dom_path     = node_path                   ,
                               value        = value                       ,
                               fill_color   = fill_color                  ,
                               font_color   = font_color                  ,
                               border_color = self._darken(fill_color)    ,
                               shape        = self.config.attr_shape      )

    def _create_text_node(self, node_id: str, value: Optional[str]) -> Extracted__Node:
        fill_color = self.colors.get_text_color()
        font_color = self.colors.get_font_color('text')
        label      = self.labels.label_for_text_node(value) if self.labels else (value or '')

        return Extracted__Node(id           = node_id                     ,
                               label        = label                       ,
                               node_type    = 'text'                      ,
                               dom_path     = 'text'                      ,
                               value        = value                       ,
                               fill_color   = fill_color                  ,
                               font_color   = font_color                  ,
                               border_color = self._darken(fill_color)    ,
                               shape        = self.config.text_shape      )

    def _should_include_node(self, node: Extracted__Node) -> bool:                # Check visibility config
        if node.node_type == 'tag'  and not self.config.show_tag_nodes:
            return False
        if node.node_type == 'attr' and not self.config.show_attr_nodes:
            return False
        if node.node_type == 'text' and not self.config.show_text_nodes:
            return False
        return True

    # ═══════════════════════════════════════════════════════════════════════════
    # Edge Extraction - Using MGraph-DB APIs
    # ═══════════════════════════════════════════════════════════════════════════

    def _extract_edges(self):                                                     # Extract all edges using MGraph data access
        mgraph_data = self.mgraph.data()

        for edge_id in mgraph_data.edges_ids():
            domain_edge = mgraph_data.edge(edge_id)
            if not domain_edge:
                continue

            extracted = self._extract_single_edge(domain_edge, edge_id)

            if extracted and self._should_include_edge(extracted):
                self.edges.append(extracted)

    def _extract_single_edge(self, domain_edge, edge_id) -> Optional[Extracted__Edge]:
        """Extract data from a single MGraph edge using proper accessors"""
        try:
            edge_data = domain_edge.edge.data

            edge_id_str = str(edge_id)
            source      = str(edge_data.from_node_id)
            target      = str(edge_data.to_node_id)
            predicate   = self._get_edge_predicate(edge_data)
            position    = self._get_edge_position(edge_data)
            color       = self.colors.get_edge_color(predicate) if self.colors else '#888888'
            dashed      = predicate in ('tag', 'attr')                            # Non-structural edges are dashed

            return Extracted__Edge(id        = edge_id_str ,
                                   source    = source      ,
                                   target    = target      ,
                                   predicate = predicate   ,
                                   position  = position    ,
                                   color     = color       ,
                                   dashed    = dashed      )
        except Exception:
            return None

    def _get_edge_predicate(self, edge_data) -> str:                              # Extract predicate from edge_label
        """MGraph-DB stores semantic relationships in edge_label.predicate"""
        try:
            if hasattr(edge_data, 'edge_label') and edge_data.edge_label:
                label = edge_data.edge_label
                if hasattr(label, 'predicate') and label.predicate:
                    return str(label.predicate)
        except Exception:
            pass
        return ''

    def _get_edge_position(self, edge_data) -> Optional[int]:                     # Extract position from edge_path
        """Html_MGraph uses edge_path to store child position"""
        try:
            if hasattr(edge_data, 'edge_path') and edge_data.edge_path:
                return int(edge_data.edge_path)
        except (ValueError, TypeError):
            pass
        return None

    def _should_include_edge(self, edge: Extracted__Edge) -> bool:                # Check if edge should be included
        if edge.target in self._excluded_nodes:                                   # Skip edges to excluded nodes
            return False

        predicate = edge.predicate
        if predicate == 'child' and not self.config.show_child_edges:
            return False
        if predicate == 'tag' and not self.config.show_tag_edges:
            return False
        if predicate == 'attr' and not self.config.show_attr_edges:
            return False
        if predicate == 'text' and not self.config.show_text_edges:
            return False

        return True

    # ═══════════════════════════════════════════════════════════════════════════
    # Root Detection
    # ═══════════════════════════════════════════════════════════════════════════

    def _find_root(self):                                                         # Find the root element node
        for node in self.nodes:
            if node.node_type == 'element' and node.depth == 1:
                self.root_id = node.id
                break

    # ═══════════════════════════════════════════════════════════════════════════
    # Utility Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _calculate_depth(self, node_path: str) -> int:                            # Calculate DOM depth from path
        if not node_path:
            return 0
        return node_path.count('.') + 1

    def _extract_tag(self, node_path: str) -> str:                                # Extract tag name from path
        if not node_path:
            return ''
        # Path like "html.body.div[0]" -> "div"
        last_part = node_path.split('.')[-1] if '.' in node_path else node_path
        # Remove index like "[0]"
        if '[' in last_part:
            last_part = last_part[:last_part.index('[')]
        return last_part

    def _darken(self, hex_color: str) -> str:                                     # Darken a hex color for borders
        if not hex_color or not hex_color.startswith('#') or len(hex_color) != 7:
            return '#CCCCCC'
        try:
            r = max(0, int(hex_color[1:3], 16) - 30)
            g = max(0, int(hex_color[3:5], 16) - 30)
            b = max(0, int(hex_color[5:7], 16) - 30)
            return f'#{r:02x}{g:02x}{b:02x}'
        except ValueError:
            return '#CCCCCC'
