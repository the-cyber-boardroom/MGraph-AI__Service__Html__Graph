from unittest                                                                                            import TestCase
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Text_Blocks_Only import Graph_Transformation__Text_Blocks_Only


class test_Graph_Transformation__Text_Blocks_Only(TestCase):

    @classmethod
    def setUpClass(cls):                                                                            # One-time setup for all tests
        cls.transformation = Graph_Transformation__Text_Blocks_Only()

    def test__init__(self):                                                                         # Test initialization and attributes
        with Graph_Transformation__Text_Blocks_Only() as _:
            assert _.name        == 'text_blocks_only'
            assert _.description == 'Show only elements containing direct text content'

    def test_transform_dict__simple_text_element(self):                                             # Test: element with direct text is preserved
        html_dict = { 'tag'      : 'p'                                                            ,
                      'children' : [{'type': 'text', 'text': 'Hello world'}]                      }

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'p'
        assert result['has_text'] is True
        assert result['children'][0]['text'] == 'Hello world'

    def test_transform_dict__empty_wrapper_removed(self):                                           # Test: purely structural elements with no text descendants removed
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [
                          {'tag': 'section', 'children': [
                              {'tag': 'article', 'children': []}                                    # Empty article
                          ]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'div'
        assert result['children'] == []                                                             # Empty structure removed

    def test_transform_dict__preserves_path_to_text(self):                                          # Test: structural ancestors of text-bearing elements preserved
        html_dict = { 'tag'      : 'body'                                                         ,
                      'children' : [
                          {'tag': 'div', 'children': [
                              {'tag': 'p', 'children': [
                                  {'type': 'text', 'text': 'Content'}
                              ]}
                          ]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'body'                                                              # Root preserved
        assert result['children'][0]['tag'] == 'div'                                                # Parent path preserved
        assert result['children'][0]['children'][0]['tag'] == 'p'                                   # Text-bearing element preserved
        assert result['children'][0]['children'][0]['has_text'] is True

    def test_transform_dict__mixed_content(self):                                                   # Test: mix of text-bearing and empty elements
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [
                          {'tag': 'header', 'children': []}                                       ,  # Empty - removed
                          {'tag': 'main', 'children': [
                              {'tag': 'p', 'children': [{'type': 'text', 'text': 'Main content'}]}
                          ]}                                                                      ,
                          {'tag': 'footer', 'children': []}                                         # Empty - removed
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert len(result['children']) == 1                                                         # Only main preserved
        assert result['children'][0]['tag'] == 'main'
        assert result['children'][0]['children'][0]['tag'] == 'p'

    def test_transform_dict__multiple_text_blocks(self):                                            # Test: multiple text-bearing elements preserved
        html_dict = { 'tag'      : 'article'                                                      ,
                      'children' : [
                          {'tag': 'h1', 'children': [{'type': 'text', 'text': 'Title'}]}          ,
                          {'tag': 'p', 'children': [{'type': 'text', 'text': 'Paragraph 1'}]}     ,
                          {'tag': 'p', 'children': [{'type': 'text', 'text': 'Paragraph 2'}]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert len(result['children']) == 3                                                         # All text-bearing elements preserved
        assert result['children'][0]['tag'] == 'h1'
        assert result['children'][0]['has_text'] is True
        assert result['children'][1]['tag'] == 'p'
        assert result['children'][2]['tag'] == 'p'

    def test_transform_dict__whitespace_not_text(self):                                             # Test: whitespace-only text is not considered content
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [
                          {'type': 'text', 'text': '   '}                                         ,  # Whitespace only
                          {'tag': 'p', 'children': [{'type': 'text', 'text': 'Real content'}]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'div'
        assert 'has_text' not in result or result.get('has_text') is not True                       # div itself has no meaningful text
        assert result['children'][0]['tag'] == 'p'                                                  # p preserved (has real text)

    def test_transform_dict__nested_text_blocks(self):                                              # Test: deeply nested text blocks
        html_dict = { 'tag'      : 'html'                                                         ,
                      'children' : [
                          {'tag': 'body', 'children': [
                              {'tag': 'main', 'children': [
                                  {'tag': 'article', 'children': [
                                      {'tag': 'section', 'children': [
                                          {'tag': 'p', 'children': [
                                              {'type': 'text', 'text': 'Deep text'}
                                          ]}
                                      ]}
                                  ]}
                              ]}
                          ]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'html'                                                              # Full path preserved
        p_element = result['children'][0]['children'][0]['children'][0]['children'][0]['children'][0]
        assert p_element['tag'] == 'p'
        assert p_element['has_text'] is True

    def test_transform_dict__empty_dict(self):                                                      # Test: empty input
        result = self.transformation.transform_dict({})
        assert result == {}

    def test_transform_dict__none_input(self):                                                      # Test: None input
        result = self.transformation.transform_dict(None)
        assert result is None

    def test_transform_dict__no_children(self):                                                     # Test: element with no children
        html_dict = {'tag': 'br'}

        result = self.transformation.transform_dict(html_dict)

        assert result == {'tag': 'br'}

    def test_transform_dict__sibling_branches(self):                                                # Test: some branches have text, others don't
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [
                          {'tag': 'nav', 'children': [                                              # Has text descendant
                              {'tag': 'a', 'children': [{'type': 'text', 'text': 'Link'}]}
                          ]}                                                                      ,
                          {'tag': 'aside', 'children': [                                            # No text
                              {'tag': 'div', 'children': []}
                          ]}                                                                      ,
                          {'tag': 'main', 'children': [                                             # Has text descendant
                              {'tag': 'p', 'children': [{'type': 'text', 'text': 'Content'}]}
                          ]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert len(result['children']) == 2                                                         # aside branch removed
        assert result['children'][0]['tag'] == 'nav'
        assert result['children'][1]['tag'] == 'main'

    def test_transform_dict__text_in_multiple_levels(self):                                         # Test: text at different nesting levels
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [
                          {'type': 'text', 'text': 'Top level text'}                              ,
                          {'tag': 'p', 'children': [
                              {'type': 'text', 'text': 'Nested text'}
                          ]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['has_text'] is True                                                           # div has direct text
        assert len(result['children']) == 2                                                         # Both preserved
        assert result['children'][0]['text'] == 'Top level text'
        assert result['children'][1]['tag'] == 'p'
        assert result['children'][1]['has_text'] is True

    def test_transform_dict__inline_elements_with_text(self):                                       # Test: inline elements with text are marked
        html_dict = { 'tag'      : 'p'                                                            ,
                      'children' : [
                          {'type': 'text', 'text': 'Before '}                                     ,
                          {'tag': 'strong', 'children': [{'type': 'text', 'text': 'bold'}]}       ,
                          {'type': 'text', 'text': ' after'}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['has_text'] is True                                                           # p has direct text
        assert result['children'][1]['tag'] == 'strong'
        assert result['children'][1]['has_text'] is True                                            # strong also has text

    def test_transform_dict__empty_text_nodes(self):                                                # Test: empty string text nodes
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [
                          {'type': 'text', 'text': ''}                                            ,  # Empty text
                          {'tag': 'span', 'children': []}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['children'] == []                                                             # Everything removed (no meaningful text)

    def test_transform_dict__preserves_text_node_content(self):                                     # Test: text node content is preserved exactly
        html_dict = { 'tag'      : 'pre'                                                          ,
                      'children' : [{'type': 'text', 'text': '  code\n    indented  '}]           }

        result = self.transformation.transform_dict(html_dict)

        assert result['has_text'] is True
        assert result['children'][0]['text'] == '  code\n    indented  '                            # Whitespace preserved in content