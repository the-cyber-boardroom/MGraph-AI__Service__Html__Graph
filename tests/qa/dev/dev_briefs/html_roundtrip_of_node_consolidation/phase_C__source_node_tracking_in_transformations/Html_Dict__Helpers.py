# ═══════════════════════════════════════════════════════════════════════════════
# Html_Dict__Helpers - Utility functions for Html_Dict manipulation
# Part of Phase C/E: Operations on Html_Dict using node_ids from tracking
# ═══════════════════════════════════════════════════════════════════════════════

from typing import Tuple, Optional, Dict, List


def find_node_by_id(node_dict: dict, target_id: str) -> Tuple[Optional[dict], Optional[dict], Optional[int]]:
    """Find a node by node_id in Html_Dict tree.

    Args:
        node_dict: Root of Html_Dict tree to search
        target_id: node_id to find

    Returns:
        Tuple of (node, parent, index_in_parent)
        Returns (None, None, None) if not found
    """
    if node_dict.get('node_id') == target_id:
        return (node_dict, None, None)

    for i, child in enumerate(node_dict.get('nodes', [])):
        if isinstance(child, dict):
            if child.get('node_id') == target_id:
                return (child, node_dict, i)
            result = find_node_by_id(child, target_id)
            if result[0] is not None:
                return result

    return (None, None, None)


def unwrap_element_in_dict(html_dict: dict, wrapper_node_id: str) -> bool:
    """Unwrap an element: replace it with its children in-place.

    Before: <div>Text <a>link</a> more</div>
    After:  <div>Text link more</div>

    Args:
        html_dict: Root of Html_Dict tree
        wrapper_node_id: node_id of element to unwrap

    Returns:
        True if unwrapped successfully, False otherwise
    """
    node, parent, index = find_node_by_id(html_dict, wrapper_node_id)

    if node is None or parent is None:
        return False

    if node.get('type') == 'TEXT':                                              # Can't unwrap text nodes
        return False

    wrapper_children = node.get('nodes', [])                                    # Get children of wrapper

    parent_nodes = parent.get('nodes', [])                                      # Remove wrapper from parent
    parent_nodes.pop(index)

    for i, child in enumerate(wrapper_children):                                # Insert wrapper's children at same position
        parent_nodes.insert(index + i, child)

    return True


def delete_node_by_id(html_dict: dict, node_id: str) -> bool:
    """Delete a node by node_id from Html_Dict tree.

    Args:
        html_dict: Root of Html_Dict tree
        node_id: node_id of node to delete

    Returns:
        True if deleted successfully, False otherwise
    """
    node, parent, index = find_node_by_id(html_dict, node_id)

    if node is None or parent is None:
        return False

    parent_nodes = parent.get('nodes', [])
    parent_nodes.pop(index)

    return True


def merge_adjacent_text_nodes(html_dict: dict) -> int:
    """Merge adjacent TEXT nodes in all nodes lists.

    Before: [TEXT "Hello ", TEXT "World"]
    After:  [TEXT "Hello World"]

    Args:
        html_dict: Root of Html_Dict tree (modified in-place)

    Returns:
        Number of merges performed
    """
    merge_count = 0
    nodes = html_dict.get('nodes', [])

    i = 0
    while i < len(nodes) - 1:
        current = nodes[i]
        next_node = nodes[i + 1]

        if (isinstance(current, dict) and isinstance(next_node, dict) and
            current.get('type') == 'TEXT' and next_node.get('type') == 'TEXT'):
            current['data'] = current.get('data', '') + next_node.get('data', '')
            nodes.pop(i + 1)
            merge_count += 1
        else:
            i += 1

    for child in nodes:                                                         # Recurse into children
        if isinstance(child, dict) and 'nodes' in child:
            merge_count += merge_adjacent_text_nodes(child)

    return merge_count


def collect_node_ids(html_dict: dict) -> set:
    """Collect all node_ids from Html_Dict tree.

    Args:
        html_dict: Root of Html_Dict tree

    Returns:
        Set of all node_id values found
    """
    node_ids = set()

    if 'node_id' in html_dict:
        node_ids.add(html_dict['node_id'])

    for child in html_dict.get('nodes', []):
        if isinstance(child, dict):
            node_ids.update(collect_node_ids(child))

    return node_ids


def html_dict_to_html(node_dict: dict) -> str:
    """Convert Html_Dict back to HTML string.

    Simple converter for testing - does not handle all edge cases.
    For production use Html_Dict__To__Html from osbot_utils.

    Args:
        node_dict: Html_Dict node

    Returns:
        HTML string
    """
    if node_dict.get('type') == 'TEXT':
        return node_dict.get('data', '')

    tag = node_dict.get('tag', '')
    if not tag:
        return ''

    attrs = node_dict.get('attrs', {})
    attrs_str = ''
    for key, value in attrs.items():
        attr_name = key.lstrip('_')                                             # Handle _class → class
        if value:
            attrs_str += f' {attr_name}="{value}"'
        else:
            attrs_str += f' {attr_name}'

    children_html = ''.join(html_dict_to_html(child)
                           for child in node_dict.get('nodes', [])
                           if isinstance(child, dict))

    void_elements = {'br', 'hr', 'img', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr'}
    if tag in void_elements:
        return f'<{tag}{attrs_str}>'

    return f'<{tag}{attrs_str}>{children_html}</{tag}>'


def unwrap_all_inline_elements(html_dict: dict, wrapper_mapping: Dict[str, dict]) -> int:
    """Unwrap all inline elements tracked in wrapper_mapping.

    Args:
        html_dict: Root of Html_Dict tree (modified in-place)
        wrapper_mapping: From Html_Use_Case__3__Source_Tracking

    Returns:
        Number of elements unwrapped
    """
    unwrap_count = 0

    for wrapper_id in wrapper_mapping.keys():
        if unwrap_element_in_dict(html_dict, wrapper_id):
            unwrap_count += 1

    return unwrap_count


def clean_html_from_tracking(html_dict: dict, wrapper_mapping: Dict[str, dict]) -> str:
    """Full workflow: unwrap inline elements and produce clean HTML.

    Args:
        html_dict: Root of Html_Dict tree (will be modified!)
        wrapper_mapping: From Html_Use_Case__3__Source_Tracking

    Returns:
        Clean HTML string with inline elements removed
    """
    unwrap_all_inline_elements(html_dict, wrapper_mapping)
    merge_adjacent_text_nodes(html_dict)
    return html_dict_to_html(html_dict)