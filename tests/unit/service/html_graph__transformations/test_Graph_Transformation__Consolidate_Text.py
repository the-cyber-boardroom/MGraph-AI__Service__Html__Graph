from unittest                                                                                        import TestCase
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Consolidate_Text import Graph_Transformation__Consolidate_Text


class test_Graph_Transformation__Consolidate_Text(TestCase):

    @classmethod
    def setUpClass(cls):                                                                            # One-time setup for all tests
        cls.transformation = Graph_Transformation__Consolidate_Text()

    def test__init__(self):                                                                         # Test initialization and attributes
        with Graph_Transformation__Consolidate_Text() as _:
            assert _.name        == 'consolidate_text'
            assert _.description == 'Merge fragmented text nodes into single consolidated text (destructive)'

    def test_transform_dict__simple_bold(self):                                                     # Test: <p>This is <b>HTML</b> element</p>
        html_dict = { 'tag'      : 'p'                                                            ,
                      'children' : [ {'type': 'text', 'text': 'This is '}                         ,
                                     {'tag': 'b', 'children': [{'type': 'text', 'text': 'HTML'}]} ,
                                     {'type': 'text', 'text': ' element'}                         ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['tag']                    == 'p'
        assert len(result['children'])          == 1                                                # Should consolidate to single text node
        assert result['children'][0]['type']    == 'text'
        assert result['children'][0]['text']    == 'This is HTML element'

    def test_transform_dict__link_inside_paragraph(self):                                           # Test: <p>Click <a href="#">here</a> to continue</p>
        html_dict = { 'tag'      : 'p'                                                            ,
                      'children' : [ {'type': 'text', 'text': 'Click '}                           ,
                                     {'tag': 'a', 'children': [{'type': 'text', 'text': 'here'}]} ,
                                     {'type': 'text', 'text': ' to continue'}                     ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['children'][0]['text'] == 'Click here to continue'

    def test_transform_dict__nested_inline_tags(self):                                              # Test: <p>Text <b><i>nested</i></b> more</p>
        html_dict = { 'tag'      : 'p'                                                            ,
                      'children' : [ {'type': 'text', 'text': 'Text '}                            ,
                                     {'tag' : 'b', 'children': [
                                         {'tag': 'i', 'children': [
                                             {'type': 'text', 'text': 'nested'}
                                         ]}
                                     ]}                                                           ,
                                     {'type': 'text', 'text': ' more'}                            ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['children'][0]['text'] == 'Text nested more'

    def test_transform_dict__no_consolidation_needed(self):                                         # Test: element with only text child (no change needed)
        html_dict = { 'tag'      : 'p'                                                            ,
                      'children' : [{'type': 'text', 'text': 'Simple text'}]                      }

        result = self.transformation.transform_dict(html_dict)

        assert result['children'][0]['text'] == 'Simple text'                                       # Should remain unchanged

    def test_transform_dict__no_inline_tags(self):                                                  # Test: element with only non-inline children
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [ {'tag': 'p', 'children': [{'type': 'text', 'text': 'Para 1'}]},
                                     {'tag': 'p', 'children': [{'type': 'text', 'text': 'Para 2'}]}]}

        result = self.transformation.transform_dict(html_dict)

        assert len(result['children']) == 2                                                         # Structure preserved (no inline tags to consolidate)
        assert result['children'][0]['tag'] == 'p'
        assert result['children'][1]['tag'] == 'p'

    def test_transform_dict__empty_dict(self):                                                      # Test: empty input
        result = self.transformation.transform_dict({})
        assert result == {}

    def test_transform_dict__none_input(self):                                                      # Test: None input
        result = self.transformation.transform_dict(None)
        assert result is None

    def test_transform_dict__recursive_structure(self):                                             # Test: nested structure with consolidation at multiple levels
        html_dict = { 'tag'      : 'div'                                                          ,
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

        assert result['children'][0]['children'][0]['text'] == 'First bold text'                    # First paragraph consolidated
        assert result['children'][1]['children'][0]['text'] == 'Second italic text'                 # Second paragraph consolidated

    def test_transform_dict__multiple_inline_types(self):                                           # Test: <p>A <b>bold</b> and <i>italic</i> and <code>code</code></p>
        html_dict = { 'tag'      : 'p'                                                            ,
                      'children' : [ {'type': 'text', 'text': 'A '}                               ,
                                     {'tag': 'b', 'children': [{'type': 'text', 'text': 'bold'}]} ,
                                     {'type': 'text', 'text': ' and '}                            ,
                                     {'tag': 'i', 'children': [{'type': 'text', 'text': 'italic'}]},
                                     {'type': 'text', 'text': ' and '}                            ,
                                     {'tag': 'code', 'children': [{'type': 'text', 'text': 'code'}]},
                                     {'type': 'text', 'text': ' end'}                             ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['children'][0]['text'] == 'A bold and italic and code end'

    def test_transform_dict__span_with_text(self):                                                  # Test: <div>Text <span>inside span</span> outside</div>
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [ {'type': 'text', 'text': 'Text '}                            ,
                                     {'tag': 'span', 'children': [{'type': 'text', 'text': 'inside span'}]},
                                     {'type': 'text', 'text': ' outside'}                         ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['children'][0]['text'] == 'Text inside span outside'