from unittest                                                                           import TestCase
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.utils.Objects                                                          import base_classes
from mgraph_ai_service_html_graph.service.html_graph.Html_Dict__OSBot__To__Html_Dict    import Html_Dict__OSBot__To__Html_Dict


class test_Html_Dict__OSBot__To__Html_Dict(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.converter = Html_Dict__OSBot__To__Html_Dict()

        cls.osbot_simple = { 'tag'  : 'html'                                                ,   # Simple OSBot format
                             'attrs': {}                                                    ,
                             'nodes': [{ 'tag'  : 'body'                                    ,
                                         'attrs': {}                                        ,
                                         'nodes': [{ 'tag'  : 'p'                           ,
                                                     'attrs': {}                            ,
                                                     'nodes': [{ 'data': 'an paragraph'     ,
                                                                 'type': 'TEXT'             }]}]}]}

        cls.osbot_with_attrs = { 'tag'  : 'html'                                            ,   # OSBot format with attributes
                                 'attrs': {'lang': 'en'}                                    ,
                                 'nodes': [{ 'tag'  : 'head'                                ,
                                             'attrs': {}                                    ,
                                             'nodes': [{ 'tag'  : 'meta'                    ,
                                                         'attrs': {'charset': 'UTF-8'}      ,
                                                         'nodes': []                        },
                                                       { 'tag'  : 'title'                   ,
                                                         'attrs': {}                        ,
                                                         'nodes': [{ 'data': 'Test Page'    ,
                                                                     'type': 'TEXT'         }]}]}]}

        cls.osbot_mixed_content = { 'tag'  : 'div'                                          ,   # OSBot format with mixed content
                                    'attrs': {}                                             ,
                                    'nodes': [{ 'data': 'text before '                      ,
                                                'type': 'TEXT'                              },
                                              { 'tag'  : 'b'                                ,
                                                'attrs': {}                                 ,
                                                'nodes': [{ 'data': 'bold text'             ,
                                                            'type': 'TEXT'                  }]},
                                              { 'data': ' text after'                       ,
                                                'type': 'TEXT'                              }]}

        cls.osbot_whitespace = { 'tag'  : 'div'                                             ,   # OSBot format with whitespace-only text
                                 'attrs': {}                                                ,
                                 'nodes': [{ 'data': '\n            '                       ,
                                             'type': 'TEXT'                                 },
                                           { 'tag'  : 'p'                                   ,
                                             'attrs': {}                                    ,
                                             'nodes': [{ 'data': 'content'                  ,
                                                         'type': 'TEXT'                     }]},
                                           { 'data': '\n        '                           ,
                                             'type': 'TEXT'                                 }]}

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                 # Test auto-initialization
        with Html_Dict__OSBot__To__Html_Dict() as _:
            assert type(_)         is Html_Dict__OSBot__To__Html_Dict
            assert base_classes(_) == [Type_Safe, object]

    # ═══════════════════════════════════════════════════════════════════════════════
    # convert Tests - Basic
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_convert__empty_dict(self):                                                     # Test converting empty dict
        with self.converter as _:
            assert _.convert({})   == {}
            assert _.convert(None) == {}

    def test_convert__simple_structure(self):                                               # Test converting simple nested structure
        with self.converter as _:
            result = _.convert(self.osbot_simple)

            assert result['tag']                                       == 'html'
            assert result['attrs']                                     == {}
            assert len(result['child_nodes'])                          == 1
            assert len(result['text_nodes'])                           == 0

            body = result['child_nodes'][0]
            assert body['tag']                                         == 'body'
            assert len(body['child_nodes'])                            == 1

            p = body['child_nodes'][0]
            assert p['tag']                                            == 'p'
            assert len(p['text_nodes'])                                == 1
            assert p['text_nodes'][0]['data']                          == 'an paragraph'

    def test_convert__preserves_attrs(self):                                                # Test that attributes are preserved
        with self.converter as _:
            result = _.convert(self.osbot_with_attrs)

            assert result['attrs']                                     == {'lang': 'en'}

            head = result['child_nodes'][0]
            meta = head['child_nodes'][0]
            assert meta['attrs']                                       == {'charset': 'UTF-8'}

    # ═══════════════════════════════════════════════════════════════════════════════
    # convert Tests - Mixed Content
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_convert__mixed_content_separates_nodes(self):                                  # Test mixed text and elements are separated
        with self.converter as _:
            result = _.convert(self.osbot_mixed_content)

            assert result['tag']              == 'div'
            assert len(result['child_nodes']) == 1                                          # One <b> element
            assert len(result['text_nodes'])  == 2                                          # Two text nodes

    def test_convert__mixed_content_preserves_positions(self):                              # Test positions are preserved for ordering
        with self.converter as _:
            result = _.convert(self.osbot_mixed_content)

            text_positions  = [t['position'] for t in result['text_nodes']]
            child_positions = [c['position'] for c in result['child_nodes']]

            assert 0 in text_positions                                                      # 'text before ' at position 0
            assert 1 in child_positions                                                     # <b> at position 1
            assert 2 in text_positions                                                      # ' text after' at position 2

    def test_convert__mixed_content_text_data(self):                                        # Test text content is correct
        with self.converter as _:
            result = _.convert(self.osbot_mixed_content)

            text_by_pos = {t['position']: t['data'] for t in result['text_nodes']}
            assert text_by_pos[0] == 'text before '
            assert text_by_pos[2] == ' text after'

    # ═══════════════════════════════════════════════════════════════════════════════
    # convert Tests - Whitespace Handling
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_convert__skips_whitespace_only_text(self):                                     # Test whitespace-only text nodes are skipped
        with self.converter as _:
            result = _.convert(self.osbot_whitespace)

            assert len(result['text_nodes'])  == 0                                          # Whitespace-only nodes skipped
            assert len(result['child_nodes']) == 1                                          # <p> element preserved

    def test_convert__preserves_text_with_mixed_whitespace(self):                           # Test text with content AND whitespace is preserved
        osbot_mixed = { 'tag'  : 'div'                                                      ,
                        'attrs': {}                                                         ,
                        'nodes': [{ 'data': '\n            another div with '               ,
                                    'type': 'TEXT'                                          },
                                  { 'tag'  : 'b'                                            ,
                                    'attrs': {}                                             ,
                                    'nodes': [{ 'data': 'a bold'                            ,
                                                'type': 'TEXT'                              }]},
                                  { 'data': ' element\n        '                            ,
                                    'type': 'TEXT'                                          }]}

        with self.converter as _:
            result = _.convert(osbot_mixed)

            assert len(result['text_nodes'])       == 2                                     # Both text nodes preserved
            assert result['text_nodes'][0]['data'] == '\n            another div with '
            assert result['text_nodes'][0]['position'] == 0
            assert result['text_nodes'][1]['data'] == ' element\n        '
            assert result['text_nodes'][1]['position'] == 2

    # ═══════════════════════════════════════════════════════════════════════════════
    # convert Tests - Recursive Structure
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_convert__deeply_nested(self):                                                  # Test deeply nested structure
        osbot_deep = { 'tag'  : 'div'                                                       ,
                       'attrs': {}                                                          ,
                       'nodes': [{ 'tag'  : 'div'                                           ,
                                   'attrs': {}                                              ,
                                   'nodes': [{ 'tag'  : 'div'                               ,
                                               'attrs': {}                                  ,
                                               'nodes': [{ 'tag'  : 'span'                  ,
                                                           'attrs': {}                      ,
                                                           'nodes': [{ 'data': 'deep'       ,
                                                                       'type': 'TEXT'       }]}]}]}]}

        with self.converter as _:
            result = _.convert(osbot_deep)

            level1 = result['child_nodes'][0]
            level2 = level1['child_nodes'][0]
            level3 = level2['child_nodes'][0]

            assert result['tag'] == 'div'
            assert level1['tag'] == 'div'
            assert level2['tag'] == 'div'
            assert level3['tag'] == 'span'
            assert level3['text_nodes'][0]['data'] == 'deep'

    def test_convert__multiple_children(self):                                              # Test multiple child elements
        osbot_multi = { 'tag'  : 'ul'                                                       ,
                        'attrs': {}                                                         ,
                        'nodes': [{ 'tag'  : 'li'                                           ,
                                    'attrs': {}                                             ,
                                    'nodes': [{ 'data': 'Item 1'                            ,
                                                'type': 'TEXT'                              }]},
                                  { 'tag'  : 'li'                                           ,
                                    'attrs': {}                                             ,
                                    'nodes': [{ 'data': 'Item 2'                            ,
                                                'type': 'TEXT'                              }]},
                                  { 'tag'  : 'li'                                           ,
                                    'attrs': {}                                             ,
                                    'nodes': [{ 'data': 'Item 3'                            ,
                                                'type': 'TEXT'                              }]}]}

        with self.converter as _:
            result = _.convert(osbot_multi)

            assert len(result['child_nodes']) == 3
            assert result['child_nodes'][0]['text_nodes'][0]['data'] == 'Item 1'
            assert result['child_nodes'][1]['text_nodes'][0]['data'] == 'Item 2'
            assert result['child_nodes'][2]['text_nodes'][0]['data'] == 'Item 3'

    # ═══════════════════════════════════════════════════════════════════════════════
    # _is_text_node Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__is_text_node__with_type_text(self):                                           # Test detection with type: TEXT
        with self.converter as _:
            assert _._is_text_node({'data': 'hello', 'type': 'TEXT'}) == True
            assert _._is_text_node({'data': '', 'type': 'TEXT'})      == True

    def test__is_text_node__with_data_only(self):                                           # Test detection with just data field
        with self.converter as _:
            assert _._is_text_node({'data': 'hello'})                 == True

    def test__is_text_node__element_node(self):                                             # Test element nodes return False
        with self.converter as _:
            assert _._is_text_node({'tag': 'p', 'attrs': {}, 'nodes': []})            == False
            assert _._is_text_node({'tag': 'p', 'data': 'x', 'attrs': {}, 'nodes': []}) == False  # Has tag, so not text

    # ═══════════════════════════════════════════════════════════════════════════════
    # Integration Test with Full HTML
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_convert__full_html_structure(self):                                            # Test complete HTML document conversion
        osbot_full = { 'tag'  : 'html'                                                      ,
                       'attrs': {'lang': 'en'}                                              ,
                       'nodes': [{ 'tag'  : 'head'                                          ,
                                   'attrs': {}                                              ,
                                   'nodes': [{ 'tag'  : 'meta'                              ,
                                               'attrs': {'charset': 'UTF-8'}                ,
                                               'nodes': []                                  },
                                             { 'tag'  : 'title'                             ,
                                               'attrs': {}                                  ,
                                               'nodes': [{ 'data': 'Test Page'              ,
                                                           'type': 'TEXT'                   }]}]},
                                 { 'tag'  : 'body'                                          ,
                                   'attrs': {}                                              ,
                                   'nodes': [{ 'tag'  : 'h1'                                ,
                                               'attrs': {}                                  ,
                                               'nodes': [{ 'data': 'Hello World'            ,
                                                           'type': 'TEXT'                   }]},
                                             { 'tag'  : 'div'                               ,
                                               'attrs': {}                                  ,
                                               'nodes': [{ 'tag'  : 'p'                     ,
                                                           'attrs': {}                      ,
                                                           'nodes': [{ 'data': 'Paragraph 1',
                                                                       'type': 'TEXT'       }]},
                                                         { 'tag'  : 'p'                     ,
                                                           'attrs': {}                      ,
                                                           'nodes': [{ 'data': 'Paragraph 2',
                                                                       'type': 'TEXT'       }]}]}]}]}

        with self.converter as _:
            result = _.convert(osbot_full)

            assert result['tag']   == 'html'
            assert result['attrs'] == {'lang': 'en'}
            assert len(result['child_nodes']) == 2                                          # head and body

            head = result['child_nodes'][0]
            body = result['child_nodes'][1]

            assert head['tag'] == 'head'
            assert body['tag'] == 'body'

            title = head['child_nodes'][1]
            assert title['tag']                    == 'title'
            assert title['text_nodes'][0]['data']  == 'Test Page'

            h1 = body['child_nodes'][0]
            assert h1['tag']                       == 'h1'
            assert h1['text_nodes'][0]['data']     == 'Hello World'

            div = body['child_nodes'][1]
            assert len(div['child_nodes'])         == 2                                     # Two <p> elements

            p1 = div['child_nodes'][0]
            p2 = div['child_nodes'][1]
            assert p1['text_nodes'][0]['data']     == 'Paragraph 1'
            assert p2['text_nodes'][0]['data']     == 'Paragraph 2'