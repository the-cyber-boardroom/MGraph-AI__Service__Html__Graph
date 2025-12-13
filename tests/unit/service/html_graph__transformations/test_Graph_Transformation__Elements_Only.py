from unittest                                                                                               import TestCase
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Elements_Only import Graph_Transformation__Elements_Only


class test_Graph_Transformation__Elements_Only(TestCase):

    @classmethod
    def setUpClass(cls):                                                                            # One-time setup for all tests
        cls.transformation = Graph_Transformation__Elements_Only()

    def test__init__(self):                                                                         # Test initialization and attributes
        with Graph_Transformation__Elements_Only() as _:
            assert _.name        == 'elements_only'
            assert _.label       == 'Elements Only'
            assert _.description == 'Simplified element hierarchy without tags, attrs, or text'

    def test_transform_dict__removes_attrs(self):                                                   # Test: attributes are removed
        html_dict = { 'tag'        : 'div'                                                        ,
                      'attrs'      : {'class': 'container', 'id': 'main', 'data-value': '123'}    ,
                      'child_nodes': []                                                           ,
                      'text_nodes' : []                                                           }

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'div'
        assert result['attrs'] == {}                                                                # Attrs cleared

    def test_transform_dict__removes_text_nodes(self):                                              # Test: text nodes are removed
        html_dict = { 'tag'        : 'p'                                                          ,
                      'attrs'      : {}                                                           ,
                      'child_nodes': []                                                           ,
                      'text_nodes' : [{'data': 'Hello'}, {'data': 'World'}]                       }

        result = self.transformation.transform_dict(html_dict)

        assert result['text_nodes'] == []                                                           # Text nodes cleared

    def test_transform_dict__preserves_tag(self):                                                   # Test: tag name preserved
        html_dict = { 'tag'        : 'section'                                                    ,
                      'attrs'      : {'class': 'main'}                                            ,
                      'child_nodes': []                                                           ,
                      'text_nodes' : [{'data': 'Content'}]                                        }

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'section'

    def test_transform_dict__preserves_position(self):                                              # Test: position is preserved
        html_dict = { 'tag'        : 'div'                                                        ,
                      'attrs'      : {}                                                           ,
                      'child_nodes': []                                                           ,
                      'text_nodes' : []                                                           ,
                      'position'   : {'line': 10, 'col': 5}                                       }

        result = self.transformation.transform_dict(html_dict)

        assert result['position'] == {'line': 10, 'col': 5}

    def test_transform_dict__recursive_children(self):                                              # Test: children are processed recursively
        html_dict = { 'tag'        : 'div'                                                        ,
                      'attrs'      : {'class': 'outer'}                                           ,
                      'child_nodes': [
                          {'tag': 'p', 'attrs': {'id': 'para'}, 'child_nodes': [], 'text_nodes': [{'data': 'Text'}]},
                          {'tag': 'span', 'attrs': {'class': 'inner'}, 'child_nodes': [], 'text_nodes': []}
                      ]                                                                           ,
                      'text_nodes' : [{'data': 'Div text'}]                                       }

        result = self.transformation.transform_dict(html_dict)

        assert result['attrs'] == {}
        assert result['text_nodes'] == []
        assert len(result['child_nodes']) == 2

        assert result['child_nodes'][0]['tag'] == 'p'                                               # Children simplified
        assert result['child_nodes'][0]['attrs'] == {}
        assert result['child_nodes'][0]['text_nodes'] == []

        assert result['child_nodes'][1]['tag'] == 'span'
        assert result['child_nodes'][1]['attrs'] == {}

    def test_transform_dict__deeply_nested(self):                                                   # Test: deeply nested structure
        html_dict = { 'tag'        : 'html'                                                       ,
                      'attrs'      : {'lang': 'en'}                                               ,
                      'child_nodes': [
                          {'tag': 'body', 'attrs': {'class': 'main'}, 'child_nodes': [
                              {'tag': 'div', 'attrs': {'id': 'container'}, 'child_nodes': [
                                  {'tag': 'p', 'attrs': {}, 'child_nodes': [], 'text_nodes': [{'data': 'Text'}]}
                              ], 'text_nodes': []}
                          ], 'text_nodes': []}
                      ]                                                                           ,
                      'text_nodes' : []                                                           }

        result = self.transformation.transform_dict(html_dict)

        assert result['attrs'] == {}
        body = result['child_nodes'][0]
        assert body['attrs'] == {}
        div = body['child_nodes'][0]
        assert div['attrs'] == {}
        p = div['child_nodes'][0]
        assert p['attrs'] == {}
        assert p['text_nodes'] == []

    def test_transform_dict__missing_tag(self):                                                     # Test: element without tag
        html_dict = { 'attrs'      : {'class': 'no-tag'}                                          ,
                      'child_nodes': []                                                           ,
                      'text_nodes' : []                                                           }

        result = self.transformation.transform_dict(html_dict)

        assert result['tag'] == 'unknown'                                                           # Default to 'unknown'

    def test_transform_dict__empty_dict(self):                                                      # Test: empty input
        result = self.transformation.transform_dict({})

        assert result['tag'] == 'unknown'
        assert result['attrs'] == {}
        assert result['child_nodes'] == []
        assert result['text_nodes'] == []

    def test_transform_dict__non_dict_children_filtered(self):                                      # Test: non-dict children are filtered
        html_dict = { 'tag'        : 'div'                                                        ,
                      'attrs'      : {}                                                           ,
                      'child_nodes': [
                          {'tag': 'p', 'attrs': {}, 'child_nodes': [], 'text_nodes': []}          ,
                          'invalid_string'                                                        ,
                          None                                                                    ,
                          {'tag': 'span', 'attrs': {}, 'child_nodes': [], 'text_nodes': []}
                      ]                                                                           ,
                      'text_nodes' : []                                                           }

        result = self.transformation.transform_dict(html_dict)

        assert len(result['child_nodes']) == 2                                                      # Only dict children
        assert result['child_nodes'][0]['tag'] == 'p'
        assert result['child_nodes'][1]['tag'] == 'span'

    def test_transform_export__filters_to_elements(self):                                           # Test Phase 5: filters to element nodes only
        export_data = { 'nodes': [
                            {'id': '1', 'nodeType': 'element', 'label': 'div'}                    ,
                            {'id': '2', 'nodeType': 'text', 'label': 'Hello'}                     ,
                            {'id': '3', 'nodeType': 'element', 'label': 'p'}                      ,
                            {'id': '4', 'nodeType': 'attribute', 'label': 'class'}
                        ]                                                                         ,
                        'edges': [
                            {'from': '1', 'to': '2'}                                              ,
                            {'from': '1', 'to': '3'}                                              ,
                            {'from': '1', 'to': '4'}
                        ]                                                                         }

        result = self.transformation.transform_export(export_data)

        assert len(result['nodes']) == 2                                                            # Only elements
        assert all(n['nodeType'] == 'element' for n in result['nodes'])

        assert len(result['edges']) == 1                                                            # Only edge between elements
        assert result['edges'][0] == {'from': '1', 'to': '3'}

    def test_transform_export__filters_links(self):                                                 # Test Phase 5: filters links (D3 format)
        export_data = { 'nodes': [
                            {'id': '1', 'nodeType': 'element'}                                    ,
                            {'id': '2', 'nodeType': 'text'}                                       ,
                            {'id': '3', 'nodeType': 'element'}
                        ]                                                                         ,
                        'links': [
                            {'source': '1', 'target': '2'}                                        ,
                            {'source': '1', 'target': '3'}
                        ]                                                                         }

        result = self.transformation.transform_export(export_data)

        assert len(result['links']) == 1
        assert result['links'][0] == {'source': '1', 'target': '3'}

    def test_transform_export__cytoscape_format(self):                                              # Test Phase 5: Cytoscape elements format
        export_data = { 'elements': {
                            'nodes': [
                                {'data': {'id': '1', 'nodeType': 'element'}}                      ,
                                {'data': {'id': '2', 'nodeType': 'text'}}                         ,
                                {'data': {'id': '3', 'nodeType': 'element'}}
                            ]                                                                     ,
                            'edges': [
                                {'data': {'source': '1', 'target': '2'}}                          ,
                                {'data': {'source': '1', 'target': '3'}}
                            ]
                        }                                                                         }

        result = self.transformation.transform_export(export_data)

        assert len(result['elements']['nodes']) == 2                                                # Only elements
        assert len(result['elements']['edges']) == 1                                                # Only edge between elements
        assert result['elements']['edges'][0]['data'] == {'source': '1', 'target': '3'}

    def test_transform_export__empty_nodes(self):                                                   # Test Phase 5: empty nodes array
        export_data = {'nodes': [], 'edges': []}

        result = self.transformation.transform_export(export_data)

        assert result['nodes'] == []
        assert result['edges'] == []

    def test_transform_export__no_elements(self):                                                   # Test Phase 5: no element type nodes
        export_data = { 'nodes': [
                            {'id': '1', 'nodeType': 'text'}                                       ,
                            {'id': '2', 'nodeType': 'attribute'}
                        ]                                                                         ,
                        'edges': [{'from': '1', 'to': '2'}]                                       }

        result = self.transformation.transform_export(export_data)

        assert result['nodes'] == []                                                                # All filtered out
        assert result['edges'] == []                                                                # No valid edges

    def test_to_dict(self):                                                                         # Test metadata output
        result = self.transformation.to_dict()

        assert result == { 'name'       : 'elements_only'                                         ,
                           'label'      : 'Elements Only'                                         ,
                           'description': 'Simplified element hierarchy without tags, attrs, or text'}

    def test_transform_export__passthrough_no_nodes(self):                                          # Test Phase 5: no nodes key
        export_data = {'custom': 'data'}

        result = self.transformation.transform_export(export_data)

        assert result == {'custom': 'data'}                                                         # Unchanged
