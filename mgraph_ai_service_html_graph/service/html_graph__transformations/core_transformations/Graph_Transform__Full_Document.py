# Graph_Transform__Full_Document
#
# Full document visualization showing all 5 subgraphs as colored clusters:
# - Head (blue)
# - Body (green)
# - Attributes (orange)
# - Scripts (pink)
# - Styles (purple)
#
# Uses Html_MGraph__Data__Extractor to combine all subgraphs and generate
# a clustered DOT output with cross-reference edges shown as dashed lines.

from typing                                                                                       import Any, Dict, List, Optional
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base  import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                 import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Data__Extractor         import Html_MGraph__Data__Extractor, Extracted__Node, Extracted__Edge
from mgraph_db.mgraph.MGraph                                                                      import MGraph
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                    import type_safe


# ═══════════════════════════════════════════════════════════════════════════════════════════
# Cluster Configuration
# ═══════════════════════════════════════════════════════════════════════════════════════════

CLUSTER_CONFIG = {
    'head'   : { 'label'   : 'Head'       ,
                 'bgcolor' : '#e3f2fd'    ,                                                       # Light blue
                 'border'  : '#90caf9'    ,
                 'order'   : 0            },
    'body'   : { 'label'   : 'Body'       ,
                 'bgcolor' : '#e8f5e9'    ,                                                       # Light green
                 'border'  : '#a5d6a7'    ,
                 'order'   : 1            },
    'attrs'  : { 'label'   : 'Attributes' ,
                 'bgcolor' : '#fff3e0'    ,                                                       # Light orange
                 'border'  : '#ffcc80'    ,
                 'order'   : 2            },
    'scripts': { 'label'   : 'Scripts'    ,
                 'bgcolor' : '#fce4ec'    ,                                                       # Light pink
                 'border'  : '#f48fb1'    ,
                 'order'   : 3            },
    'styles' : { 'label'   : 'Styles'     ,
                 'bgcolor' : '#f3e5f5'    ,                                                       # Light purple
                 'border'  : '#ce93d8'    ,
                 'order'   : 4            },
}


class Graph_Transform__Full_Document(Graph_Transformation__Base):
    name        : str = 'full-document'
    label       : str = 'Full Document'
    description : str = 'Complete document with all subgraphs as colored clusters'

    # Internal state - populated during pipeline
    _html_mgraph     : Html_MGraph                   = None
    _extractor       : Html_MGraph__Data__Extractor  = None
    _extracted_nodes : List[Extracted__Node]         = None
    _extracted_edges : List[Extracted__Edge]         = None

    @type_safe
    def html__to__html_mgraph(self, html: str) -> Html_MGraph:
        """Phase 1: Parse HTML and store for later use."""
        self._html_mgraph = Html_MGraph.from_html(html)
        return self._html_mgraph

    @type_safe
    def html_mgraph__to__mgraph(self, html_mgraph: Html_MGraph) -> MGraph:
        """Phase 2: Extract all data using the extractor and store for Phase 5.
        
        Returns the document MGraph for compatibility, but the real work
        happens in transform_export() using the extracted data.
        """
        self._html_mgraph = html_mgraph

        # Use extractor to get combined nodes/edges from all subgraphs
        self._extractor = Html_MGraph__Data__Extractor(html_mgraph=html_mgraph)
        self._extractor.extract()
        self._extracted_nodes = self._extractor.nodes
        self._extracted_edges = self._extractor.edges

        # Return document MGraph for compatibility with pipeline
        if html_mgraph.document and html_mgraph.document.mgraph:
            return html_mgraph.document.mgraph
        return MGraph()

    @type_safe
    def transform_export(self, output: Any) -> Any:
        """Phase 5: Generate clustered DOT output from extracted data.
        
        This overrides the engine output with our custom clustered DOT.
        """
        # Only generate custom output for DOT format
        if isinstance(output, str) and 'digraph' in output:
            return self._generate_clustered_dot()
        return output

    # ═══════════════════════════════════════════════════════════════════════════════════════════
    # DOT Generation with Clusters
    # ═══════════════════════════════════════════════════════════════════════════════════════════

    def _generate_clustered_dot(self) -> str:
        """Generate DOT string with subgraph clusters."""
        lines = []

        # Graph header
        lines.append('digraph G {')
        lines.append('  graph [rankdir=TB; splines=true; nodesep=0.3; ranksep=0.5; bgcolor="transparent"; compound=true];')
        lines.append('  node [shape=box; style="rounded,filled"; fontname="Arial"; fontsize=10];')
        lines.append('  edge [fontname="Arial"; fontsize=8; arrowsize=0.7];')
        lines.append('')

        # Group nodes by graph_source
        nodes_by_cluster = self._group_nodes_by_cluster()

        # Generate clusters in order
        sorted_clusters = sorted(CLUSTER_CONFIG.items(), key=lambda x: x[1]['order'])
        for cluster_name, cluster_cfg in sorted_clusters:
            cluster_nodes = nodes_by_cluster.get(cluster_name, [])
            if cluster_nodes:                                                                     # Only render non-empty clusters
                lines.extend(self._generate_cluster(cluster_name, cluster_cfg, cluster_nodes))
                lines.append('')

        # Generate edges (including cross-cluster dashed edges)
        lines.extend(self._generate_edges())

        lines.append('}')
        return '\n'.join(lines)

    def _group_nodes_by_cluster(self) -> Dict[str, List[Extracted__Node]]:
        """Group extracted nodes by their graph_source."""
        groups: Dict[str, List[Extracted__Node]] = {}
        for node in (self._extracted_nodes or []):
            cluster = node.graph_source or 'unknown'
            if cluster not in groups:
                groups[cluster] = []
            groups[cluster].append(node)
        return groups

    def _generate_cluster(self, cluster_name: str,
                                cluster_cfg : Dict,
                                nodes       : List[Extracted__Node]) -> List[str]:
        """Generate DOT subgraph cluster."""
        lines = []
        lines.append(f'  subgraph cluster_{cluster_name} {{')
        lines.append(f'    label="{cluster_cfg["label"]}";')
        lines.append(f'    style="rounded";')
        lines.append(f'    bgcolor="{cluster_cfg["bgcolor"]}";')
        lines.append(f'    color="{cluster_cfg["border"]}";')
        lines.append(f'    fontname="Arial";')
        lines.append(f'    fontcolor="#333333";')
        lines.append('')

        for node in nodes:
            node_def = self._format_node(node)
            lines.append(f'    {node_def}')

        lines.append('  }')
        return lines

    def _format_node(self, node: Extracted__Node) -> str:
        """Format extracted node as DOT node definition."""
        node_id = self._safe_id(node.id)
        label   = self._escape_label(node.label)

        attrs = [
            f'label="{label}"'                 ,
            f'fillcolor="{node.fill_color}"'   ,
            f'fontcolor="{node.font_color}"'   ,
        ]

        # Map shape
        shape = self._map_shape(node.shape)
        if shape != 'box':
            attrs.append(f'shape={shape}')

        return f'"{node_id}" [{"; ".join(attrs)}];'

    def _generate_edges(self) -> List[str]:
        """Generate DOT edge definitions."""
        lines = []
        for edge in (self._extracted_edges or []):
            edge_def = self._format_edge(edge)
            if edge_def:
                lines.append(f'  {edge_def}')
        return lines

    def _format_edge(self, edge: Extracted__Edge) -> Optional[str]:
        """Format extracted edge as DOT edge definition."""
        source = self._safe_id(edge.source)
        target = self._safe_id(edge.target)

        if source == target:                                                                      # Skip self-loops
            return None

        attrs = []

        # Edge label (predicate)
        if edge.predicate:
            attrs.append(f'label="{edge.predicate}"')

        # Color
        if edge.color:
            attrs.append(f'color="{edge.color}"')

        # Dashed style for cross-cluster edges
        if edge.dashed:
            attrs.append('style="dashed"')

        if attrs:
            return f'"{source}" -> "{target}" [{"; ".join(attrs)}];'
        else:
            return f'"{source}" -> "{target}";'

    # ═══════════════════════════════════════════════════════════════════════════════════════════
    # Utility Methods
    # ═══════════════════════════════════════════════════════════════════════════════════════════

    def _safe_id(self, node_id: str) -> str:
        """Make node ID safe for DOT."""
        if not node_id:
            return 'unknown'
        # Replace problematic characters
        safe = node_id.replace('-', '_').replace(':', '_').replace('.', '_')
        # Ensure doesn't start with digit
        if safe and safe[0].isdigit():
            safe = 'n' + safe
        return safe

    def _escape_label(self, label: str) -> str:
        """Escape label for DOT."""
        if not label:
            return ''
        label = label.replace('\\', '\\\\').replace('"', '\\"')
        label = label.replace('\n', '\\n').replace('\r', '')
        # Truncate long labels
        if len(label) > 40:
            label = label[:37] + '...'
        return label

    def _map_shape(self, shape: str) -> str:
        """Map shape to DOT shape."""
        shapes = {
            'box'     : 'box'     ,
            'ellipse' : 'ellipse' ,
            'circle'  : 'circle'  ,
            'diamond' : 'diamond' ,
            'note'    : 'note'    ,
        }
        return shapes.get(shape, 'box')