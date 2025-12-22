# MGraph Engine - DOT (Graphviz)
#
# Converts MGraph to DOT language for Graphviz rendering.
# Produces directed graph with configurable layout and styling.

from typing                                                                                   import Dict, List, Optional
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Base                import MGraph__Engine__Base
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Dot import MGraph__Engine__Config__Dot


class MGraph__Engine__Dot(MGraph__Engine__Base):   # DOT format exporter
    config: MGraph__Engine__Config__Dot

    def export(self) -> str:                                                    # Export MGraph to DOT string
        lines = []
        lines.append(self._graph_header())
        lines.append(self._graph_attributes())
        lines.append(self._node_defaults())
        lines.append(self._edge_defaults())
        lines.extend(self._node_definitions())
        lines.extend(self._edge_definitions())
        lines.append('}')
        return '\n'.join(lines)

    # ═══════════════════════════════════════════════════════════════════════════
    # Graph Structure
    # ═══════════════════════════════════════════════════════════════════════════

    def _graph_header(self) -> str:                                             # DOT digraph declaration
        return 'digraph G {'

    def _graph_attributes(self) -> str:                                         # Global graph attributes
        cfg = self.config
        attrs = [
            f'rankdir={cfg.rankdir}'   ,
            f'splines={cfg.splines}'   ,
            f'nodesep={cfg.nodesep}'   ,
            f'ranksep={cfg.rank_sep}'  ,
            f'bgcolor="{cfg.bgcolor}"' ,
        ]
        if cfg.concentrate:
            attrs.append('concentrate=true')
        return f'  graph [{"; ".join(attrs)}];'

    def _node_defaults(self) -> str:                                            # Default node attributes
        cfg = self.config
        attrs = [
            f'shape={cfg.node_shape}'          ,
            f'style="{cfg.node_style}"'        ,
            f'fillcolor="{cfg.node_fillcolor}"',
            f'fontcolor="{cfg.node_fontcolor}"',
            f'fontname="{cfg.font_name}"'      ,
            f'fontsize={cfg.font_size}'        ,
        ]
        return f'  node [{"; ".join(attrs)}];'

    def _edge_defaults(self) -> str:                                            # Default edge attributes
        cfg = self.config
        attrs = [
            f'color="{cfg.edge_color}"'     ,
            f'arrowsize={cfg.edge_arrowsize}',
            f'fontname="{cfg.font_name}"'   ,
            f'fontsize={cfg.font_size - 2}' ,
        ]
        return f'  edge [{"; ".join(attrs)}];'

    # ═══════════════════════════════════════════════════════════════════════════
    # Node Definitions
    # ═══════════════════════════════════════════════════════════════════════════

    def _node_definitions(self) -> List[str]:                                   # Generate DOT node statements
        lines = []
        for node in self.nodes():
            node_def = self._format_node(node)
            if node_def:
                lines.append(node_def)
        return lines

    def _format_node(self, node) -> Optional[str]:                              # Format single node as DOT
        node_id   = self.safe_id(self.node_id_str(node))
        label     = self._node_label(node)
        attrs     = self._node_attributes(node)
        attrs_str = ', '.join(f'{k}="{v}"' for k, v in attrs.items())
        return f'  "{node_id}" [label="{label}", {attrs_str}];'

    def _node_label(self, node) -> str:                                         # Build node label text
        path  = self.node_path(node)
        value = self.node_value(node)

        if value:
            label = self.escape_quotes(value)
        elif path:
            label = self.escape_quotes(path)
        else:
            label = self.node_id_str(node)[:8]

        label = self.truncate(label, self.config.max_label_len)

        if self.config.show_node_ids:
            short_id = self.node_id_str(node)[:8]
            label    = f'{short_id}\\n{label}'

        return label

    def _node_attributes(self, node) -> Dict[str, str]:                         # Get node styling attributes
        attrs = {}

        fillcolor = self.get_node_style(node, 'fillcolor')                      # Check for styling metadata
        if fillcolor:
            attrs['fillcolor'] = fillcolor

        fontcolor = self.get_node_style(node, 'fontcolor')
        if fontcolor:
            attrs['fontcolor'] = fontcolor

        shape = self.get_node_style(node, 'shape')
        if shape:
            attrs['shape'] = shape

        return attrs

    # ═══════════════════════════════════════════════════════════════════════════
    # Edge Definitions
    # ═══════════════════════════════════════════════════════════════════════════

    def _edge_definitions(self) -> List[str]:                                   # Generate DOT edge statements
        lines = []
        for edge in self.edges():
            edge_def = self._format_edge(edge)
            if edge_def:
                lines.append(edge_def)
        return lines

    def _format_edge(self, edge) -> Optional[str]:                              # Format single edge as DOT
        from_id   = self.safe_id(self.edge_from_id(edge))
        to_id     = self.safe_id(self.edge_to_id(edge))
        predicate = self.edge_predicate(edge)
        attrs     = self._edge_attributes(edge)

        if predicate:
            attrs['label'] = self.escape_quotes(predicate)

        if attrs:
            attrs_str = ', '.join(f'{k}="{v}"' for k, v in attrs.items())
            return f'  "{from_id}" -> "{to_id}" [{attrs_str}];'
        else:
            return f'  "{from_id}" -> "{to_id}";'

    def _edge_attributes(self, edge) -> Dict[str, str]:                         # Get edge styling attributes
        attrs = {}

        color = self.get_edge_style(edge, 'color')                              # Check for styling metadata
        if color:
            attrs['color'] = color

        style = self.get_edge_style(edge, 'style')
        if style:
            attrs['style'] = style

        return attrs
