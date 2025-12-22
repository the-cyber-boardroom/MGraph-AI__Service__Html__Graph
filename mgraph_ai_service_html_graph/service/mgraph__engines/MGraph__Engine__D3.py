# MGraph Engine - D3 (Force-Directed)
#
# Converts MGraph to D3.js compatible JSON format.
# Output structure: { nodes: [...], links: [...], config: {...} }

from typing                                                                                     import Dict, List, Any
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__D3    import MGraph__Engine__Config__D3
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Base                  import MGraph__Engine__Base


class MGraph__Engine__D3(MGraph__Engine__Base):      # D3 JSON format exporter
    config: MGraph__Engine__Config__D3


    def export(self) -> Dict[str, Any]:                                          # Export MGraph to D3 JSON
        result = {
            'nodes' : self._export_nodes() ,
            'links' : self._export_links() ,
            'config': self._export_config(),
        }
        if self.config.include_stats:
            result['stats'] = self._build_stats()
        return result

    # ═══════════════════════════════════════════════════════════════════════════
    # Node Export
    # ═══════════════════════════════════════════════════════════════════════════

    def _export_nodes(self) -> List[Dict[str, Any]]:                             # Convert all nodes to D3 format
        nodes = []
        for node in self.nodes():
            node_data = self._format_node(node)
            if node_data:
                nodes.append(node_data)
        return nodes

    def _format_node(self, node) -> Dict[str, Any]:                              # Format single node for D3
        node_id = self.node_id_str(node)
        path    = self.node_path(node)
        value   = self.node_value(node)

        label = value or path or node_id[:8]                                     # Build label
        label = self.truncate(label, self.config.max_label_len)

        node_data = {
            'id'    : node_id                    ,
            'label' : label                      ,
            'radius': self.config.node_radius    ,
        }

        if self.config.include_types:                                            # Add type info if configured
            node_data['nodeType'] = self._get_node_type(node)

        if path:                                                                 # Add path if present
            node_data['path'] = path

        color = self.get_node_style(node, 'color')                               # Add styling metadata
        if color:
            node_data['color'] = color

        group = self.get_node_style(node, 'group')
        if group:
            node_data['group'] = group

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
    # Link Export
    # ═══════════════════════════════════════════════════════════════════════════

    def _export_links(self) -> List[Dict[str, Any]]:                             # Convert all edges to D3 links
        links = []
        for edge in self.edges():
            link_data = self._format_link(edge)
            if link_data:
                links.append(link_data)
        return links

    def _format_link(self, edge) -> Dict[str, Any]:                              # Format single edge for D3
        from_id   = self.edge_from_id(edge)
        to_id     = self.edge_to_id(edge)
        predicate = self.edge_predicate(edge)

        link_data = {
            'source'  : from_id                     ,
            'target'  : to_id                       ,
            'distance': self.config.link_distance   ,
        }

        if predicate:
            link_data['label'] = predicate

        return link_data

    # ═══════════════════════════════════════════════════════════════════════════
    # Config and Stats
    # ═══════════════════════════════════════════════════════════════════════════

    def _export_config(self) -> Dict[str, Any]:                                  # Export D3 simulation config
        cfg = self.config
        return {
            'chargeStrength' : cfg.charge_strength  ,
            'linkDistance'   : cfg.link_distance    ,
            'collisionRadius': cfg.collision_radius ,
            'centerStrength' : cfg.center_strength  ,
        }

    def _build_stats(self) -> Dict[str, int]:                                    # Build graph statistics
        return {
            'nodeCount': len(self.nodes()),
            'linkCount': len(self.edges()),
        }
