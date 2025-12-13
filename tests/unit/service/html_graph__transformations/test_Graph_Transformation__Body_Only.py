from unittest                                                                                             import TestCase
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Body_Only import Graph_Transformation__Body_Only


class test_Graph_Transformation__Body_Only(TestCase):

    @classmethod
    def setUpClass(cls):                                                                            # One-time setup for all tests
        cls.transformation = Graph_Transformation__Body_Only()

    def test__init__(self):                                                                         # Test initialization and attributes
        with Graph_Transformation__Body_Only() as _:
            assert _.name        == 'body_only'
            assert _.label       == 'Body Only'
            assert _.description == 'Show only body content, hiding head and metadata'

    def test_transform_dict__extracts_body(self):                                                   # Test: extracts body from full HTML structure
        html_dict = { 'tag'        : 'html'                                                       ,
                      'child_nodes': [
                          {'tag': 'head', 'child_nodes': [
                              {'tag': 'title', 'child_nodes': [], 'text_nodes': [{'data': 'Page'}]}
                          ], 'text_nodes': []}                                                    ,
                          {'tag': 'body', 'child_nodes': [
                              {'tag': 'div', 'child_nodes': [], 'text_nodes': [{'data': 'Content'}]}
                          ], 'text_nodes': []}
                      ]                                                                           ,
                      'text_nodes' : []                                                           }

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'body'                                                              # Should return body element
        assert len(result['child_nodes']) == 1
        assert result['child_nodes'][0]['tag'] == 'div'

    def test_transform_dict__body_with_multiple_children(self):                                     # Test: body with multiple child elements
        html_dict = { 'tag'        : 'html'                                                       ,
                      'child_nodes': [
                          {'tag': 'body', 'child_nodes': [
                              {'tag': 'header', 'child_nodes': [], 'text_nodes': []}              ,
                              {'tag': 'main', 'child_nodes': [], 'text_nodes': []}                ,
                              {'tag': 'footer', 'child_nodes': [], 'text_nodes': []}
                          ], 'text_nodes': []}
                      ]                                                                           ,
                      'text_nodes' : []                                                           }

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'body'
        assert len(result['child_nodes']) == 3
        assert result['child_nodes'][0]['tag'] == 'header'
        assert result['child_nodes'][1]['tag'] == 'main'
        assert result['child_nodes'][2]['tag'] == 'footer'

    def test_transform_dict__no_body_returns_original(self):                                        # Test: fallback when no body found
        html_dict = { 'tag'        : 'div'                                                        ,
                      'child_nodes': [
                          {'tag': 'p', 'child_nodes': [], 'text_nodes': [{'data': 'No body'}]}
                      ]                                                                           ,
                      'text_nodes' : []                                                           }

        result = self.transformation.transform_dict(html_dict)

        assert result == html_dict                                                                  # Returns original when no body

    def test_transform_dict__deeply_nested_body(self):                                              # Test: body nested inside other elements
        html_dict = { 'tag'        : 'html'                                                       ,
                      'child_nodes': [
                          {'tag': 'head', 'child_nodes': [], 'text_nodes': []}                    ,
                          {'tag': 'body', 'child_nodes': [
                              {'tag': 'div', 'child_nodes': [
                                  {'tag': 'section', 'child_nodes': [
                                      {'tag': 'article', 'child_nodes': [], 'text_nodes': []}
                                  ], 'text_nodes': []}
                              ], 'text_nodes': []}
                          ], 'text_nodes': []}
                      ]                                                                           ,
                      'text_nodes' : []                                                           }

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'body'
        assert result['child_nodes'][0]['tag'] == 'div'
        assert result['child_nodes'][0]['child_nodes'][0]['tag'] == 'section'

    def test_transform_dict__body_case_insensitive(self):                                           # Test: BODY tag (uppercase) is found
        html_dict = { 'tag'        : 'html'                                                       ,
                      'child_nodes': [
                          {'tag': 'BODY', 'child_nodes': [
                              {'tag': 'p', 'child_nodes': [], 'text_nodes': []}
                          ], 'text_nodes': []}
                      ]                                                                           ,
                      'text_nodes' : []                                                           }

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'BODY'                                                              # Returns the body element

    def test_transform_dict__empty_body(self):                                                      # Test: empty body element
        html_dict = { 'tag'        : 'html'                                                       ,
                      'child_nodes': [
                          {'tag': 'head', 'child_nodes': [], 'text_nodes': []}                    ,
                          {'tag': 'body', 'child_nodes': [], 'text_nodes': []}
                      ]                                                                           ,
                      'text_nodes' : []                                                           }

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'body'
        assert result['child_nodes'] == []

    def test_transform_dict__body_with_text_nodes(self):                                            # Test: body with direct text content
        html_dict = { 'tag'        : 'html'                                                       ,
                      'child_nodes': [
                          {'tag': 'body', 'child_nodes': [], 'text_nodes': [{'data': 'Direct text'}]}
                      ]                                                                           ,
                      'text_nodes' : []                                                           }

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'body'
        assert result['text_nodes'] == [{'data': 'Direct text'}]

    def test_transform_dict__empty_dict(self):                                                      # Test: empty input
        result = self.transformation.transform_dict({})
        assert result == {}                                                                         # No body found, returns original

    def test_transform_dict__preserves_body_attributes(self):                                       # Test: body attributes are preserved
        html_dict = { 'tag'        : 'html'                                                       ,
                      'child_nodes': [
                          {'tag'       : 'body'                                                   ,
                           'attrs'     : {'class': 'main-body', 'id': 'root'}                     ,
                           'child_nodes': []                                                      ,
                           'text_nodes': []                                                       }
                      ]                                                                           ,
                      'text_nodes' : []                                                           }

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'body'
        assert result['attrs'] == {'class': 'main-body', 'id': 'root'}

    def test_transform_export__passthrough(self):                                                   # Test Phase 5: passes through unchanged
        export_data = { 'nodes': [{'id': '1', 'label': 'body'}]                                   ,
                        'edges': []                                                               }

        result = self.transformation.transform_export(export_data)

        assert result == export_data

    def test_to_dict(self):                                                                         # Test metadata output
        result = self.transformation.to_dict()

        assert result == { 'name'       : 'body_only'                                             ,
                           'label'      : 'Body Only'                                             ,
                           'description': 'Show only body content, hiding head and metadata'     }

    def test__find_body__direct_child(self):                                                        # Test private method: body as direct child
        html_dict = { 'tag'        : 'html'                                                       ,
                      'child_nodes': [
                          {'tag': 'body', 'child_nodes': [], 'text_nodes': []}
                      ]}

        result = self.transformation._find_body(html_dict)

        assert result['tag'] == 'body'

    def test__find_body__none_for_non_dict(self):                                                   # Test private method: non-dict input
        result = self.transformation._find_body("not a dict")
        assert result is None

        result = self.transformation._find_body(None)
        assert result is None

        result = self.transformation._find_body([])
        assert result is None
