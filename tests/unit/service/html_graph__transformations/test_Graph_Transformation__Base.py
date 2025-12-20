from unittest                                                                                        import TestCase
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base


class test_Graph_Transformation__Base(TestCase):

    @classmethod
    def setUpClass(cls):                                                                            # One-time setup for all tests
        cls.transformation = Graph_Transformation__Base()

    def test__init__(self):                                                                         # Test initialization and attributes
        with Graph_Transformation__Base() as _:
            assert _.name        == 'default'
            assert _.label       == 'Default'
            assert _.description == 'Standard HTML to MGraph conversion with full detail'

    def test_transform_html__passthrough(self):                                                     # Test Phase 1: default passes through unchanged
        html = '<div><p>Hello</p></div>'

        result = self.transformation.transform_html(html)

        assert result == html                                                                       # Should return unchanged

    def test_transform_html__empty_string(self):                                                    # Test Phase 1: empty string
        result = self.transformation.transform_html('')
        assert result == ''

    def test_transform_html__complex_html(self):                                                    # Test Phase 1: complex HTML passes through
        html = '''<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><div class="container"><p>Content</p></div></body>
</html>'''

        result = self.transformation.transform_html(html)

        assert result == html

    def test_transform_dict__passthrough(self):                                                     # Test Phase 2: default passes through unchanged
        html_dict = { 'tag'        : 'div'                                                        ,
                      'attrs'      : {'class': 'test'}                                            ,
                      'child_nodes': [{'tag': 'p', 'attrs': {}, 'child_nodes': [], 'text_nodes': []}],
                      'text_nodes' : []                                                           }

        result = self.transformation.transform_dict(html_dict)

        assert result == html_dict                                                                  # Should return unchanged

    def test_transform_dict__empty_dict(self):                                                      # Test Phase 2: empty dict
        result = self.transformation.transform_dict({})
        assert result == {}

    def test_transform_dict__nested_structure(self):                                                # Test Phase 2: nested structure passes through
        html_dict = { 'tag'        : 'html'                                                       ,
                      'child_nodes': [
                          {'tag': 'body', 'child_nodes': [
                              {'tag': 'div', 'child_nodes': [
                                  {'tag': 'p', 'child_nodes': [], 'text_nodes': [{'data': 'Text'}]}
                              ], 'text_nodes': []}
                          ], 'text_nodes': []}
                      ]                                                                           ,
                      'text_nodes' : []                                                           }

        result = self.transformation.transform_dict(html_dict)

        assert result == html_dict

    def test_transform_mgraph__passthrough(self):                                                   # Test Phase 4: default passes through unchanged
        mock_mgraph = {'mock': 'mgraph'}                                                            # Using dict as mock

        result = self.transformation.transform_mgraph(mock_mgraph)

        assert result == mock_mgraph

    def test_transform_export__passthrough(self):                                                   # Test Phase 5: default passes through unchanged
        export_data = { 'nodes': [{'id': '1', 'label': 'div'}]                                    ,
                        'edges': [{'from': '1', 'to': '2'}]                                       }

        result = self.transformation.transform_export(export_data)

        assert result == export_data

    def test_transform_export__empty_dict(self):                                                    # Test Phase 5: empty dict
        result = self.transformation.transform_export({})
        assert result == {}

    def test_to_dict(self):                                                                         # Test metadata output
        result = self.transformation.to_dict()

        assert result == { 'name'       : 'default'                                               ,
                           'label'      : 'Default'                                               ,
                           'description': 'Standard HTML to MGraph conversion with full detail'  }

    def test_to_dict__custom_transformation(self):                                                  # Test to_dict with custom values
        class Custom_Transformation(Graph_Transformation__Base):
            name        : str = 'custom'
            label       : str = 'Custom Transform'
            description : str = 'A custom transformation'

        with Custom_Transformation() as _:
            result = _.to_dict()

            assert result == { 'name'       : 'custom'                                            ,
                               'label'      : 'Custom Transform'                                  ,
                               'description': 'A custom transformation'                          }

    def test_inheritance__override_single_phase(self):                                              # Test that subclasses can override single phase
        class Html_Uppercase(Graph_Transformation__Base):
            def transform_html(self, html: str) -> str:
                return html.upper()

        with Html_Uppercase() as _:
            result = _.transform_html('<div>hello</div>')
            assert result == '<DIV>HELLO</DIV>'

            dict_result = _.transform_dict({'tag': 'div'})                                          # Other phases unchanged
            assert dict_result == {'tag': 'div'}
