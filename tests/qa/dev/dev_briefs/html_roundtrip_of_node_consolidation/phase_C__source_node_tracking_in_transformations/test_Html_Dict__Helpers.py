# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Html_Dict__Helpers - Utility functions for Html_Dict manipulation
# ═══════════════════════════════════════════════════════════════════════════════

from unittest           import TestCase
from Html_Dict__Helpers import (find_node_by_id            ,
                                unwrap_element_in_dict     ,
                                delete_node_by_id          ,
                                merge_adjacent_text_nodes  ,
                                collect_node_ids           ,
                                html_dict_to_html          ,
                                unwrap_all_inline_elements ,
                                clean_html_from_tracking   )


class test_Html_Dict__Helpers(TestCase):

    # ═══════════════════════════════════════════════════════════════════════════
    # find_node_by_id Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_find_node_by_id__finds_root(self):
        html_dict = {'tag': 'div', 'node_id': 'root_001', 'nodes': []}

        node, parent, index = find_node_by_id(html_dict, 'root_001')

        assert node   == html_dict
        assert parent is None
        assert index  is None

    def test_find_node_by_id__finds_child(self):
        html_dict = {'tag': 'div', 'node_id': 'root_001', 'nodes': [
            {'tag': 'p', 'node_id': 'p_001', 'nodes': []}
        ]}

        node, parent, index = find_node_by_id(html_dict, 'p_001')

        assert node['node_id'] == 'p_001'
        assert parent == html_dict
        assert index == 0

    def test_find_node_by_id__finds_nested(self):
        html_dict = {'tag': 'div', 'node_id': 'root', 'nodes': [
            {'tag': 'p', 'node_id': 'p_001', 'nodes': [
                {'tag': 'span', 'node_id': 'span_001', 'nodes': []}
            ]}
        ]}

        node, parent, index = find_node_by_id(html_dict, 'span_001')

        assert node['node_id'] == 'span_001'
        assert parent['node_id'] == 'p_001'
        assert index == 0

    def test_find_node_by_id__not_found(self):
        html_dict = {'tag': 'div', 'node_id': 'root', 'nodes': []}

        node, parent, index = find_node_by_id(html_dict, 'nonexistent')

        assert node   is None
        assert parent is None
        assert index  is None

    # ═══════════════════════════════════════════════════════════════════════════
    # unwrap_element_in_dict Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_unwrap_element__simple(self):
        html_dict = {'tag': 'div', 'node_id': 'div_001', 'nodes': [
            {'tag': 'b', 'node_id': 'b_001', 'nodes': [
                {'type': 'TEXT', 'data': 'bold', 'node_id': 'text_001'}
            ]}
        ]}

        result = unwrap_element_in_dict(html_dict, 'b_001')

        assert result is True
        assert len(html_dict['nodes']) == 1
        assert html_dict['nodes'][0]['type'] == 'TEXT'
        assert html_dict['nodes'][0]['data'] == 'bold'

    def test_unwrap_element__preserves_siblings(self):
        html_dict = {'tag': 'div', 'node_id': 'div_001', 'nodes': [
            {'type': 'TEXT', 'data': 'before ', 'node_id': 'text_001'},
            {'tag': 'b', 'node_id': 'b_001', 'nodes': [
                {'type': 'TEXT', 'data': 'bold', 'node_id': 'text_002'}
            ]},
            {'type': 'TEXT', 'data': ' after', 'node_id': 'text_003'}
        ]}

        result = unwrap_element_in_dict(html_dict, 'b_001')

        assert result is True
        assert len(html_dict['nodes']) == 3
        assert html_dict['nodes'][0]['data'] == 'before '
        assert html_dict['nodes'][1]['data'] == 'bold'
        assert html_dict['nodes'][2]['data'] == ' after'

    def test_unwrap_element__not_found(self):
        html_dict = {'tag': 'div', 'node_id': 'div_001', 'nodes': []}

        result = unwrap_element_in_dict(html_dict, 'nonexistent')

        assert result is False

    def test_unwrap_element__cannot_unwrap_text(self):
        html_dict = {'tag': 'div', 'node_id': 'div_001', 'nodes': [
            {'type': 'TEXT', 'data': 'hello', 'node_id': 'text_001'}
        ]}

        result = unwrap_element_in_dict(html_dict, 'text_001')

        assert result is False

    # ═══════════════════════════════════════════════════════════════════════════
    # delete_node_by_id Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_delete_node__simple(self):
        html_dict = {'tag': 'div', 'node_id': 'div_001', 'nodes': [
            {'type': 'TEXT', 'data': 'hello', 'node_id': 'text_001'}
        ]}

        result = delete_node_by_id(html_dict, 'text_001')

        assert result is True
        assert len(html_dict['nodes']) == 0

    def test_delete_node__not_found(self):
        html_dict = {'tag': 'div', 'node_id': 'div_001', 'nodes': []}

        result = delete_node_by_id(html_dict, 'nonexistent')

        assert result is False

    # ═══════════════════════════════════════════════════════════════════════════
    # merge_adjacent_text_nodes Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_merge_adjacent__two_text_nodes(self):
        html_dict = {'tag': 'div', 'node_id': 'div_001', 'nodes': [
            {'type': 'TEXT', 'data': 'Hello ', 'node_id': 'text_001'},
            {'type': 'TEXT', 'data': 'World', 'node_id': 'text_002'}
        ]}

        count = merge_adjacent_text_nodes(html_dict)

        assert count == 1
        assert len(html_dict['nodes']) == 1
        assert html_dict['nodes'][0]['data'] == 'Hello World'

    def test_merge_adjacent__three_text_nodes(self):
        html_dict = {'tag': 'div', 'node_id': 'div_001', 'nodes': [
            {'type': 'TEXT', 'data': 'A', 'node_id': 'text_001'},
            {'type': 'TEXT', 'data': 'B', 'node_id': 'text_002'},
            {'type': 'TEXT', 'data': 'C', 'node_id': 'text_003'}
        ]}

        count = merge_adjacent_text_nodes(html_dict)

        assert count == 2
        assert len(html_dict['nodes']) == 1
        assert html_dict['nodes'][0]['data'] == 'ABC'

    def test_merge_adjacent__non_adjacent(self):
        html_dict = {'tag': 'div', 'node_id': 'div_001', 'nodes': [
            {'type': 'TEXT', 'data': 'A', 'node_id': 'text_001'},
            {'tag': 'br', 'node_id': 'br_001', 'nodes': []},
            {'type': 'TEXT', 'data': 'B', 'node_id': 'text_002'}
        ]}

        count = merge_adjacent_text_nodes(html_dict)

        assert count == 0
        assert len(html_dict['nodes']) == 3

    def test_merge_adjacent__recursive(self):
        html_dict = {'tag': 'div', 'node_id': 'div_001', 'nodes': [
            {'tag': 'p', 'node_id': 'p_001', 'nodes': [
                {'type': 'TEXT', 'data': 'A', 'node_id': 'text_001'},
                {'type': 'TEXT', 'data': 'B', 'node_id': 'text_002'}
            ]}
        ]}

        count = merge_adjacent_text_nodes(html_dict)

        assert count == 1
        assert html_dict['nodes'][0]['nodes'][0]['data'] == 'AB'

    # ═══════════════════════════════════════════════════════════════════════════
    # collect_node_ids Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_collect_node_ids__simple(self):
        html_dict = {'tag': 'div', 'node_id': 'div_001', 'nodes': [
            {'type': 'TEXT', 'data': 'hello', 'node_id': 'text_001'}
        ]}

        ids = collect_node_ids(html_dict)

        assert ids == {'div_001', 'text_001'}

    def test_collect_node_ids__nested(self):
        html_dict = {'tag': 'div', 'node_id': 'div_001', 'nodes': [
            {'tag': 'p', 'node_id': 'p_001', 'nodes': [
                {'type': 'TEXT', 'data': 'hello', 'node_id': 'text_001'}
            ]}
        ]}

        ids = collect_node_ids(html_dict)

        assert ids == {'div_001', 'p_001', 'text_001'}

    # ═══════════════════════════════════════════════════════════════════════════
    # html_dict_to_html Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_html_dict_to_html__simple_element(self):
        html_dict = {'tag': 'div', 'node_id': 'div_001', 'attrs': {}, 'nodes': []}

        html = html_dict_to_html(html_dict)

        assert html == '<div></div>'

    def test_html_dict_to_html__with_text(self):
        html_dict = {'tag': 'div', 'node_id': 'div_001', 'attrs': {}, 'nodes': [
            {'type': 'TEXT', 'data': 'Hello', 'node_id': 'text_001'}
        ]}

        html = html_dict_to_html(html_dict)

        assert html == '<div>Hello</div>'

    def test_html_dict_to_html__with_attrs(self):
        html_dict = {'tag': 'div', 'node_id': 'div_001', 'attrs': {'_class': 'test'}, 'nodes': []}

        html = html_dict_to_html(html_dict)

        assert html == '<div class="test"></div>'

    def test_html_dict_to_html__void_element(self):
        html_dict = {'tag': 'br', 'node_id': 'br_001', 'attrs': {}, 'nodes': []}

        html = html_dict_to_html(html_dict)

        assert html == '<br>'

    def test_html_dict_to_html__nested(self):
        html_dict = {'tag': 'div', 'node_id': 'div_001', 'attrs': {}, 'nodes': [
            {'tag': 'p', 'node_id': 'p_001', 'attrs': {}, 'nodes': [
                {'type': 'TEXT', 'data': 'Hello', 'node_id': 'text_001'}
            ]}
        ]}

        html = html_dict_to_html(html_dict)

        assert html == '<div><p>Hello</p></div>'

    # ═══════════════════════════════════════════════════════════════════════════
    # unwrap_all_inline_elements Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_unwrap_all__multiple_wrappers(self):
        html_dict = {'tag': 'div', 'node_id': 'div_001', 'nodes': [
            {'type': 'TEXT', 'data': 'Start ', 'node_id': 'text_001'},
            {'tag': 'a', 'node_id': 'a_001', 'nodes': [
                {'type': 'TEXT', 'data': 'link', 'node_id': 'text_002'}
            ]},
            {'type': 'TEXT', 'data': ' middle ', 'node_id': 'text_003'},
            {'tag': 'b', 'node_id': 'b_001', 'nodes': [
                {'type': 'TEXT', 'data': 'bold', 'node_id': 'text_004'}
            ]},
            {'type': 'TEXT', 'data': ' end', 'node_id': 'text_005'}
        ]}

        wrapper_mapping = {
            'a_001': {'parent_id': 'div_001', 'child_id': 'text_002'},
            'b_001': {'parent_id': 'div_001', 'child_id': 'text_004'}
        }

        count = unwrap_all_inline_elements(html_dict, wrapper_mapping)

        assert count == 2

        # All nodes should now be TEXT
        for node in html_dict['nodes']:
            assert node.get('type') == 'TEXT' or node.get('tag') is None

    # ═══════════════════════════════════════════════════════════════════════════
    # clean_html_from_tracking Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_clean_html__full_workflow(self):
        html_dict = {'tag': 'p', 'node_id': 'p_001', 'attrs': {}, 'nodes': [
            {'type': 'TEXT', 'data': 'Hello ', 'node_id': 'text_001'},
            {'tag': 'b', 'node_id': 'b_001', 'attrs': {}, 'nodes': [
                {'type': 'TEXT', 'data': 'World', 'node_id': 'text_002'}
            ]},
            {'type': 'TEXT', 'data': '!', 'node_id': 'text_003'}
        ]}

        wrapper_mapping = {
            'b_001': {'parent_id': 'p_001', 'child_id': 'text_002'}
        }

        html = clean_html_from_tracking(html_dict, wrapper_mapping)

        assert '<b>' not in html
        assert 'Hello World!' in html