# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Core Data Extractor (v3)
# Updated for multi-graph architecture (Html_MGraph facade)
#
# Extracts semantic data from:
# - Body graph (elements + text)
# - Head graph (elements + text)
# - Attributes graph (tags + attributes)
# - Scripts graph (script content)
# - Styles graph (style content)
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                               import Dict, List, Optional, Set
from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                         import Html_MGraph
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config         import Html_MGraph__Render__Config
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors         import Html_MGraph__Render__Colors
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Labels         import Html_MGraph__Render__Labels


# ═══════════════════════════════════════════════════════════════════════════════
# Data Classes for Extracted Nodes and Edges
# ═══════════════════════════════════════════════════════════════════════════════

class Extracted__Node(Type_Safe):                                                         # Extracted node with all semantic data
    id           : str                                                                    # Node ID
    label        : str              = ''                                                  # Display label
    node_type    : str              = 'element'                                           # element, tag, attr, text, script, style
    dom_path     : str              = ''                                                  # DOM path (e.g., "html.body.div")
    value        : Optional[str]    = None                                                # Value for value nodes
    depth        : int              = 0                                                   # DOM depth level
    category     : str              = ''                                                  # Tag category (structural, text, form, etc.)
    graph_source : str              = ''                                                  # Which graph: body, head, attrs, scripts, styles
    fill_color   : str              = '#E8E8E8'                                           # Node background color
    font_color   : str              = '#333333'                                           # Node text color
    border_color : str              = '#CCCCCC'                                           # Node border color
    shape        : str              = 'box'                                               # Node shape


class Extracted__Edge(Type_Safe):                                                         # Extracted edge with semantic data
    id           : str                                                                    # Edge ID
    source       : str                                                                    # Source node ID
    target       : str                                                                    # Target node ID
    predicate    : str              = ''                                                  # Relationship type: child, tag, attr, text
    position     : Optional[int]    = None                                                # Position among siblings
    graph_source : str              = ''                                                  # Which graph this edge came from
    color        : str              = '#888888'                                           # Edge color
    dashed       : bool             = False                                               # Whether edge is dashed


# ═══════════════════════════════════════════════════════════════════════════════
# Main Extractor Class - Updated for Multi-Graph Architecture
# ═══════════════════════════════════════════════════════════════════════════════

class Html_MGraph__Data__Extractor(Type_Safe):                                            # Extracts structured data from Html_MGraph
    html_mgraph     : Html_MGraph                    = None                               # The Html_MGraph facade
    config          : Html_MGraph__Render__Config   = None                               # Render configuration
    colors          : Html_MGraph__Render__Colors   = None                               # Color scheme
    labels          : Html_MGraph__Render__Labels   = None                               # Label utilities

    # Results
    nodes           : List[Extracted__Node]         = None
    edges           : List[Extracted__Edge]         = None
    root_id         : Optional[str]                 = None

    # Internal state
    _extracted_ids  : Set[str]                      = None                               # Track extracted node IDs
    _excluded_nodes : Set[str]                      = None                               # Node IDs to exclude from edges

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_defaults()

    def _init_defaults(self):                                                             # Initialize default values
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
        if self._extracted_ids is None:
            self._extracted_ids = set()
        if self._excluded_nodes is None:
            self._excluded_nodes = set()

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Extraction Method
    # ═══════════════════════════════════════════════════════════════════════════

    def extract(self) -> 'Html_MGraph__Data__Extractor':                                  # Extract all data from the Html_MGraph
        self.nodes           = []
        self.edges           = []
        self._extracted_ids  = set()
        self._excluded_nodes = set()

        if self.html_mgraph is None:
            return self

        self._extract_from_body_graph()                                                   # Extract body structure
        self._extract_from_head_graph()                                                   # Extract head structure
        self._extract_from_attrs_graph()                                                  # Extract tags and attributes
        self._extract_from_scripts_graph()                                                # Extract script content
        self._extract_from_styles_graph()                                                 # Extract style content
        self._find_root()                                                                 # Find root node

        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # Body Graph Extraction
    # ═══════════════════════════════════════════════════════════════════════════

    def _extract_from_body_graph(self):                                                   # Extract elements and text from body graph
        body_graph = self.html_mgraph.body_graph
        if not body_graph or not body_graph.mgraph:
            return

        for node_id in body_graph.nodes_ids():
            if str(node_id) in self._extracted_ids:
                continue

            node_path = body_graph.node_path(node_id)
            path_str  = str(node_path) if node_path else ''

            if path_str == 'text' or path_str.startswith('text:'):                        # Text node
                value = body_graph.node_value(node_id)
                extracted = self._create_text_node(str(node_id), value, 'body')
            else:                                                                         # Element node
                tag = self.html_mgraph.get_tag(node_id) or self._extract_tag(path_str)
                extracted = self._create_element_node(str(node_id), path_str, tag, 'body')

            if extracted and self._should_include_node(extracted):
                self.nodes.append(extracted)
                self._extracted_ids.add(str(node_id))
            elif extracted:
                self._excluded_nodes.add(str(node_id))

        self._extract_edges_from_graph(body_graph, 'body')                                # Extract body edges

    # ═══════════════════════════════════════════════════════════════════════════
    # Head Graph Extraction
    # ═══════════════════════════════════════════════════════════════════════════

    def _extract_from_head_graph(self):                                                   # Extract elements and text from head graph
        head_graph = self.html_mgraph.head_graph
        if not head_graph or not head_graph.mgraph:
            return

        for node_id in head_graph.nodes_ids():
            if str(node_id) in self._extracted_ids:
                continue

            node_path = head_graph.node_path(node_id)
            path_str  = str(node_path) if node_path else ''

            if path_str == 'text' or path_str.startswith('text:'):                        # Text node
                value = head_graph.node_value(node_id)
                extracted = self._create_text_node(str(node_id), value, 'head')
            else:                                                                         # Element node
                tag = self.html_mgraph.get_tag(node_id) or self._extract_tag(path_str)
                extracted = self._create_element_node(str(node_id), path_str, tag, 'head')

            if extracted and self._should_include_node(extracted):
                self.nodes.append(extracted)
                self._extracted_ids.add(str(node_id))
            elif extracted:
                self._excluded_nodes.add(str(node_id))

        self._extract_edges_from_graph(head_graph, 'head')                                # Extract head edges

    # ═══════════════════════════════════════════════════════════════════════════
    # Attributes Graph Extraction
    # ═══════════════════════════════════════════════════════════════════════════

    def _extract_from_attrs_graph(self):                                                  # Extract tags and attributes from attrs graph
        attrs_graph = self.html_mgraph.attrs_graph
        if not attrs_graph or not attrs_graph.mgraph:
            return

        for node_id in attrs_graph.nodes_ids():
            if str(node_id) in self._extracted_ids:
                continue

            node_path = attrs_graph.node_path(node_id)
            path_str  = str(node_path) if node_path else ''
            value     = attrs_graph.node_value(node_id)

            if path_str.startswith('tag:'):                                               # Tag node
                extracted = self._create_tag_node(str(node_id), path_str, value, 'attrs')
            elif path_str.startswith('attr:'):                                            # Attribute node
                extracted = self._create_attr_node(str(node_id), path_str, value, 'attrs')
            else:
                continue                                                                  # Skip anchor nodes (already in body/head)

            if extracted and self._should_include_node(extracted):
                self.nodes.append(extracted)
                self._extracted_ids.add(str(node_id))
            elif extracted:
                self._excluded_nodes.add(str(node_id))

        self._extract_edges_from_graph(attrs_graph, 'attrs')                              # Extract attr edges

    # ═══════════════════════════════════════════════════════════════════════════
    # Scripts Graph Extraction
    # ═══════════════════════════════════════════════════════════════════════════

    def _extract_from_scripts_graph(self):                                                # Extract script content from scripts graph
        scripts_graph = self.html_mgraph.scripts_graph
        if not scripts_graph or not scripts_graph.mgraph:
            return

        for node_id in scripts_graph.nodes_ids():
            if str(node_id) in self._extracted_ids:
                continue

            node_path = scripts_graph.node_path(node_id)
            path_str  = str(node_path) if node_path else ''
            value     = scripts_graph.node_value(node_id)

            if path_str.startswith('content:'):                                           # Script content node
                extracted = self._create_script_node(str(node_id), value, 'scripts')
                if extracted and self._should_include_node(extracted):
                    self.nodes.append(extracted)
                    self._extracted_ids.add(str(node_id))

        self._extract_edges_from_graph(scripts_graph, 'scripts')

    # ═══════════════════════════════════════════════════════════════════════════
    # Styles Graph Extraction
    # ═══════════════════════════════════════════════════════════════════════════

    def _extract_from_styles_graph(self):                                                 # Extract style content from styles graph
        styles_graph = self.html_mgraph.styles_graph
        if not styles_graph or not styles_graph.mgraph:
            return

        for node_id in styles_graph.nodes_ids():
            if str(node_id) in self._extracted_ids:
                continue

            node_path = styles_graph.node_path(node_id)
            path_str  = str(node_path) if node_path else ''
            value     = styles_graph.node_value(node_id)

            if path_str.startswith('content:'):                                           # Style content node
                extracted = self._create_style_node(str(node_id), value, 'styles')
                if extracted and self._should_include_node(extracted):
                    self.nodes.append(extracted)
                    self._extracted_ids.add(str(node_id))

        self._extract_edges_from_graph(styles_graph, 'styles')

    # ═══════════════════════════════════════════════════════════════════════════
    # Edge Extraction
    # ═══════════════════════════════════════════════════════════════════════════

    def _extract_edges_from_graph(self, graph, graph_source: str):                        # Extract edges from a specific graph
        if not graph or not graph.mgraph:
            return

        mgraph_data = graph.mgraph.data()
        for edge_id in mgraph_data.edges_ids():
            domain_edge = mgraph_data.edge(edge_id)
            if not domain_edge:
                continue

            extracted = self._extract_single_edge(domain_edge, edge_id, graph_source)
            if extracted and self._should_include_edge(extracted):
                self.edges.append(extracted)

    def _extract_single_edge(self, domain_edge, edge_id, graph_source: str) -> Optional[Extracted__Edge]:
        try:
            edge_data = domain_edge.edge.data

            edge_id_str = str(edge_id)
            source      = str(edge_data.from_node_id)
            target      = str(edge_data.to_node_id)
            predicate   = self._get_edge_predicate(edge_data)
            position    = self._get_edge_position(edge_data)
            color       = self.colors.get_edge_color(predicate) if self.colors else '#888888'
            dashed      = predicate in ('tag', 'attr', 'script', 'style')                 # Non-structural edges are dashed

            return Extracted__Edge(id           = edge_id_str   ,
                                   source       = source        ,
                                   target       = target        ,
                                   predicate    = predicate     ,
                                   position     = position      ,
                                   graph_source = graph_source  ,
                                   color        = color         ,
                                   dashed       = dashed        )
        except Exception:
            return None

    def _get_edge_predicate(self, edge_data) -> str:                                      # Extract predicate from edge_label
        try:
            if hasattr(edge_data, 'edge_label') and edge_data.edge_label:
                label = edge_data.edge_label
                if hasattr(label, 'predicate') and label.predicate:
                    return str(label.predicate)
        except Exception:
            pass
        return ''

    def _get_edge_position(self, edge_data) -> Optional[int]:                             # Extract position from edge_path
        try:
            if hasattr(edge_data, 'edge_path') and edge_data.edge_path:
                return int(edge_data.edge_path)
        except (ValueError, TypeError):
            pass
        return None

    def _should_include_edge(self, edge: Extracted__Edge) -> bool:                        # Check if edge should be included
        if edge.source in self._excluded_nodes or edge.target in self._excluded_nodes:
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
    # Node Creation Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _create_element_node(self, node_id: str, node_path: str, tag: str, graph_source: str) -> Extracted__Node:
        depth      = self._calculate_depth(node_path)
        category   = self.colors.get_tag_category(tag) if self.colors and tag else ''
        fill_color = self.colors.get_element_color(depth) if self.colors else '#E8E8E8'
        font_color = self.colors.get_font_color('element') if self.colors else '#333333'
        label      = self.labels.label_for_element_node(node_path) if self.labels else (tag or node_path)

        return Extracted__Node(id           = node_id                     ,
                               label        = label                       ,
                               node_type    = 'element'                   ,
                               dom_path     = node_path                   ,
                               depth        = depth                       ,
                               category     = category                    ,
                               graph_source = graph_source                ,
                               fill_color   = fill_color                  ,
                               font_color   = font_color                  ,
                               border_color = self._darken(fill_color)    ,
                               shape        = self.config.element_shape if self.config else 'box')

    def _create_tag_node(self, node_id: str, node_path: str, value: Optional[str], graph_source: str) -> Extracted__Node:
        tag_name   = node_path[4:] if node_path.startswith('tag:') else ''
        category   = self.colors.get_tag_category(tag_name) if self.colors else ''
        fill_color = self.colors.get_tag_color(tag_name) if self.colors else '#4A90D9'
        font_color = self.colors.get_font_color('tag') if self.colors else '#FFFFFF'
        label      = self.labels.label_for_tag_node(node_path, value) if self.labels else f'<{tag_name}>'

        return Extracted__Node(id           = node_id                     ,
                               label        = label                       ,
                               node_type    = 'tag'                       ,
                               dom_path     = node_path                   ,
                               value        = value                       ,
                               category     = category                    ,
                               graph_source = graph_source                ,
                               fill_color   = fill_color                  ,
                               font_color   = font_color                  ,
                               border_color = self._darken(fill_color)    ,
                               shape        = self.config.tag_shape if self.config else 'ellipse')

    def _create_attr_node(self, node_id: str, node_path: str, value: Optional[str], graph_source: str) -> Extracted__Node:
        fill_color = self.colors.get_attr_color() if self.colors else '#B39DDB'
        font_color = self.colors.get_font_color('attr') if self.colors else '#333333'
        label      = self.labels.label_for_attr_node(node_path, value) if self.labels else (value or node_path)

        return Extracted__Node(id           = node_id                     ,
                               label        = label                       ,
                               node_type    = 'attr'                      ,
                               dom_path     = node_path                   ,
                               value        = value                       ,
                               graph_source = graph_source                ,
                               fill_color   = fill_color                  ,
                               font_color   = font_color                  ,
                               border_color = self._darken(fill_color)    ,
                               shape        = self.config.attr_shape if self.config else 'box')

    def _create_text_node(self, node_id: str, value: Optional[str], graph_source: str) -> Extracted__Node:
        fill_color = self.colors.get_text_color() if self.colors else '#FFFACD'
        font_color = self.colors.get_font_color('text') if self.colors else '#333333'
        label      = self.labels.label_for_text_node(value) if self.labels else (value or '')

        return Extracted__Node(id           = node_id                     ,
                               label        = label                       ,
                               node_type    = 'text'                      ,
                               dom_path     = 'text'                      ,
                               value        = value                       ,
                               graph_source = graph_source                ,
                               fill_color   = fill_color                  ,
                               font_color   = font_color                  ,
                               border_color = self._darken(fill_color)    ,
                               shape        = self.config.text_shape if self.config else 'box')

    def _create_script_node(self, node_id: str, value: Optional[str], graph_source: str) -> Extracted__Node:
        fill_color = '#FCE4EC'                                                            # Light pink for scripts
        font_color = '#333333'
        label      = (value or '')[:30] + '...' if value and len(value) > 30 else (value or '')

        return Extracted__Node(id           = node_id                     ,
                               label        = f'script: {label}'          ,
                               node_type    = 'script'                    ,
                               dom_path     = 'script'                    ,
                               value        = value                       ,
                               graph_source = graph_source                ,
                               fill_color   = fill_color                  ,
                               font_color   = font_color                  ,
                               border_color = self._darken(fill_color)    ,
                               shape        = 'box'                       )

    def _create_style_node(self, node_id: str, value: Optional[str], graph_source: str) -> Extracted__Node:
        fill_color = '#F3E5F5'                                                            # Light purple for styles
        font_color = '#333333'
        label      = (value or '')[:30] + '...' if value and len(value) > 30 else (value or '')

        return Extracted__Node(id           = node_id                     ,
                               label        = f'style: {label}'           ,
                               node_type    = 'style'                     ,
                               dom_path     = 'style'                     ,
                               value        = value                       ,
                               graph_source = graph_source                ,
                               fill_color   = fill_color                  ,
                               font_color   = font_color                  ,
                               border_color = self._darken(fill_color)    ,
                               shape        = 'box'                       )

    def _should_include_node(self, node: Extracted__Node) -> bool:                        # Check visibility config
        if not self.config:
            return True
        if node.node_type == 'tag'  and not self.config.show_tag_nodes:
            return False
        if node.node_type == 'attr' and not self.config.show_attr_nodes:
            return False
        if node.node_type == 'text' and not self.config.show_text_nodes:
            return False
        return True

    # ═══════════════════════════════════════════════════════════════════════════
    # Root Detection
    # ═══════════════════════════════════════════════════════════════════════════

    def _find_root(self):                                                                 # Find the root element node
        if self.html_mgraph:
            root = self.html_mgraph.root_id()
            if root:
                self.root_id = str(root)
                return

        for node in self.nodes:                                                           # Fallback: find by depth
            if node.node_type == 'element' and node.depth == 1:
                self.root_id = node.id
                break

    # ═══════════════════════════════════════════════════════════════════════════
    # Utility Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _calculate_depth(self, node_path: str) -> int:                                    # Calculate DOM depth from path
        if not node_path:
            return 0
        return node_path.count('.') + 1

    def _extract_tag(self, node_path: str) -> str:                                        # Extract tag name from path
        if not node_path:
            return ''
        last_part = node_path.split('.')[-1] if '.' in node_path else node_path
        if '[' in last_part:
            last_part = last_part[:last_part.index('[')]
        return last_part

    def _get_tag_category(self, tag: str) -> str:                                         # Get tag category
        categories = {
            'structural' : ['html', 'head', 'body', 'div', 'span', 'section', 'article', 'header', 'footer', 'nav', 'aside', 'main'],
            'text'       : ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'strong', 'em', 'b', 'i', 'u', 'br', 'hr'],
            'form'       : ['form', 'input', 'button', 'select', 'textarea', 'label', 'option'],
            'media'      : ['img', 'video', 'audio', 'canvas', 'svg', 'picture'],
            'list'       : ['ul', 'ol', 'li', 'dl', 'dt', 'dd'],
            'table'      : ['table', 'tr', 'td', 'th', 'thead', 'tbody', 'tfoot'],
            'meta'       : ['meta', 'link', 'title', 'style', 'script']
        }
        for category, tags in categories.items():
            if tag.lower() in tags:
                return category
        return 'other'

    def _darken(self, hex_color: str) -> str:                                             # Darken a hex color for borders
        if not hex_color or not hex_color.startswith('#') or len(hex_color) != 7:
            return '#CCCCCC'
        try:
            r = max(0, int(hex_color[1:3], 16) - 30)
            g = max(0, int(hex_color[3:5], 16) - 30)
            b = max(0, int(hex_color[5:7], 16) - 30)
            return f'#{r:02x}{g:02x}{b:02x}'
        except ValueError:
            return '#CCCCCC'