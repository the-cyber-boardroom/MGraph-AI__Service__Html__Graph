# MGraph Engine - Tree
#
# Converts MGraph to tree representation (text, JSON, or nested dict).
# Performs depth-first traversal from root nodes.

import json
from typing                                                                                     import Dict, List, Any, Optional, Set
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Tree  import MGraph__Engine__Config__Tree
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Base                  import MGraph__Engine__Base



class MGraph__Engine__Tree(MGraph__Engine__Base):      # Tree view exporter
    config: MGraph__Engine__Config__Tree

    def export(self) -> Any:                                                     # Export MGraph to tree format
        output_format = self.config.output_format
        if output_format == 'text':
            return self._export_text()
        elif output_format == 'json':
            return self._export_json()
        elif output_format == 'nested_dict':
            return self._export_nested_dict()
        else:
            return self._export_text()

    # ═══════════════════════════════════════════════════════════════════════════
    # Text Export
    # ═══════════════════════════════════════════════════════════════════════════

    def _export_text(self) -> str:                                               # Export as text tree
        lines   = []
        roots   = self._find_roots()
        visited = set()

        for i, root in enumerate(roots):
            is_last = (i == len(roots) - 1)
            self._render_text_node(root, '', is_last, lines, visited)

        return '\n'.join(lines)

    def _render_text_node(self, node, prefix: str, is_last: bool,                # Render node as text
                          lines: List[str], visited: Set[str]) -> None:
        node_id = self.node_id_str(node)

        if node_id in visited:                                                   # Avoid cycles
            return
        visited.add(node_id)

        cfg   = self.config
        label = self._node_label(node)

        if cfg.tree_chars:                                                       # Build line with tree characters
            connector = cfg.prefix_leaf if is_last else cfg.prefix_branch
            line      = f'{prefix}{connector}{label}'
        else:
            indent = cfg.indent_char * cfg.indent_size * (len(prefix) // 4)
            line   = f'{indent}{label}'

        lines.append(line)

        children = self._get_children(node)                                      # Recurse into children
        for i, child in enumerate(children):
            child_is_last = (i == len(children) - 1)
            if cfg.tree_chars:
                child_prefix = prefix + (cfg.prefix_space if is_last else cfg.prefix_pipe)
            else:
                child_prefix = prefix + (cfg.indent_char * cfg.indent_size)
            self._render_text_node(child, child_prefix, child_is_last, lines, visited)

    # ═══════════════════════════════════════════════════════════════════════════
    # JSON Export
    # ═══════════════════════════════════════════════════════════════════════════

    def _export_json(self) -> str:                                               # Export as JSON string
        tree_data = self._export_nested_dict()
        indent    = None if self.config.compact_json else 2
        return json.dumps(tree_data, indent=indent)

    def _export_nested_dict(self) -> Dict[str, Any]:                             # Export as nested dictionary
        roots   = self._find_roots()
        visited = set()

        tree = {
            'roots': [self._build_tree_node(root, visited) for root in roots],
        }

        if self.config.include_stats:
            tree['stats'] = {
                'nodeCount': len(self.nodes()),
                'edgeCount': len(self.edges()),
                'rootCount': len(roots),
            }

        return tree

    def _build_tree_node(self, node, visited: Set[str]) -> Dict[str, Any]:       # Build tree node recursively
        node_id = self.node_id_str(node)

        if node_id in visited:                                                   # Avoid cycles
            return {'id': node_id, 'label': '[circular ref]', 'children': []}
        visited.add(node_id)

        path  = self.node_path(node)
        value = self.node_value(node)
        label = self._node_label(node)

        tree_node = {
            'label': label,
        }

        if self.config.show_node_ids:
            tree_node['id'] = node_id

        if path:
            tree_node['path'] = path

        if value and value != label:
            tree_node['value'] = value

        children = self._get_children(node)                                      # Add children
        if children:
            tree_node['children'] = [
                self._build_tree_node(child, visited) for child in children
            ]

        return tree_node

    # ═══════════════════════════════════════════════════════════════════════════
    # Tree Utilities
    # ═══════════════════════════════════════════════════════════════════════════

    def _node_label(self, node) -> str:                                          # Build node label
        path  = self.node_path(node)
        value = self.node_value(node)

        if value:
            label = value
        elif path:
            label = path
        else:
            label = self.node_id_str(node)[:8]

        return self.truncate(label, self.config.max_label_len)

    def _find_roots(self) -> List:                                               # Find root nodes (no incoming edges)
        has_parent = set()
        for edge in self.edges():
            to_id = self.edge_to_id(edge)
            has_parent.add(to_id)

        roots = []
        for node in self.nodes():
            node_id = self.node_id_str(node)
            if node_id not in has_parent:
                roots.append(node)

        if not roots and self.nodes():                                           # Fallback: use first node
            roots = [self.nodes()[0]]

        return roots

    def _get_children(self, node) -> List:                                       # Get child nodes
        node_id  = self.node_id_str(node)
        children = []
        node_map = {self.node_id_str(n): n for n in self.nodes()}

        for edge in self.edges():
            from_id = self.edge_from_id(edge)
            if from_id == node_id:
                to_id = self.edge_to_id(edge)
                if to_id in node_map:
                    children.append(node_map[to_id])

        return children