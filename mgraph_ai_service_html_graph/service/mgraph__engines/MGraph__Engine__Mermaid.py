# MGraph Engine - Mermaid
#
# Converts MGraph to Mermaid diagram syntax.
# Produces flowchart/graph markdown syntax for rendering.

from typing                                                                                         import Dict, List
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Mermaid   import MGraph__Engine__Config__Mermaid
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Base                      import MGraph__Engine__Base


class MGraph__Engine__Mermaid(MGraph__Engine__Base): # Mermaid diagram exporter
    config: MGraph__Engine__Config__Mermaid

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.config is None:
            self.config = MGraph__Engine__Config__Mermaid()

    def export(self) -> str:                                                     # Export MGraph to Mermaid string
        lines = []
        lines.append(self._diagram_header())
        lines.extend(self._node_definitions())
        lines.extend(self._edge_definitions())
        return '\n'.join(lines)

    # ═══════════════════════════════════════════════════════════════════════════
    # Diagram Structure
    # ═══════════════════════════════════════════════════════════════════════════

    def _diagram_header(self) -> str:                                            # Mermaid diagram declaration
        cfg = self.config
        return f'{cfg.diagram_type} {cfg.direction}'

    # ═══════════════════════════════════════════════════════════════════════════
    # Node Definitions
    # ═══════════════════════════════════════════════════════════════════════════

    def _node_definitions(self) -> List[str]:                                    # Generate Mermaid node statements
        lines        = []
        defined_ids  = set()

        for edge in self.edges():                                                # Define nodes via edges
            from_id = self.edge_from_id(edge)
            to_id   = self.edge_to_id(edge)
            defined_ids.add(from_id)
            defined_ids.add(to_id)

        for node in self.nodes():                                                # Define orphan nodes explicitly
            node_id = self.node_id_str(node)
            if node_id not in defined_ids:
                node_def = self._format_node_definition(node)
                if node_def:
                    lines.append(node_def)

        return lines

    def _format_node_definition(self, node) -> str:                              # Format standalone node definition
        node_id = self._mermaid_id(self.node_id_str(node))
        label   = self._node_label(node)
        shape   = self._node_shape_syntax(label)
        return f'    {node_id}{shape}'

    def _node_label(self, node) -> str:                                          # Build node label text
        path  = self.node_path(node)
        value = self.node_value(node)

        if value:
            label = value
        elif path:
            label = path
        else:
            label = self.node_id_str(node)[:8]

        label = self.truncate(label, self.config.max_label_len)

        if self.config.escape_special:
            label = self._escape_mermaid(label)

        return label

    def _node_shape_syntax(self, label: str) -> str:                             # Get node shape brackets
        shape = self.config.node_shape
        shapes = {
            'rect'   : (f'["{label}"]'  , f'["{label}"]'  ),
            'round'  : (f'("{label}")'  , f'("{label}")'  ),
            'stadium': (f'(["{label}"])', f'(["{label}"])'),
            'diamond': (f'{{"{label}"}}', f'{{"{label}"}}'),
            'circle' : (f'(("{label}"))', f'(("{label}"))'),
        }
        return shapes.get(shape, (f'["{label}"]', f'["{label}"]'))[0]

    # ═══════════════════════════════════════════════════════════════════════════
    # Edge Definitions
    # ═══════════════════════════════════════════════════════════════════════════

    def _edge_definitions(self) -> List[str]:                                    # Generate Mermaid edge statements
        lines     = []
        node_map  = self._build_node_map()

        for edge in self.edges():
            edge_def = self._format_edge(edge, node_map)
            if edge_def:
                lines.append(edge_def)

        return lines

    def _build_node_map(self) -> Dict[str, str]:                                 # Build node_id -> label map
        node_map = {}
        for node in self.nodes():
            node_id = self.node_id_str(node)
            label   = self._node_label(node)
            node_map[node_id] = label
        return node_map

    def _format_edge(self, edge, node_map: Dict[str, str]) -> str:               # Format single edge as Mermaid
        from_id   = self.edge_from_id(edge)
        to_id     = self.edge_to_id(edge)
        predicate = self.edge_predicate(edge)

        from_mermaid = self._mermaid_id(from_id)
        to_mermaid   = self._mermaid_id(to_id)

        from_label = node_map.get(from_id, from_id[:8])                          # Get labels for inline definition
        to_label   = node_map.get(to_id, to_id[:8])

        from_shape = self._node_shape_syntax(from_label)
        to_shape   = self._node_shape_syntax(to_label)

        link = self._link_syntax(predicate)

        return f'    {from_mermaid}{from_shape} {link} {to_mermaid}{to_shape}'

    def _link_syntax(self, label: str = None) -> str:                            # Get link arrow syntax
        style = self.config.link_style
        if label:
            label = self._escape_mermaid(label)
            links = {
                'arrow' : f'-->|"{label}"|',
                'open'  : f'---|"{label}"|',
                'dotted': f'-.->|"{label}"|',
            }
        else:
            links = {
                'arrow' : '-->' ,
                'open'  : '---' ,
                'dotted': '-.->',
            }
        return links.get(style, '-->')

    # ═══════════════════════════════════════════════════════════════════════════
    # Utilities
    # ═══════════════════════════════════════════════════════════════════════════

    def _mermaid_id(self, id_str: str) -> str:                                   # Make ID safe for Mermaid
        safe = self.safe_id(id_str)
        if safe and safe[0].isdigit():                                           # Mermaid IDs can't start with digit
            safe = f'n{safe}'
        return safe

    def _escape_mermaid(self, text: str) -> str:                                 # Escape special Mermaid characters
        if not text:
            return ''
        text = text.replace('"', "'")                                            # Replace quotes
        text = text.replace('<', '&lt;')                                         # HTML entities for angle brackets
        text = text.replace('>', '&gt;')
        text = text.replace('\n', ' ')                                           # Remove newlines
        return text
