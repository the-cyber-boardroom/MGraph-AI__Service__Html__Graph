from unittest                                                                                              import TestCase
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Collapse_Text import Graph_Transformation__Collapse_Text


class test_Graph_Transformation__Collapse_Text(TestCase):

    @classmethod
    def setUpClass(cls):                                                                            # One-time setup for all tests
        cls.transformation = Graph_Transformation__Collapse_Text()

    def test__init__(self):                                                                         # Test initialization and attributes
        with Graph_Transformation__Collapse_Text() as _:
            assert _.name        == 'collapse_text'
            assert _.label       == 'Collapse Text'
            assert _.description == 'Text content merged into parent element labels'

    def test_transform_dict__collapses_text_nodes(self):                                            # Test: text nodes collapsed into _collapsed_text
        html_dict = { 'tag'        : 'p'                                                          ,
                      'child_nodes': []                                                           ,
                      'text_nodes' : [{'data': 'Hello'}, {'data': 'World'}]                       }

        result = self.transformation.transform_dict(html_dict)

        assert result['text_nodes'] == []                                                           # Text nodes cleared
        assert result['_collapsed_text'] == 'Hello World'                                           # Text collapsed

    def test_transform_dict__single_text_node(self):                                                # Test: single text node
        html_dict = { 'tag'        : 'span'                                                       ,
                      'child_nodes': []                                                           ,
                      'text_nodes' : [{'data': 'Single text'}]                                    }

        result = self.transformation.transform_dict(html_dict)

        assert result['text_nodes'] == []
        assert result['_collapsed_text'] == 'Single text'

    def test_transform_dict__empty_text_nodes(self):                                                # Test: no text nodes
        html_dict = { 'tag'        : 'div'                                                        ,
                      'child_nodes': []                                                           ,
                      'text_nodes' : []                                                           }

        result = self.transformation.transform_dict(html_dict)

        assert result['text_nodes'] == []
        assert '_collapsed_text' not in result                                                      # No collapsed text if empty

    def test_transform_dict__whitespace_trimmed(self):                                              # Test: whitespace is trimmed and joined
        html_dict = { 'tag'        : 'p'                                                          ,
                      'child_nodes': []                                                           ,
                      'text_nodes' : [{'data': '  Hello  '}, {'data': '  World  '}]               }

        result = self.transformation.transform_dict(html_dict)

        assert result['_collapsed_text'] == 'Hello World'                                           # Trimmed and joined

    def test_transform_dict__whitespace_only_ignored(self):                                         # Test: whitespace-only text nodes ignored
        html_dict = { 'tag'        : 'div'                                                        ,
                      'child_nodes': []                                                           ,
                      'text_nodes' : [{'data': '   '}, {'data': '\n\t'}]                          }

        result = self.transformation.transform_dict(html_dict)

        assert result['text_nodes'] == []
        assert '_collapsed_text' not in result                                                      # No collapsed text for whitespace-only

    def test_transform_dict__recursive_children(self):                                              # Test: recursive processing of child nodes
        html_dict = { 'tag'        : 'div'                                                        ,
                      'child_nodes': [
                          {'tag': 'p', 'child_nodes': [], 'text_nodes': [{'data': 'Para text'}]}  ,
                          {'tag': 'span', 'child_nodes': [], 'text_nodes': [{'data': 'Span text'}]}
                      ]                                                                           ,
                      'text_nodes' : [{'data': 'Div text'}]                                       }

        result = self.transformation.transform_dict(html_dict)

        assert result['_collapsed_text'] == 'Div text'
        assert result['child_nodes'][0]['_collapsed_text'] == 'Para text'
        assert result['child_nodes'][1]['_collapsed_text'] == 'Span text'

    def test_transform_dict__deeply_nested(self):                                                   # Test: deeply nested structure
        html_dict = { 'tag'        : 'article'                                                    ,
                      'child_nodes': [
                          {'tag': 'section', 'child_nodes': [
                              {'tag': 'p', 'child_nodes': [], 'text_nodes': [{'data': 'Deep'}]}
                          ], 'text_nodes': [{'data': 'Section'}]}
                      ]                                                                           ,
                      'text_nodes' : [{'data': 'Article'}]                                        }

        result = self.transformation.transform_dict(html_dict)

        assert result['_collapsed_text'] == 'Article'
        assert result['child_nodes'][0]['_collapsed_text'] == 'Section'
        assert result['child_nodes'][0]['child_nodes'][0]['_collapsed_text'] == 'Deep'

    def test_transform_dict__preserves_other_attributes(self):                                      # Test: other attributes are preserved
        html_dict = { 'tag'        : 'div'                                                        ,
                      'attrs'      : {'class': 'container', 'id': 'main'}                         ,
                      'child_nodes': []                                                           ,
                      'text_nodes' : [{'data': 'Content'}]                                        ,
                      'position'   : {'line': 1, 'col': 1}                                        }

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'div'
        assert result['attrs'] == {'class': 'container', 'id': 'main'}
        assert result['position'] == {'line': 1, 'col': 1}
        assert result['_collapsed_text'] == 'Content'

    def test_transform_dict__empty_dict(self):                                                      # Test: empty input
        result = self.transformation.transform_dict({})
        assert result == {}

    def test_transform_dict__non_dict_passthrough(self):                                            # Test: non-dict input
        result = self.transformation._collapse_text_recursive("string")
        assert result == "string"

        result = self.transformation._collapse_text_recursive(123)
        assert result == 123

    def test_transform_dict__missing_text_nodes_key(self):                                          # Test: no text_nodes key in dict
        html_dict = { 'tag'        : 'br'                                                         ,
                      'child_nodes': []                                                           }

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'br'
        assert '_collapsed_text' not in result

    def test_transform_dict__text_nodes_with_non_dict_entries(self):                                # Test: text_nodes with invalid entries
        html_dict = { 'tag'        : 'p'                                                          ,
                      'child_nodes': []                                                           ,
                      'text_nodes' : [{'data': 'Valid'}, 'invalid', None, {'data': 'Also valid'}] }

        result = self.transformation.transform_dict(html_dict)

        assert result['_collapsed_text'] == 'Valid Also valid'                                      # Only valid entries processed

    def test_transform_export__passthrough(self):                                                   # Test Phase 5: passes through unchanged
        export_data = { 'nodes': [{'id': '1', 'label': 'div'}]                                    ,
                        'edges': []                                                               }

        result = self.transformation.transform_export(export_data)

        assert result == export_data

    def test_to_dict(self):                                                                         # Test metadata output
        result = self.transformation.to_dict()

        assert result == { 'name'       : 'collapse_text'                                         ,
                           'label'      : 'Collapse Text'                                         ,
                           'description': 'Text content merged into parent element labels'       }

    def test_transform_dict__multiple_text_with_empty(self):                                        # Test: mix of text and empty data
        html_dict = { 'tag'        : 'p'                                                          ,
                      'child_nodes': []                                                           ,
                      'text_nodes' : [{'data': 'First'}, {'data': ''}, {'data': 'Second'}]        }

        result = self.transformation.transform_dict(html_dict)

        assert result['_collapsed_text'] == 'First Second'                                          # Empty strings filtered out
