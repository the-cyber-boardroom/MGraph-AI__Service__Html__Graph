from unittest                                                                                              import TestCase
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Strip_Inline_Tags import Graph_Transformation__Strip_Inline_Tags


class test_Graph_Transformation__Strip_Inline_Tags(TestCase):

    @classmethod
    def setUpClass(cls):                                                                            # One-time setup for all tests
        cls.transformation = Graph_Transformation__Strip_Inline_Tags()

    def test__init__(self):                                                                         # Test initialization and attributes
        with Graph_Transformation__Strip_Inline_Tags() as _:
            assert _.name        == 'strip_inline_tags'
            assert _.description == 'Remove inline formatting tags, preserve text content'

    def test_transform_dict__simple_link(self):                                                     # Test: <p>Click <a href="#">here</a> to continue</p>
        html_dict = { 'tag'      : 'p'                                                            ,
                      'children' : [ {'type': 'text', 'text': 'Click '}                           ,
                                     {'tag': 'a', 'children': [{'type': 'text', 'text': 'here'}]} ,
                                     {'type': 'text', 'text': ' to continue'}                     ]}

        result = self.transformation.transform_dict(html_dict)

        assert len(result['children']) == 1                                                         # All text merged into one
        assert result['children'][0]['type'] == 'text'
        assert result['children'][0]['text'] == 'Click here to continue'

    def test_transform_dict__bold_tag(self):                                                        # Test: <p>This is <b>bold</b> text</p>
        html_dict = { 'tag'      : 'p'                                                            ,
                      'children' : [ {'type': 'text', 'text': 'This is '}                         ,
                                     {'tag': 'b', 'children': [{'type': 'text', 'text': 'bold'}]} ,
                                     {'type': 'text', 'text': ' text'}                            ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['children'][0]['text'] == 'This is bold text'

    def test_transform_dict__italic_tag(self):                                                      # Test: <p>This is <i>italic</i> text</p>
        html_dict = { 'tag'      : 'p'                                                            ,
                      'children' : [ {'type': 'text', 'text': 'This is '}                         ,
                                     {'tag': 'i', 'children': [{'type': 'text', 'text': 'italic'}]},
                                     {'type': 'text', 'text': ' text'}                            ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['children'][0]['text'] == 'This is italic text'

    def test_transform_dict__span_tag(self):                                                        # Test: <div>Text <span class="x">inside</span> outside</div>
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [ {'type': 'text', 'text': 'Text '}                            ,
                                     {'tag': 'span', 'children': [{'type': 'text', 'text': 'inside'}]},
                                     {'type': 'text', 'text': ' outside'}                         ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['children'][0]['text'] == 'Text inside outside'

    def test_transform_dict__multiple_inline_tags(self):                                            # Test: <p><b>bold</b> and <i>italic</i> and <code>code</code></p>
        html_dict = { 'tag'      : 'p'                                                            ,
                      'children' : [ {'tag': 'b', 'children': [{'type': 'text', 'text': 'bold'}]}    ,
                                     {'type': 'text', 'text': ' and '}                              ,
                                     {'tag': 'i', 'children': [{'type': 'text', 'text': 'italic'}]} ,
                                     {'type': 'text', 'text': ' and '}                              ,
                                     {'tag': 'code', 'children': [{'type': 'text', 'text': 'code'}]}]}

        result = self.transformation.transform_dict(html_dict)

        assert result['children'][0]['text'] == 'bold and italic and code'

    def test_transform_dict__nested_inline_tags(self):                                              # Test: <p>Text <b><i>nested</i></b> end</p>
        html_dict = { 'tag'      : 'p'                                                            ,
                      'children' : [ {'type': 'text', 'text': 'Text '}                            ,
                                     {'tag': 'b', 'children': [
                                         {'tag': 'i', 'children': [
                                             {'type': 'text', 'text': 'nested'}
                                         ]}
                                     ]}                                                           ,
                                     {'type': 'text', 'text': ' end'}                             ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['children'][0]['text'] == 'Text nested end'

    def test_transform_dict__preserves_block_elements(self):                                        # Test: block elements like div, p are preserved
        html_dict = { 'tag'      : 'div'                                                          ,
                      'children' : [ {'tag': 'p', 'children': [
                                         {'type': 'text', 'text': 'Para '}                        ,
                                         {'tag': 'b', 'children': [{'type': 'text', 'text': 'bold'}]}
                                     ]}                                                           ,
                                     {'tag': 'p', 'children': [
                                         {'type': 'text', 'text': 'Another'}
                                     ]}                                                           ]}

        result = self.transformation.transform_dict(html_dict)

        assert len(result['children']) == 2                                                         # Both p tags preserved
        assert result['children'][0]['tag'] == 'p'
        assert result['children'][1]['tag'] == 'p'
        assert result['children'][0]['children'][0]['text'] == 'Para bold'                          # But inline stripped inside

    def test_transform_dict__em_and_strong_tags(self):                                              # Test: semantic inline tags <em>, <strong>
        html_dict = { 'tag'      : 'p'                                                            ,
                      'children' : [ {'type': 'text', 'text': 'This is '}                         ,
                                     {'tag': 'em', 'children': [{'type': 'text', 'text': 'emphasized'}]},
                                     {'type': 'text', 'text': ' and '}                            ,
                                     {'tag': 'strong', 'children': [{'type': 'text', 'text': 'strong'}]},
                                     {'type': 'text', 'text': ' text'}                            ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['children'][0]['text'] == 'This is emphasized and strong text'

    def test_transform_dict__mark_and_small_tags(self):                                             # Test: <mark> and <small> tags
        html_dict = { 'tag'      : 'p'                                                            ,
                      'children' : [ {'type': 'text', 'text': 'Text '}                            ,
                                     {'tag': 'mark', 'children': [{'type': 'text', 'text': 'highlighted'}]},
                                     {'type': 'text', 'text': ' and '}                            ,
                                     {'tag': 'small', 'children': [{'type': 'text', 'text': 'small'}]},
                                     {'type': 'text', 'text': ' text'}                            ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['children'][0]['text'] == 'Text highlighted and small text'

    def test_transform_dict__sub_and_sup_tags(self):                                                # Test: <sub> and <sup> tags (subscript/superscript)
        html_dict = { 'tag'      : 'p'                                                            ,
                      'children' : [ {'type': 'text', 'text': 'H'}                                ,
                                     {'tag': 'sub', 'children': [{'type': 'text', 'text': '2'}]}  ,
                                     {'type': 'text', 'text': 'O and E=mc'}                       ,
                                     {'tag': 'sup', 'children': [{'type': 'text', 'text': '2'}]}  ]}

        result = self.transformation.transform_dict(html_dict)

        assert result['children'][0]['text'] == 'H2O and E=mc2'

    def test_transform_dict__empty_dict(self):                                                      # Test: empty input
        result = self.transformation.transform_dict({})
        assert result == {}

    def test_transform_dict__none_input(self):                                                      # Test: None input
        result = self.transformation.transform_dict(None)
        assert result is None

    def test_transform_dict__no_children(self):                                                     # Test: element with no children
        html_dict = {'tag': 'p'}

        result = self.transformation.transform_dict(html_dict)

        assert result == {'tag': 'p'}

    def test_transform_dict__only_text_children(self):                                              # Test: element with only text children (no inline to strip)
        html_dict = { 'tag'      : 'p'                                                            ,
                      'children' : [ {'type': 'text', 'text': 'First '}                           ,
                                     {'type': 'text', 'text': 'Second'}                           ]}

        result = self.transformation.transform_dict(html_dict)

        assert len(result['children']) == 1                                                         # Adjacent text nodes merged
        assert result['children'][0]['text'] == 'First Second'

    def test_transform_dict__abbr_and_dfn_tags(self):                                               # Test: <abbr> and <dfn> tags
        html_dict = { 'tag'      : 'p'                                                            ,
                      'children' : [ {'type': 'text', 'text': 'The '}                             ,
                                     {'tag': 'abbr', 'children': [{'type': 'text', 'text': 'HTML'}]},
                                     {'type': 'text', 'text': ' means '}                          ,
                                     {'tag': 'dfn', 'children': [{'type': 'text', 'text': 'HyperText'}]}]}

        result = self.transformation.transform_dict(html_dict)

        assert result['children'][0]['text'] == 'The HTML means HyperText'

    def test_transform_dict__kbd_and_samp_tags(self):                                               # Test: <kbd> and <samp> tags (keyboard/sample output)
        html_dict = { 'tag'      : 'p'                                                            ,
                      'children' : [ {'type': 'text', 'text': 'Press '}                           ,
                                     {'tag': 'kbd', 'children': [{'type': 'text', 'text': 'Ctrl+C'}]},
                                     {'type': 'text', 'text': ' to see '}                         ,
                                     {'tag': 'samp', 'children': [{'type': 'text', 'text': 'output'}]}]}

        result = self.transformation.transform_dict(html_dict)

        assert result['children'][0]['text'] == 'Press Ctrl+C to see output'