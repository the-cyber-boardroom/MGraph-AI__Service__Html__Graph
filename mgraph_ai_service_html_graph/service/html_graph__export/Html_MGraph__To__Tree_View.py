# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Tree View Exporter
# Converts Html_MGraph to hierarchical tree structure
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                               import Dict, Any, List, Optional
from osbot_utils.decorators.methods.cache_on_self                                         import cache_on_self
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Export__Base    import Html_MGraph__Export__Base


class Schema__Tree_Node(Dict):                                                            # Tree node structure
    """Tree node with id, value, and children grouped by type"""
    pass


class Html_MGraph__To__Tree_View(Html_MGraph__Export__Base):                              # Exports Html_MGraph as tree view

    def export(self) -> Any:                                                              # Export main method - returns tree or uses MGraph export
        return self.export_tree()

    def export_tree(self) -> Dict[str, Any]:                                              # Export as hierarchical tree structure
        if not self.html_mgraph:
            return {}

        root_id = self.html_mgraph.root_id()
        if not root_id:
            return {}

        return self._build_tree_node(str(root_id))

    def export_tree__as_text(self) -> str:                                                # Export tree as formatted text
        tree = self.export_tree()
        return self._format_tree_as_text(tree)

    # ═══════════════════════════════════════════════════════════════════════════
    # Tree Building
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_tree_node(self, node_id: str) -> Dict[str, Any]:                           # Build tree node with children grouped by type
        tag   = self.html_mgraph.get_tag(node_id) or node_id
        attrs = self.html_mgraph.get_attributes(node_id) or {}

        tree_node = {
            'id'       : node_id ,
            'value'    : tag     ,
            'children' : {}
        }

        # Add tag as child
        if tag:
            tree_node['children']['tag'] = [{'id': f'{node_id}_tag', 'value': tag, 'children': {}}]

        # Add attributes as children
        attr_children = []
        for attr_name, attr_value in attrs.items():
            attr_children.append({
                'id'       : f'{node_id}_attr_{attr_name}' ,
                'value'    : f'{attr_name}={attr_value}'   ,
                'children' : {}
            })
        if attr_children:
            tree_node['children']['attr'] = attr_children

        # Add text content
        text_content = self._get_direct_text(node_id)
        if text_content:
            tree_node['children']['text'] = [{'id': f'{node_id}_text', 'value': text_content, 'children': {}}]

        # Add child elements recursively
        element_children = self._get_element_children(node_id)
        if element_children:
            child_trees = []
            for child_id in element_children:
                child_trees.append(self._build_tree_node(child_id))
            tree_node['children']['child'] = child_trees

        return tree_node

    def _get_element_children(self, node_id: str) -> List[str]:                           # Get child element node IDs
        children = []

        # Try body graph first
        if self.html_mgraph.body_graph:
            from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id import Node_Id
            body_children = self.html_mgraph.body_graph.get_element_children(Node_Id(node_id))
            children.extend([str(c) for c in body_children])

        # Then head graph
        if not children and self.html_mgraph.head_graph:
            from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id import Node_Id
            head_children = self.html_mgraph.head_graph.get_element_children(Node_Id(node_id))
            children.extend([str(c) for c in head_children])

        return children

    def _get_direct_text(self, node_id: str) -> Optional[str]:                            # Get direct text content for element
        if self.html_mgraph.body_graph:
            from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id import Node_Id
            text = self.html_mgraph.body_graph.get_text_content(Node_Id(node_id))
            if text:
                return text

        if self.html_mgraph.head_graph:
            from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id import Node_Id
            text = self.html_mgraph.head_graph.get_text_content(Node_Id(node_id))
            if text:
                return text

        return None

    # ═══════════════════════════════════════════════════════════════════════════
    # Text Formatting
    # ═══════════════════════════════════════════════════════════════════════════

    def _format_tree_as_text(self, tree: Dict[str, Any], indent: int = 0) -> str:         # Format tree as indented text
        if not tree:
            return ''

        lines    = []
        prefix   = '    ' * indent
        node_id  = tree.get('id', '')
        children = tree.get('children', {})

        lines.append(f'{prefix}{node_id}')

        for child_type in ['tag', 'attr', 'text', 'child']:                               # Ordered child types
            child_list = children.get(child_type, [])
            if child_list:
                lines.append(f'{prefix}    {child_type}:')
                for child in child_list:
                    if child_type == 'child':                                             # Recursive for element children
                        child_text = self._format_tree_as_text(child, indent + 2)
                        lines.append(child_text)
                    else:
                        lines.append(f'{prefix}        {child.get("value", "")}')

        return '\n'.join(lines)