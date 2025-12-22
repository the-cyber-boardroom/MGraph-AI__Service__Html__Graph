from typing                                                                         import Dict, Any, List, Optional
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                   import Html_MGraph
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Base      import Html_MGraph__Base
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                   import Node_Id


class Html_MGraph__To__Dot(Type_Safe):                                              # Convert Html_MGraph to DOT format for visualization
    """Converts Html_MGraph to Graphviz DOT format.

    Supports:
    - Full multi-graph visualization (graph of graphs)
    - Individual component graph visualization
    - DOT clusters for logical grouping
    - Customizable node/edge styling per graph type

    Usage:
        # Full graph
        dot = Html_MGraph__To__Dot().convert(mgraph)

        # Body only
        dot = Html_MGraph__To__Dot().body_only(mgraph)

        # Custom selection
        dot = Html_MGraph__To__Dot(show_scripts=False, show_styles=False).convert(mgraph)
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # Configuration
    # ═══════════════════════════════════════════════════════════════════════════

    show_head    : bool = True                                                      # Include head graph
    show_body    : bool = True                                                      # Include body graph
    show_attrs   : bool = True                                                      # Include attributes graph
    show_scripts : bool = True                                                      # Include scripts graph
    show_styles  : bool = True                                                      # Include styles graph
    use_clusters : bool = True                                                      # Use DOT subgraphs for grouping
    show_legend  : bool = False                                                     # Show color legend

    # ═══════════════════════════════════════════════════════════════════════════
    # Color Schemes
    # ═══════════════════════════════════════════════════════════════════════════

    COLORS = { 'head'    : {'fill': '#E3F2FD', 'border': '#1976D2', 'label': 'Head'      },
               'body'    : {'fill': '#E8F5E9', 'border': '#388E3C', 'label': 'Body'      },
               'attrs'   : {'fill': '#FFF3E0', 'border': '#F57C00', 'label': 'Attributes'},
               'scripts' : {'fill': '#FCE4EC', 'border': '#C2185B', 'label': 'Scripts'   },
               'styles'  : {'fill': '#F3E5F5', 'border': '#7B1FA2', 'label': 'Styles'    },
               'text'    : {'fill': '#FFFDE7', 'border': '#FBC02D', 'label': 'Text'      },
               'edge'    : {'child': '#666666', 'text': '#999999', 'attr': '#F57C00'    }}

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Conversion Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def convert(self, mgraph: Html_MGraph) -> str:                                  # Convert full Html_MGraph to DOT
        lines = ['digraph Html_MGraph {']
        lines.append('    rankdir=TB;')
        lines.append('    node [shape=box, style="filled,rounded", fontname="Arial"];')
        lines.append('    edge [fontname="Arial", fontsize=10];')
        lines.append('')

        if self.use_clusters:
            lines.extend(self._render_clustered(mgraph))
        else:
            lines.extend(self._render_flat(mgraph))

        if self.show_legend:
            lines.extend(self._render_legend())

        lines.append('}')
        return '\n'.join(lines)

    def convert_single(self, graph: Html_MGraph__Base, name: str) -> str:           # Convert single component graph to DOT
        lines = [f'digraph {name} {{']
        lines.append('    rankdir=TB;')
        lines.append('    node [shape=box, style="filled,rounded", fontname="Arial"];')
        lines.append('    edge [fontname="Arial", fontsize=10];')
        lines.append('')

        color = self.COLORS.get(name.lower(), self.COLORS['body'])
        lines.extend(self._render_graph(graph, name, color, indent='    '))

        lines.append('}')
        return '\n'.join(lines)

    # ═══════════════════════════════════════════════════════════════════════════
    # Convenience Methods - Single Graph
    # ═══════════════════════════════════════════════════════════════════════════

    def head_only(self, mgraph: Html_MGraph) -> str:                                # Render only head graph
        return self.convert_single(mgraph.head_graph, 'Head')

    def body_only(self, mgraph: Html_MGraph) -> str:                                # Render only body graph
        return self.convert_single(mgraph.body_graph, 'Body')

    def attrs_only(self, mgraph: Html_MGraph) -> str:                               # Render only attributes graph
        return self.convert_single(mgraph.attrs_graph, 'Attrs')

    def scripts_only(self, mgraph: Html_MGraph) -> str:                             # Render only scripts graph
        return self.convert_single(mgraph.scripts_graph, 'Scripts')

    def styles_only(self, mgraph: Html_MGraph) -> str:                              # Render only styles graph
        return self.convert_single(mgraph.styles_graph, 'Styles')

    # ═══════════════════════════════════════════════════════════════════════════
    # Rendering Methods - Clustered Layout
    # ═══════════════════════════════════════════════════════════════════════════

    def _render_clustered(self, mgraph: Html_MGraph) -> List[str]:                  # Render with DOT clusters
        lines = []

        if self.show_head and mgraph.head_graph:
            lines.extend(self._render_cluster(mgraph.head_graph, 'head', self.COLORS['head']))

        if self.show_body and mgraph.body_graph:
            lines.extend(self._render_cluster(mgraph.body_graph, 'body', self.COLORS['body']))

        if self.show_attrs and mgraph.attrs_graph:
            lines.extend(self._render_cluster(mgraph.attrs_graph, 'attrs', self.COLORS['attrs']))

        if self.show_scripts and mgraph.scripts_graph:
            lines.extend(self._render_cluster(mgraph.scripts_graph, 'scripts', self.COLORS['scripts']))

        if self.show_styles and mgraph.styles_graph:
            lines.extend(self._render_cluster(mgraph.styles_graph, 'styles', self.COLORS['styles']))

        lines.extend(self._render_cross_references(mgraph))                         # Add edges between graphs

        return lines

    def _render_cluster(self, graph: Html_MGraph__Base, name: str, color: Dict) -> List[str]:
        lines = []
        lines.append(f'    subgraph cluster_{name} {{')
        lines.append(f'        label="{color["label"]}";')
        lines.append(f'        style="filled,rounded";')
        lines.append(f'        fillcolor="{color["fill"]}";')
        lines.append(f'        color="{color["border"]}";')
        lines.append(f'        penwidth=2;')
        lines.append('')

        lines.extend(self._render_graph(graph, name, color, indent='        '))

        lines.append('    }')
        lines.append('')
        return lines

    # ═══════════════════════════════════════════════════════════════════════════
    # Rendering Methods - Flat Layout
    # ═══════════════════════════════════════════════════════════════════════════

    def _render_flat(self, mgraph: Html_MGraph) -> List[str]:                       # Render without clusters
        lines = []

        if self.show_head and mgraph.head_graph:
            lines.extend(self._render_graph(mgraph.head_graph, 'head', self.COLORS['head']))

        if self.show_body and mgraph.body_graph:
            lines.extend(self._render_graph(mgraph.body_graph, 'body', self.COLORS['body']))

        if self.show_attrs and mgraph.attrs_graph:
            lines.extend(self._render_graph(mgraph.attrs_graph, 'attrs', self.COLORS['attrs']))

        if self.show_scripts and mgraph.scripts_graph:
            lines.extend(self._render_graph(mgraph.scripts_graph, 'scripts', self.COLORS['scripts']))

        if self.show_styles and mgraph.styles_graph:
            lines.extend(self._render_graph(mgraph.styles_graph, 'styles', self.COLORS['styles']))

        lines.extend(self._render_cross_references(mgraph))

        return lines

    # ═══════════════════════════════════════════════════════════════════════════
    # Rendering Methods - Graph Content
    # ═══════════════════════════════════════════════════════════════════════════

    def _render_graph(self, graph: Html_MGraph__Base, name: str, color: Dict, indent: str = '    ') -> List[str]:
        lines = []

        for node_id in graph.nodes_ids():                                           # Render nodes
            node_dot = self._render_node(graph, node_id, name, color, indent)
            if node_dot:
                lines.append(node_dot)

        lines.append('')

        for edge in self._get_edges(graph):                                         # Render edges
            edge_dot = self._render_edge(edge, name, indent)
            if edge_dot:
                lines.append(edge_dot)

        return lines

    def _render_node(self, graph: Html_MGraph__Base, node_id: Node_Id, graph_name: str, color: Dict, indent: str) -> str:
        node_path = graph.node_path(node_id)
        path_str  = str(node_path) if node_path else 'unknown'

        node_value = graph.node_value(node_id)                                      # Determine node type and label
        if node_value is not None:
            label      = self._escape_label(str(node_value)[:50])                   # Value node - show value (truncated)
            fill_color = self.COLORS['text']['fill']
            border     = self.COLORS['text']['border']
        else:
            label      = path_str                                                   # Element node - show path
            fill_color = color['fill']
            border     = color['border']

        safe_id = self._safe_node_id(node_id, graph_name)
        return f'{indent}"{safe_id}" [label="{label}", fillcolor="{fill_color}", color="{border}"];'

    def _render_edge(self, edge: Dict, graph_name: str, indent: str) -> str:
        from_id   = self._safe_node_id(edge['from'], graph_name)
        to_id     = self._safe_node_id(edge['to'], graph_name)
        predicate = edge.get('predicate', '')
        edge_path = edge.get('edge_path', '')

        label = predicate
        if edge_path:
            label = f"{predicate}[{edge_path}]" if predicate else edge_path

        color = self.COLORS['edge'].get(predicate, '#666666')
        return f'{indent}"{from_id}" -> "{to_id}" [label="{label}", color="{color}"];'

    # ═══════════════════════════════════════════════════════════════════════════
    # Cross-Reference Rendering (Shared Node IDs between graphs)
    # ═══════════════════════════════════════════════════════════════════════════

    def _render_cross_references(self, mgraph: Html_MGraph) -> List[str]:           # Render edges showing shared node IDs
        lines = []
        lines.append('    // Cross-references between graphs')

        if self.show_attrs and self.show_body:                                      # Body elements → Attributes
            for node_id in mgraph.body_graph.all_element_nodes():
                if mgraph.attrs_graph.get_tag(node_id):
                    body_id  = self._safe_node_id(node_id, 'body')
                    attrs_id = self._safe_node_id(node_id, 'attrs')
                    lines.append(f'    "{body_id}" -> "{attrs_id}" [style=dashed, color="#999999", constraint=false];')

        if self.show_attrs and self.show_head:                                      # Head elements → Attributes
            for node_id in mgraph.head_graph.all_element_nodes():
                if mgraph.attrs_graph.get_tag(node_id):
                    head_id  = self._safe_node_id(node_id, 'head')
                    attrs_id = self._safe_node_id(node_id, 'attrs')
                    lines.append(f'    "{head_id}" -> "{attrs_id}" [style=dashed, color="#999999", constraint=false];')

        return lines

    # ═══════════════════════════════════════════════════════════════════════════
    # Legend Rendering
    # ═══════════════════════════════════════════════════════════════════════════

    def _render_legend(self) -> List[str]:                                          # Render color legend
        lines = []
        lines.append('    subgraph cluster_legend {')
        lines.append('        label="Legend";')
        lines.append('        style="filled";')
        lines.append('        fillcolor="#FAFAFA";')
        lines.append('        node [shape=box, width=1.5];')

        for name, color in self.COLORS.items():
            if name != 'edge' and isinstance(color, dict) and 'fill' in color:
                lines.append(f'        legend_{name} [label="{color["label"]}", fillcolor="{color["fill"]}", color="{color["border"]}"];')

        lines.append('    }')
        return lines

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _get_edges(self, graph: Html_MGraph__Base) -> List[Dict]:                   # Extract edges from graph
        edges = []
        for node_id in graph.nodes_ids():
            for edge in graph.outgoing_edges(node_id):
                predicate = graph.edge_predicate(edge)
                edge_path = graph.edge_path(edge)
                edges.append({ 'from'      : node_id                    ,
                               'to'        : edge.edge.data.to_node_id  ,
                               'predicate' : str(predicate) if predicate else '' ,
                               'edge_path' : str(edge_path) if edge_path else '' })
        return edges

    def _safe_node_id(self, node_id: Node_Id, prefix: str) -> str:                  # Create unique DOT node ID
        return f"{prefix}_{str(node_id)}"

    def _escape_label(self, text: str) -> str:                                      # Escape special characters for DOT labels
        return (text.replace('\\', '\\\\')
                    .replace('"', '\\"')
                    .replace('\n', '\\n')
                    .replace('\r', ''))