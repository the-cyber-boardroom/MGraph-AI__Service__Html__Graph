from typing                                                                                         import Any, Dict, List, Set
from mgraph_db.mgraph.MGraph                                                                        import MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base    import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                   import Html_MGraph
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Dot       import MGraph__Engine__Config__Dot
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__D3        import MGraph__Engine__Config__D3
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Cytoscape import MGraph__Engine__Config__Cytoscape
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__VisJs     import MGraph__Engine__Config__VisJs
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Mermaid   import MGraph__Engine__Config__Mermaid
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Tree      import MGraph__Engine__Config__Tree


class Html_Use_Case__2(Graph_Transformation__Base):
    """Semantic DOM Visualization with depth-based coloring.

    This transformation creates a clean, semantically-styled visualization:

    Features:
    - Element nodes colored by DOM depth (darker = deeper)
    - Text nodes in distinct yellow/amber color
    - Clean labels showing tag names for elements, truncated content for text
    - Structural edges (child) vs content edges (text) visually differentiated
    - Hidden node IDs for cleaner appearance

    Visual Guide:
    - Blue tones: Element nodes (depth determines shade)
    - Yellow: Text content nodes
    - Gray arrows: Parent-child relationships
    - Orange arrows: Element-to-text relationships
    """

    name        : str = "html-use-case-2"
    label       : str = "Html Use Case #2"
    description : str = "Semantic DOM visualization with depth-based coloring"

    # Store mgraph reference for Phase 5 custom DOT generation
    _mgraph     : MGraph = None

    # ═══════════════════════════════════════════════════════════════════════════
    # Color Configuration
    # ═══════════════════════════════════════════════════════════════════════════

    # Element colors by depth (index = depth, wraps at end)
    DEPTH_COLORS = [
        '#E3F2FD',  # Depth 0 - very light blue (html/body)
        '#BBDEFB',  # Depth 1 - light blue
        '#90CAF9',  # Depth 2 - medium light blue
        '#64B5F6',  # Depth 3 - medium blue
        '#42A5F5',  # Depth 4 - blue
        '#2196F3',  # Depth 5+ - darker blue
    ]

    TEXT_NODE_COLOR       = '#FFF9C4'     # Light yellow for text content
    TEXT_NODE_FONT_COLOR  = '#5D4037'     # Brown text for readability

    EDGE_COLOR_CHILD      = '#78909C'     # Blue-gray for structural edges
    EDGE_COLOR_TEXT       = '#FFB74D'     # Amber for text edges

    FONT_NAME             = 'Arial'
    FONT_SIZE             = 10
    MAX_LABEL_LENGTH      = 35

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 2: Select body graph (default behavior)
    # ═══════════════════════════════════════════════════════════════════════════

    def html_mgraph__to__mgraph(self, html_mgraph: Html_MGraph) -> MGraph:
        """Select body graph and store reference."""
        if html_mgraph and html_mgraph.body_graph:
            self._mgraph = html_mgraph.body_graph.mgraph
            return self._mgraph
        return None

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 3: Configure MGraph (optional native DOT settings)
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_mgraph(self, mgraph: MGraph) -> MGraph:
        """Store reference and optionally configure MGraph's native DOT export."""
        self._mgraph = mgraph

        # Optionally configure MGraph's native export_dot() for screenshots
        if mgraph:
            try:
                with mgraph.export().export_dot() as dot:
                    dot.set_graph__rank_dir__tb()
                    dot.set_node__shape__type__box()
                    dot.set_node__shape__rounded()
                    dot.show_node__value()
                    dot.show_edge__predicate()
            except Exception:
                pass  # Some MGraph versions may not support all methods

        return mgraph

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 4: Engine Configuration
    # ═══════════════════════════════════════════════════════════════════════════

    def configure_dot(self, config: MGraph__Engine__Config__Dot) -> MGraph__Engine__Config__Dot:
        """Configure DOT engine with semantic HTML styling."""
        config.rankdir        = 'TB'
        config.splines        = 'ortho'
        config.nodesep        = 0.35
        config.rank_sep       = 0.5
        config.node_shape     = 'box'
        config.node_style     = 'rounded,filled'
        config.node_fillcolor = self.DEPTH_COLORS[0]
        config.node_fontcolor = '#333333'
        config.edge_color     = self.EDGE_COLOR_CHILD
        config.edge_arrowsize = 0.6
        config.font_name      = self.FONT_NAME
        config.font_size      = self.FONT_SIZE
        config.max_label_len  = self.MAX_LABEL_LENGTH
        config.show_node_ids  = False
        config.bgcolor        = 'transparent'
        return config

    def configure_d3(self, config: MGraph__Engine__Config__D3) -> MGraph__Engine__Config__D3:
        config.charge_strength  = -350.0
        config.link_distance    = 70
        config.collision_radius = 30
        config.node_radius      = 22
        config.max_label_len    = self.MAX_LABEL_LENGTH
        return config

    def configure_cytoscape(self, config: MGraph__Engine__Config__Cytoscape) -> MGraph__Engine__Config__Cytoscape:
        config.layout_name      = 'dagre'
        config.layout_direction = 'TB'
        config.node_bg_color    = self.DEPTH_COLORS[1]
        config.node_border_color = '#64B5F6'
        config.max_label_len    = self.MAX_LABEL_LENGTH
        return config

    def configure_visjs(self, config: MGraph__Engine__Config__VisJs) -> MGraph__Engine__Config__VisJs:
        config.hierarchical     = True
        config.layout_direction = 'UD'
        config.physics_enabled  = False
        config.node_color_bg    = self.DEPTH_COLORS[1]
        config.node_color_border = '#64B5F6'
        config.level_separation = 100
        config.node_spacing     = 70
        config.max_label_len    = self.MAX_LABEL_LENGTH
        return config

    def configure_mermaid(self, config: MGraph__Engine__Config__Mermaid) -> MGraph__Engine__Config__Mermaid:
        config.diagram_type   = 'flowchart'
        config.direction      = 'TD'
        config.node_shape     = 'round'
        config.link_style     = 'arrow'
        config.max_label_len  = self.MAX_LABEL_LENGTH
        return config

    def configure_tree(self, config: MGraph__Engine__Config__Tree) -> MGraph__Engine__Config__Tree:
        config.output_format  = 'text'
        config.tree_chars     = True
        config.indent_size    = 2
        config.max_label_len  = 50
        config.show_node_ids  = False
        return config

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 5: Post-process - Generate custom semantic DOT output
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_export(self, output: Any) -> Any:
        """Override DOT output with semantically-styled version."""
        # Only process DOT string output
        if not isinstance(output, str) or 'digraph' not in output:
            return output

        # Generate custom DOT with semantic styling
        if self._mgraph:
            try:
                custom_dot = self._generate_semantic_dot()
                if custom_dot:
                    return custom_dot
            except Exception as e:
                print(f"Warning: Custom DOT generation failed: {e}")

        return output

    def _generate_semantic_dot(self) -> str:
        """Generate DOT string with semantic styling based on node types."""
        if not self._mgraph:
            return None

        lines = []
        lines.append('digraph G {')
        lines.append(f'  graph [rankdir=TB; splines=ortho; nodesep=0.35; ranksep=0.5; bgcolor="transparent"];')
        lines.append(f'  node [shape=box; style="rounded,filled"; fontname="{self.FONT_NAME}"; fontsize={self.FONT_SIZE}];')
        lines.append(f'  edge [fontname="{self.FONT_NAME}"; fontsize=8; arrowsize=0.6];')
        lines.append('')

        # Collect node info
        node_info = self._analyze_nodes()

        # Generate node definitions with semantic styling
        for node_id, info in node_info.items():
            node_def = self._format_node_def(node_id, info)
            lines.append(f'  {node_def}')

        lines.append('')

        # Generate edge definitions
        edge_lines = self._generate_edges(node_info)
        lines.extend(edge_lines)

        lines.append('}')
        return '\n'.join(lines)

    def _analyze_nodes(self) -> Dict[str, Dict]:
        """Analyze all nodes and extract semantic information."""
        node_info = {}

        for node in self._mgraph.data().nodes():
            node_id = str(node.node_id)
            path    = self._get_node_path(node)
            value   = self._get_node_value(node)

            # Determine node type and styling
            if path == 'text' or path.startswith('text:'):
                node_type = 'text'
                label     = self._truncate(value or '[text]', self.MAX_LABEL_LENGTH)
                depth     = 0
            else:
                node_type = 'element'
                label     = self._extract_tag_label(path)
                depth     = self._calculate_depth(path)

            node_info[node_id] = {
                'type'  : node_type,
                'label' : label,
                'depth' : depth,
                'path'  : path,
                'value' : value,
            }

        return node_info

    def _format_node_def(self, node_id: str, info: Dict) -> str:
        """Format a single node definition with appropriate styling."""
        safe_id = self._safe_id(node_id)
        label   = self._escape_label(info['label'])

        if info['type'] == 'text':
            # Text nodes: yellow with brown text
            fill_color = self.TEXT_NODE_COLOR
            font_color = self.TEXT_NODE_FONT_COLOR
        else:
            # Element nodes: blue shade by depth
            depth_idx  = min(info['depth'], len(self.DEPTH_COLORS) - 1)
            fill_color = self.DEPTH_COLORS[depth_idx]
            font_color = '#1A237E' if info['depth'] < 3 else '#FFFFFF'

        return f'"{safe_id}" [label="{label}"; fillcolor="{fill_color}"; fontcolor="{font_color}"];'

    def _generate_edges(self, node_info: Dict[str, Dict]) -> List[str]:
        """Generate edge definitions with predicate-based styling."""
        lines = []

        for edge in self._mgraph.data().edges():
            from_id   = str(edge.edge.data.from_node_id)
            to_id     = str(edge.edge.data.to_node_id)
            predicate = self._get_edge_predicate(edge)

            safe_from = self._safe_id(from_id)
            safe_to   = self._safe_id(to_id)

            # Skip if nodes not in our info (shouldn't happen)
            if from_id not in node_info or to_id not in node_info:
                continue

            # Style based on predicate
            if predicate == 'text':
                color = self.EDGE_COLOR_TEXT
                style = 'dashed'
            else:
                color = self.EDGE_COLOR_CHILD
                style = 'solid'

            edge_label = predicate if predicate else ''
            lines.append(f'  "{safe_from}" -> "{safe_to}" [label="{edge_label}"; color="{color}"; style="{style}"];')

        return lines

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _get_node_path(self, node) -> str:
        """Extract node_path from node."""
        if hasattr(node, 'node') and hasattr(node.node, 'data'):
            path = node.node.data.node_path
            return str(path) if path else ''
        return ''

    def _get_node_value(self, node) -> str:
        """Extract value from value node."""
        if hasattr(node, 'node') and hasattr(node.node, 'data'):
            node_data = node.node.data
            if hasattr(node_data, 'node_data') and hasattr(node_data.node_data, 'value'):
                return str(node_data.node_data.value)
        return None

    def _get_edge_predicate(self, edge) -> str:
        """Extract predicate from edge label."""
        if hasattr(edge, 'edge') and hasattr(edge.edge, 'data'):
            label = edge.edge.data.edge_label
            if label and hasattr(label, 'predicate') and label.predicate:
                return str(label.predicate)
        return ''

    def _extract_tag_label(self, path: str) -> str:
        """Extract clean tag label from path like 'body.div[0].span'."""
        if not path:
            return '[element]'

        # Get last segment
        segments = path.split('.')
        last     = segments[-1] if segments else path

        # Remove index like [0]
        if '[' in last:
            tag = last[:last.index('[')]
        else:
            tag = last

        # Format as <tag>
        return f'<{tag}>' if tag else '[element]'

    def _calculate_depth(self, path: str) -> int:
        """Calculate DOM depth from path."""
        if not path:
            return 0
        return path.count('.') + 1

    def _truncate(self, text: str, max_len: int) -> str:
        """Truncate text with ellipsis."""
        if not text:
            return ''
        text = ' '.join(text.split())  # Normalize whitespace
        if len(text) <= max_len:
            return text
        return text[:max_len - 3] + '...'

    def _escape_label(self, text: str) -> str:
        """Escape special characters for DOT labels."""
        if not text:
            return ''
        return (text.replace('\\', '\\\\')
                    .replace('"', '\\"')
                    .replace('\n', '\\n')
                    .replace('\r', ''))

    def _safe_id(self, id_str: str) -> str:
        """Make ID safe for DOT format."""
        if not id_str:
            return 'unknown'
        safe = id_str.replace('-', '_').replace(':', '_').replace('.', '_')
        if safe and safe[0].isdigit():
            safe = 'n' + safe
        return safe