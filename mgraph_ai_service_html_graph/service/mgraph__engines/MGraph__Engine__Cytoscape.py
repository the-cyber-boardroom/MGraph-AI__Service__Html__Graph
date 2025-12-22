# MGraph Engine - Cytoscape
#
# Converts MGraph to Cytoscape.js compatible JSON format.
# Output structure: { elements: { nodes: [...], edges: [...] }, style: [...], layout: {...} }

from typing                                                                                         import Dict, List, Any
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Base                      import MGraph__Engine__Base
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Cytoscape import MGraph__Engine__Config__Cytoscape


class MGraph__Engine__Cytoscape(MGraph__Engine__Base):  # Cytoscape JSON exporter
    config: MGraph__Engine__Config__Cytoscape

    def export(self) -> Dict[str, Any]:                                          # Export MGraph to Cytoscape JSON
        result = {
            'elements': {
                'nodes': self._export_nodes(),
                'edges': self._export_edges(),
            },
            'layout': self._export_layout(),
        }
        if self.config.include_style:
            result['style'] = self._export_style()
        if self.config.include_stats:
            result['stats'] = self._build_stats()
        return result

    # ═══════════════════════════════════════════════════════════════════════════
    # Node Export
    # ═══════════════════════════════════════════════════════════════════════════

    def _export_nodes(self) -> List[Dict[str, Any]]:                             # Convert all nodes to Cytoscape format
        nodes = []
        for node in self.nodes():
            node_data = self._format_node(node)
            if node_data:
                nodes.append(node_data)
        return nodes

    def _format_node(self, node) -> Dict[str, Any]:                              # Format single node for Cytoscape
        node_id = self.node_id_str(node)
        path    = self.node_path(node)
        value   = self.node_value(node)

        label = value or path or node_id[:8]
        label = self.truncate(label, self.config.max_label_len)

        data = {
            'id'   : node_id,
            'label': label  ,
        }

        if path:
            data['path'] = path

        node_type = self._get_node_type(node)                                    # Add node type for styling
        if node_type:
            data['nodeType'] = node_type

        bg_color = self.get_node_style(node, 'bg_color')                         # Add styling overrides
        if bg_color:
            data['bgColor'] = bg_color

        return {'data': data}

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

    def _export_edges(self) -> List[Dict[str, Any]]:                             # Convert all edges to Cytoscape format
        edges = []
        for i, edge in enumerate(self.edges()):
            edge_data = self._format_edge(edge, i)
            if edge_data:
                edges.append(edge_data)
        return edges

    def _format_edge(self, edge, index: int) -> Dict[str, Any]:                  # Format single edge for Cytoscape
        from_id   = self.edge_from_id(edge)
        to_id     = self.edge_to_id(edge)
        predicate = self.edge_predicate(edge)

        data = {
            'id'    : f'e{index}'                ,
            'source': from_id                    ,
            'target': to_id                      ,
        }

        if predicate:
            data['label'] = predicate

        return {'data': data}

    # ═══════════════════════════════════════════════════════════════════════════
    # Layout and Style
    # ═══════════════════════════════════════════════════════════════════════════

    def _export_layout(self) -> Dict[str, Any]:                                  # Export layout configuration
        cfg = self.config
        layout = {
            'name': cfg.layout_name,
        }
        if cfg.layout_name == 'dagre':
            layout['rankDir'] = cfg.layout_direction
        return layout

    def _export_style(self) -> List[Dict[str, Any]]:                             # Export Cytoscape style definitions
        cfg = self.config
        return [
            {
                'selector': 'node',
                'style'   : {
                    'label'           : 'data(label)'       ,
                    'width'           : cfg.node_width      ,
                    'height'          : cfg.node_height     ,
                    'shape'           : cfg.node_shape      ,
                    'background-color': cfg.node_bg_color   ,
                    'border-color'    : cfg.node_border_color,
                    'border-width'    : cfg.node_border_width,
                    'font-size'       : cfg.font_size       ,
                    'text-valign'     : 'center'            ,
                    'text-halign'     : 'center'            ,
                },
            },
            {
                'selector': 'edge',
                'style'   : {
                    'width'             : cfg.edge_width      ,
                    'line-color'        : cfg.edge_color      ,
                    'target-arrow-color': cfg.edge_color      ,
                    'target-arrow-shape': cfg.edge_arrow_shape,
                    'curve-style'       : 'bezier'            ,
                },
            },
        ]

    def _build_stats(self) -> Dict[str, int]:                                    # Build graph statistics
        return {
            'nodeCount': len(self.nodes()),
            'edgeCount': len(self.edges()),
        }
