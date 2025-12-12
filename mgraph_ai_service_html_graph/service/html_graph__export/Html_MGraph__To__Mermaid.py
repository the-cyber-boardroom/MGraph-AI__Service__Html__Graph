# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Mermaid Native Exporter
# Converts Html_MGraph to Mermaid flowchart syntax
# https://mermaid.js.org/
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                             import List, Dict
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from mgraph_db.mgraph.MGraph                                                            import MGraph
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config       import Html_MGraph__Render__Config
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Data__Extractor import (
    Html_MGraph__Data__Extractor, Extracted__Node, Extracted__Edge
)


class Html_MGraph__To__Mermaid(Type_Safe):                                              # Converts Html_MGraph to Mermaid flowchart
    mgraph      : MGraph
    config      : Html_MGraph__Render__Config = None
    _id_map     : Dict[str, str]              = None                                    # Long ID → short ID
    _id_counter : int                         = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self._id_map is None:
            self._id_map = {}

    def export(self) -> str:                                                            # Export to Mermaid flowchart string
        self._id_map = {}
        self._id_counter = 0

        extractor = Html_MGraph__Data__Extractor(mgraph=self.mgraph, config=self.config)
        extractor.extract()

        lines = ['flowchart TB']

        for node in extractor.nodes:                                                    # Node definitions
            lines.append(f'    {self._format_node(node)}')

        lines.append('')
        lines.extend(self._format_styles(extractor.nodes))                              # Style classes
        lines.append('')

        for edge in extractor.edges:                                                    # Edge definitions
            edge_line = self._format_edge(edge)
            if edge_line:
                lines.append(f'    {edge_line}')

        return '\n'.join(lines)

    def _get_short_id(self, long_id: str) -> str:                                       # Get/create short Mermaid-safe ID
        if long_id not in self._id_map:
            self._id_map[long_id] = f'n{self._id_counter}'
            self._id_counter += 1
        return self._id_map[long_id]

    def _format_node(self, node: Extracted__Node) -> str:                               # Format node as Mermaid syntax
        short_id = self._get_short_id(node.id)
        label    = self._escape_label(node.label)

        shapes = {                                                                      # Different shapes per node type
            'element' : f'{short_id}["{label}"]'    ,                                   # Rectangle
            'tag'     : f'{short_id}(("{label}"))'  ,                                   # Circle
            'attr'    : f'{short_id}{{{{"{label}"}}}}',                                 # Hexagon
            'text'    : f'{short_id}>"{label}"]'                                        # Flag
        }
        return shapes.get(node.node_type, f'{short_id}["{label}"]')

    def _format_edge(self, edge: Extracted__Edge) -> str:                               # Format edge as Mermaid syntax
        source_id = self._get_short_id(edge.source)
        target_id = self._get_short_id(edge.target)

        if source_id == target_id:                                                      # Skip self-loops
            return ''

        arrow = '-.->' if edge.dashed else '-->'
        return f'{source_id} {arrow} {target_id}'

    def _format_styles(self, nodes: List[Extracted__Node]) -> List[str]:                # Generate Mermaid style definitions
        by_type: Dict[str, List[str]] = {'element': [], 'tag': [], 'attr': [], 'text': []}

        for node in nodes:
            short_id = self._id_map.get(node.id)
            if short_id:
                node_type = node.node_type if node.node_type in by_type else 'element'
                by_type[node_type].append(short_id)

        styles = {
            'element' : 'fill:#E8E8E8,stroke:#999999,color:#333333'  ,
            'tag'     : 'fill:#4A90D9,stroke:#2E5B8A,color:#FFFFFF'  ,
            'attr'    : 'fill:#B39DDB,stroke:#7E57C2,color:#333333'  ,
            'text'    : 'fill:#FFFACD,stroke:#DAA520,color:#333333'
        }

        result = []
        for node_type, ids in by_type.items():
            if ids:
                result.append(f'    style {",".join(ids)} {styles[node_type]}')
        return result

    def _escape_label(self, label: str) -> str:                                         # Escape for Mermaid syntax
        if not label:
            return ''
        label = label.replace('\\', '\\\\').replace('"', "'")
        label = label.replace('\n', ' ')
        for char in '<>[]{}()':
            label = label.replace(char, '')
        return label[:30] + '...' if len(label) > 30 else label
