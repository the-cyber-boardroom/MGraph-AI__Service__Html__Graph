# MGraph Engine - VisJs
#
# Converts MGraph to vis.js Network compatible JSON format.
# Output structure: { nodes: [...], edges: [...], options: {...} }

from typing                                                                                     import Dict, List, Any
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__VisJs import MGraph__Engine__Config__VisJs
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Base                  import MGraph__Engine__Base



class MGraph__Engine__VisJs(MGraph__Engine__Base):   # VisJs JSON exporter
    config: MGraph__Engine__Config__VisJs


    def export(self) -> Dict[str, Any]:                                          # Export MGraph to VisJs JSON
        result = {
            'nodes': self._export_nodes(),
            'edges': self._export_edges(),
        }
        if self.config.include_options:
            result['options'] = self._export_options()
        if self.config.include_stats:
            result['stats'] = self._build_stats()
        return result

    # ═══════════════════════════════════════════════════════════════════════════
    # Node Export
    # ═══════════════════════════════════════════════════════════════════════════

    def _export_nodes(self) -> List[Dict[str, Any]]:                             # Convert all nodes to VisJs format
        nodes = []
        for level, node in enumerate(self.nodes()):
            node_data = self._format_node(node, level)
            if node_data:
                nodes.append(node_data)
        return nodes

    def _format_node(self, node, level: int) -> Dict[str, Any]:                  # Format single node for VisJs
        cfg     = self.config
        node_id = self.node_id_str(node)
        path    = self.node_path(node)
        value   = self.node_value(node)

        label = value or path or node_id[:8]
        label = self.truncate(label, cfg.max_label_len)

        node_data = {
            'id'   : node_id       ,
            'label': label         ,
            'shape': cfg.node_shape,
            'color': {
                'background': cfg.node_color_bg     ,
                'border'    : cfg.node_color_border ,
                'highlight' : {
                    'background': cfg.node_color_highlight_bg    ,
                    'border'    : cfg.node_color_highlight_border,
                },
            },
            'font': {
                'size': cfg.node_font_size,
            },
            'borderWidth': cfg.node_border_width,
        }

        if cfg.hierarchical:                                                     # Add level for hierarchical layout
            node_data['level'] = level

        node_type = self._get_node_type(node)                                    # Add node type metadata
        if node_type:
            node_data['nodeType'] = node_type

        if path:
            node_data['path'] = path

        bg_color = self.get_node_style(node, 'bg_color')                         # Apply style overrides
        if bg_color:
            node_data['color']['background'] = bg_color

        return node_data

    def _get_node_type(self, node) -> str:                                       # Determine node type category
        if hasattr(node, 'node') and hasattr(node.node, 'data'):
            node_data = node.node.data
            if hasattr(node_data, 'node_data'):
                data_type = type(node_data.node_data).__name__
                if 'Element' in data_type:
                    return 'element'
                elif 'Text' in data_type or 'Value' in data_type:
                    return 'text'
                elif 'Attribute' in data_type:
                    return 'attribute'
        return 'unknown'

    # ═══════════════════════════════════════════════════════════════════════════
    # Edge Export
    # ═══════════════════════════════════════════════════════════════════════════

    def _export_edges(self) -> List[Dict[str, Any]]:                             # Convert all edges to VisJs format
        edges = []
        for i, edge in enumerate(self.edges()):
            edge_data = self._format_edge(edge, i)
            if edge_data:
                edges.append(edge_data)
        return edges

    def _format_edge(self, edge, index: int) -> Dict[str, Any]:                  # Format single edge for VisJs
        cfg       = self.config
        from_id   = self.edge_from_id(edge)
        to_id     = self.edge_to_id(edge)
        predicate = self.edge_predicate(edge)

        edge_data = {
            'id'    : f'e{index}'                   ,
            'from'  : from_id                       ,
            'to'    : to_id                         ,
            'arrows': cfg.edge_arrows               ,
            'color' : {'color': cfg.edge_color}     ,
            'width' : cfg.edge_width                ,
            'smooth': {'type': cfg.edge_smooth_type},
        }

        if predicate:
            edge_data['label'] = predicate

        return edge_data

    # ═══════════════════════════════════════════════════════════════════════════
    # Options and Stats
    # ═══════════════════════════════════════════════════════════════════════════

    def _export_options(self) -> Dict[str, Any]:                                 # Export vis.js network options
        cfg = self.config
        options = {
            'physics': {
                'enabled': cfg.physics_enabled,
            },
            'interaction': {
                'hover'           : True,
                'navigationButtons': True,
                'keyboard'        : True,
            },
        }

        if cfg.hierarchical:
            options['layout'] = {
                'hierarchical': {
                    'enabled'        : True               ,
                    'direction'      : cfg.layout_direction,
                    'sortMethod'     : 'directed'         ,
                    'levelSeparation': cfg.level_separation,
                    'nodeSpacing'    : cfg.node_spacing   ,
                },
            }

        return options

    def _build_stats(self) -> Dict[str, int]:                                    # Build graph statistics
        return {
            'nodeCount': len(self.nodes()),
            'edgeCount': len(self.edges()),
        }
