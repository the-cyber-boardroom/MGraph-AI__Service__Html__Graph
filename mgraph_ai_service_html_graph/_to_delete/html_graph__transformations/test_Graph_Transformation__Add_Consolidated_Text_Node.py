from unittest                                                                                                    import TestCase
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Add_Consolidated_Text_Node import Graph_Transformation__Add_Consolidated_Text_Node


class test_Graph_Transformation__Add_Consolidated_Text_Node(TestCase):

    @classmethod
    def setUpClass(cls):                                                                            # One-time setup for all tests
        cls.transformation = Graph_Transformation__Add_Consolidated_Text_Node()

    def test__init__(self):                                                                         # Test initialization and attributes
        with Graph_Transformation__Add_Consolidated_Text_Node() as _:
            assert _.name        == 'add_consolidated_text_node'
            assert _.description == 'Add consolidated text nodes as siblings (non-destructive)'

    def test_transform_dict__simple_bold(self):                                                     # Test: <p>This is <b>HTML</b> element</p>
        html_dict = { 'tag'      : 'body'                                                         ,
                      'children' : [
                          {'tag': 'p', 'children': [
                              {'type': 'text', 'text': 'This is '}                                ,
                              {'tag': 'b', 'children': [{'type': 'text', 'text': 'HTML'}]}        ,
                              {'type': 'text', 'text': ' element'}
                          ]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'body'
        assert len(result['children']) == 2                                                         # Original p + consolidated node

        original_p = result['children'][0]                                                          # Verify original structure preserved
        assert original_p['tag'] == 'p'
        assert len(original_p['children']) == 3                                                     # Still has 3 children

        consolidated = result['children'][1]                                                        # Verify consolidated node added
        assert consolidated['tag']        == 'consolidated_text'
        assert consolidated['type']       == 'synthetic'
        assert consolidated['source_tag'] == 'p'
        assert consolidated['text']       == 'This is HTML element'

    def test_transform_dict__link_inside_paragraph(self):                                           # Test: <p>Click <a href="#">here</a> to continue</p>
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [
                          {'tag': 'p', 'children': [
                              {'type': 'text', 'text': 'Click '}                                  ,
                              {'tag': 'a', 'children': [{'type': 'text', 'text': 'here'}]}        ,
                              {'type': 'text', 'text': ' to continue'}
                          ]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        consolidated = result['children'][1]
        assert consolidated['text'] == 'Click here to continue'
        assert consolidated['source_tag'] == 'p'

    def test_transform_dict__no_consolidation_needed(self):                                         # Test: element with only text child (no synthetic node added)
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [
                          {'tag': 'p', 'children': [{'type': 'text', 'text': 'Simple text'}]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert len(result['children']) == 1                                                         # No consolidated node added
        assert result['children'][0]['tag'] == 'p'

    def test_transform_dict__multiple_paragraphs(self):                                             # Test: multiple paragraphs each needing consolidation
        html_dict = { 'tag'      : 'article'                                                      ,
                      'children' : [
                          {'tag': 'p', 'children': [
                              {'type': 'text', 'text': 'First '}                                  ,
                              {'tag': 'strong', 'children': [{'type': 'text', 'text': 'bold'}]}   ,
                              {'type': 'text', 'text': ' text'}
                          ]}                                                                      ,
                          {'tag': 'p', 'children': [
                              {'type': 'text', 'text': 'Second '}                                 ,
                              {'tag': 'em', 'children': [{'type': 'text', 'text': 'italic'}]}     ,
                              {'type': 'text', 'text': ' text'}
                          ]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert len(result['children']) == 4                                                         # 2 original + 2 consolidated

        assert result['children'][0]['tag'] == 'p'                                                  # Original paragraphs preserved
        assert result['children'][1]['tag'] == 'p'

        assert result['children'][2]['tag']  == 'consolidated_text'                                 # Consolidated nodes at end
        assert result['children'][2]['text'] == 'First bold text'
        assert result['children'][3]['tag']  == 'consolidated_text'
        assert result['children'][3]['text'] == 'Second italic text'

    def test_transform_dict__empty_dict(self):                                                      # Test: empty input
        result = self.transformation.transform_dict({})
        assert result == {}

    def test_transform_dict__none_input(self):                                                      # Test: None input
        result = self.transformation.transform_dict(None)
        assert result is None

    def test_transform_dict__deeply_nested(self):                                                   # Test: deeply nested structure
        html_dict = { 'tag'      : 'html'                                                         ,
                      'children' : [
                          {'tag': 'body', 'children': [
                              {'tag': 'div', 'children': [
                                  {'tag': 'p', 'children': [
                                      {'type': 'text', 'text': 'Deep '}                           ,
                                      {'tag': 'b', 'children': [{'type': 'text', 'text': 'text'}]}
                                  ]}
                              ]}
                          ]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        div = result['children'][0]['children'][0]                                                  # Navigate to div level
        assert len(div['children']) == 2                                                            # p + consolidated

        assert div['children'][0]['tag'] == 'p'                                                     # Original p preserved
        assert div['children'][1]['tag'] == 'consolidated_text'                                     # Consolidated added
        assert div['children'][1]['text'] == 'Deep text'

    def test_transform_dict__whitespace_only_skipped(self):                                         # Test: whitespace-only text should not create consolidated node
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [
                          {'tag': 'p', 'children': [
                              {'type': 'text', 'text': '   '}                                     ,  # Whitespace only
                              {'tag': 'span', 'children': [{'type': 'text', 'text': '  '}]}           # Whitespace only
                          ]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert len(result['children']) == 1                                                         # No consolidated node (only whitespace)

    def test_transform_dict__preserves_original_children_order(self):                               # Test: original children order is preserved
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [
                          {'type': 'text', 'text': 'Plain text'}                                  ,
                          {'tag': 'p', 'children': [
                              {'type': 'text', 'text': 'Para '}                                   ,
                              {'tag': 'b', 'children': [{'type': 'text', 'text': 'bold'}]}
                          ]}                                                                      ,
                          {'tag': 'span', 'children': [{'type': 'text', 'text': 'span text'}]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['children'][0]         == {'type': 'text', 'text': 'Plain text'}              # Text preserved in position
        assert result['children'][1]['tag']  == 'p'                                                 # P preserved in position
        assert result['children'][2]['tag']  == 'span'                                              # Span preserved in position
        assert result['children'][3]['tag']  == 'consolidated_text'                                 # Consolidated at end
        assert result['children'][3]['text'] == 'Para bold'

    def test_transform_dict__synthetic_node_attributes(self):                                       # Test: verify all synthetic node attributes
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [
                          {'tag': 'h1', 'children': [
                              {'type': 'text', 'text': 'Title '}                                  ,
                              {'tag': 'small', 'children': [{'type': 'text', 'text': 'subtitle'}]}
                          ]}
                      ]}

        result = self.transformation.transform_dict(html_dict)

        consolidated = result['children'][1]

        assert consolidated['tag']        == 'consolidated_text'
        assert consolidated['type']       == 'synthetic'
        assert consolidated['source_tag'] == 'h1'
        assert consolidated['text']       == 'Title subtitle'
        assert consolidated['children']   == []