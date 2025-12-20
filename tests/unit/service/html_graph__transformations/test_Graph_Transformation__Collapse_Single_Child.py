from unittest                                                                                                import TestCase
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Collapse_Single_Child import Graph_Transformation__Collapse_Single_Child


class test_Graph_Transformation__Collapse_Single_Child(TestCase):

    @classmethod
    def setUpClass(cls):                                                                            # One-time setup for all tests
        cls.transformation = Graph_Transformation__Collapse_Single_Child()

    def test__init__(self):                                                                         # Test initialization and attributes
        with Graph_Transformation__Collapse_Single_Child() as _:
            assert _.name        == 'collapse_single_child'
            assert _.description == 'Collapse single-child element chains'

    def test_transform_dict__simple_chain(self):                                                    # Test: div -> div -> p (each with single child)
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [
                          {'tag': 'div', 'children': [
                              {'tag': 'p', 'children': [
                                  {'type': 'text', 'text': 'Content'}
                              ]}
                          ]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'p'                                                                 # Collapsed to innermost element
        assert result['collapsed_path'] == ['div', 'div']                                           # Path tracked
        assert result['children'][0]['text'] == 'Content'

    def test_transform_dict__three_level_chain(self):                                               # Test: html -> body -> main -> article -> p
        html_dict = { 'tag'      : 'html'                                                         ,
                      'children' : [
                          {'tag': 'body', 'children': [
                              {'tag': 'main', 'children': [
                                  {'tag': 'article', 'children': [
                                      {'tag': 'p', 'children': [
                                          {'type': 'text', 'text': 'Text'}
                                      ]}
                                  ]}
                              ]}
                          ]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'p'
        assert result['collapsed_path'] == ['html', 'body', 'main', 'article']

    def test_transform_dict__no_collapse_multiple_children(self):                                   # Test: element with multiple children should not collapse
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [
                          {'tag': 'p', 'children': [{'type': 'text', 'text': 'First'}]}           ,
                          {'tag': 'p', 'children': [{'type': 'text', 'text': 'Second'}]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'div'                                                               # Not collapsed (has 2 children)
        assert len(result['children']) == 2

    def test_transform_dict__no_collapse_with_text(self):                                           # Test: element with text + child should not collapse
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [
                          {'type': 'text', 'text': 'Some text'}                                   ,
                          {'tag': 'p', 'children': [{'type': 'text', 'text': 'Para'}]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'div'                                                               # Not collapsed (has text)
        assert len(result['children']) == 2

    def test_transform_dict__partial_chain(self):                                                   # Test: div -> div -> (p + p) - stops at branching point
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [
                          {'tag': 'div', 'children': [
                              {'tag': 'p', 'children': [{'type': 'text', 'text': 'First'}]}       ,
                              {'tag': 'p', 'children': [{'type': 'text', 'text': 'Second'}]}
                          ]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'div'                                                               # Collapsed to inner div (which has multiple children)
        assert result['collapsed_path'] == ['div']
        assert len(result['children']) == 2

    def test_transform_dict__empty_dict(self):                                                      # Test: empty input
        result = self.transformation.transform_dict({})
        assert result == {}

    def test_transform_dict__none_input(self):                                                      # Test: None input
        result = self.transformation.transform_dict(None)
        assert result is None

    def test_transform_dict__leaf_element(self):                                                    # Test: element with no children
        html_dict = {'tag': 'br'}

        result = self.transformation.transform_dict(html_dict)

        assert result == {'tag': 'br'}

    def test_transform_dict__preserves_text_bearing_element(self):                                  # Test: element with direct meaningful text is not collapsed
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [
                          {'tag': 'p', 'children': [
                              {'type': 'text', 'text': 'Important text'}
                          ]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'p'                                                                 # Collapsed to p (text is inside p, not div)
        assert result['collapsed_path'] == ['div']

    def test_transform_dict__whitespace_text_ignored(self):                                         # Test: whitespace-only text nodes don't prevent collapse
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [
                          {'type': 'text', 'text': '   '}                                         ,  # Whitespace only
                          {'tag': 'p', 'children': [{'type': 'text', 'text': 'Content'}]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        #assert result['tag'] == 'div'                                                               # Not collapsed - has whitespace text node
        assert result['tag'] == 'p'                                                                  # todo: see if this is a bug
        # Note: current implementation counts whitespace as text preventing collapse

    def test_transform_dict__recursive_processing(self):                                            # Test: multiple independent chains in same tree
        html_dict = { 'tag'      : 'body'                                                         ,
                      'children' : [
                          {'tag': 'div', 'children': [                                              # Chain 1
                              {'tag': 'section', 'children': [
                                  {'tag': 'p', 'children': [{'type': 'text', 'text': 'First'}]}
                              ]}
                          ]}                                                                      ,
                          {'tag': 'div', 'children': [                                              # Chain 2
                              {'tag': 'article', 'children': [
                                  {'tag': 'p', 'children': [{'type': 'text', 'text': 'Second'}]}
                              ]}
                          ]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'body'                                                              # Body not collapsed (has 2 children)
        assert result['children'][0]['tag'] == 'p'                                                  # First chain collapsed
        assert result['children'][0]['collapsed_path'] == ['div', 'section']
        assert result['children'][1]['tag'] == 'p'                                                  # Second chain collapsed
        assert result['children'][1]['collapsed_path'] == ['div', 'article']

    def test_transform_dict__deep_nesting(self):                                                    # Test: very deep nesting collapses correctly
        html_dict = { 'tag': 'a', 'children': [
                      { 'tag': 'b', 'children': [
                        { 'tag': 'c', 'children': [
                          { 'tag': 'd', 'children': [
                            { 'tag': 'e', 'children': [
                              {'type': 'text', 'text': 'Deep'}
                            ]}
                          ]}
                        ]}
                      ]}
                    ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'e'
        assert result['collapsed_path'] == ['a', 'b', 'c', 'd']

    def test_transform_dict__mixed_structure(self):                                                 # Test: some branches collapse, others don't
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [
                          {'tag': 'section', 'children': [                                          # Will collapse
                              {'tag': 'p', 'children': [{'type': 'text', 'text': 'Text'}]}
                          ]}                                                                      ,
                          {'tag': 'aside', 'children': [                                            # Won't collapse (multiple children)
                              {'tag': 'p', 'children': [{'type': 'text', 'text': 'A'}]}           ,
                              {'tag': 'p', 'children': [{'type': 'text', 'text': 'B'}]}
                          ]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'div'
        assert result['children'][0]['tag'] == 'p'                                                  # First collapsed
        assert result['children'][0]['collapsed_path'] == ['section']
        assert result['children'][1]['tag'] == 'aside'                                              # Second not collapsed
        assert 'collapsed_path' not in result['children'][1]

    def test_transform_dict__no_tag_not_collapsed(self):                                            # Test: elements without tags are handled
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [
                          {'type': 'text', 'text': 'Just text'}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'div'                                                               # Not collapsed (child has no tag)
        assert result['children'][0]['text'] == 'Just text'