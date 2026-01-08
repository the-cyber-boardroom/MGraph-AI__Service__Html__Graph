# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Html__To__Html_Dict__With__Node_Ids
# Verifies node_id assignment to all element and text nodes during HTML parsing
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                           import TestCase
from osbot_utils.helpers.html.transformers.Html__To__Html_Dict                          import Html__To__Html_Dict
from osbot_utils.helpers.html.transformers.Html__To__Html_Dict                          import STRING__SCHEMA_TEXT
from Html__To__Html_Dict__With__Node_Ids                                               import Html__To__Html_Dict__With__Node_Ids
from Html__To__Html_Dict__With__Node_Ids                                               import STRING__NODE_ID
from osbot_utils.testing.Graph__Deterministic__Ids import graph_deterministic_ids
from osbot_utils.testing.__ import __
from osbot_utils.testing.__helpers import obj


class test_Html__To__Html_Dict__With__Node_Ids(TestCase):

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def collect_all_node_ids(self, node: dict) -> list:                         # Recursively collect all node_ids
        node_ids = []

        if STRING__NODE_ID in node:
            node_ids.append(node[STRING__NODE_ID])

        for child in node.get('nodes', []):
            if isinstance(child, dict):
                node_ids.extend(self.collect_all_node_ids(child))

        return node_ids

    # ═══════════════════════════════════════════════════════════════════════════
    # Core Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                     # Test initialization and inheritance
        with Html__To__Html_Dict__With__Node_Ids("<p>Test</p>") as _:
            assert type(_)                                is Html__To__Html_Dict__With__Node_Ids
            assert isinstance(_, Html__To__Html_Dict)     is True               # Inherits from parent
            assert _.html                                 == "<p>Test</p>"

    # ═══════════════════════════════════════════════════════════════════════════
    # convert() Method Tests - Node_Id Assignment
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert__simple_element(self):                                     # Test node_id on simple element
        html = "<p>Hello</p>"
        with graph_deterministic_ids():
            with Html__To__Html_Dict__With__Node_Ids(html) as _:
                result = _.convert()

                assert STRING__NODE_ID in result                                    # Element has node_id
                assert type(result[STRING__NODE_ID]) is str
                assert len(result[STRING__NODE_ID])  > 0
                assert result      == {'attrs': {},
                                       'node_id': 'f0000001',
                                       'nodes': [{'data': 'Hello', 'node_id': 'f0000002', 'type': 'TEXT'}],
                                       'tag': 'p'}
                assert obj(result) == __(tag='p',
                                         attrs=__(),
                                         nodes=[__(type='TEXT', data='Hello', node_id='f0000002')],
                                         node_id='f0000001')

    def test_convert__text_node_has_node_id(self):                              # Test node_id on text nodes
        html = "<p>Hello</p>"
        with Html__To__Html_Dict__With__Node_Ids(html) as _:
            with graph_deterministic_ids():
                result    = _.convert()
            text_node = result['nodes'][0]

            assert text_node['type']              == STRING__SCHEMA_TEXT
            assert text_node['data']              == 'Hello'
            assert STRING__NODE_ID in text_node                                 # Text node has node_id
            assert type(text_node[STRING__NODE_ID]) is str
            assert obj(result) == __(tag='p',
                                     attrs=__(),
                                     nodes=[__(type='TEXT', data='Hello', node_id='f0000002')],
                                     node_id='f0000001')

    def test_convert__element_and_text_different_ids(self):                     # Test element and text have different IDs
        html = "<p>Hello</p>"
        with Html__To__Html_Dict__With__Node_Ids(html) as _:
            result      = _.convert()
            element_id  = result[STRING__NODE_ID]
            text_id     = result['nodes'][0][STRING__NODE_ID]

            assert element_id != text_id                                        # Must be different

    def test_convert__nested_elements(self):                                    # Test nested elements all have node_ids
        html = "<div><p><span>Text</span></p></div>"
        with Html__To__Html_Dict__With__Node_Ids(html) as _:
            result   = _.convert()
            node_ids = self.collect_all_node_ids(result)

            assert len(node_ids) == 4                                           # div, p, span, text
            assert len(set(node_ids)) == 4                                      # All unique

    def test_convert__multiple_text_nodes(self):                                # Test multiple text nodes in mixed content
        html = "<p>Before<b>Bold</b>After</p>"
        with Html__To__Html_Dict__With__Node_Ids(html) as _:
            result   = _.convert()
            node_ids = self.collect_all_node_ids(result)

            assert len(node_ids) == 5                                           # p, "Before", b, "Bold", "After"
            assert len(set(node_ids)) == 5                                      # All unique

    # ═══════════════════════════════════════════════════════════════════════════
    # Void Element Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert__void_element_br(self):                                    # Test <br> gets node_id
        html = "<p>Before<br>After</p>"
        with Html__To__Html_Dict__With__Node_Ids(html) as _:
            with graph_deterministic_ids():
                result = _.convert()
            nodes  = result['nodes']

            assert nodes[0]['type']           == STRING__SCHEMA_TEXT            # "Before"
            assert nodes[1]['tag']            == 'br'                           # <br>
            assert nodes[2]['type']           == STRING__SCHEMA_TEXT            # "After"

            assert STRING__NODE_ID in nodes[0]                                  # Text has node_id
            assert STRING__NODE_ID in nodes[1]                                  # <br> has node_id
            assert STRING__NODE_ID in nodes[2]                                  # Text has node_id
            assert obj(result) == __(tag='p',
                                     attrs=__(),
                                     nodes=[__(type='TEXT', data='Before', node_id='f0000002'),
                                            __(tag='br', attrs=__(), nodes=[], node_id='f0000003'),
                                            __(type='TEXT', data='After', node_id='f0000004')],
                                     node_id='f0000001')

    def test_convert__void_element_img(self):                                   # Test <img> gets node_id
        html = "<p>Text<img src='test.jpg'>More</p>"
        with Html__To__Html_Dict__With__Node_Ids(html) as _:
            with graph_deterministic_ids():
                result = _.convert()
            nodes  = result['nodes']

            img_node = nodes[1]
            assert img_node['tag'] == 'img'
            assert STRING__NODE_ID in img_node                                  # <img> has node_id
            assert obj(result)     == __(tag='p',
                                         attrs=__(),
                                         nodes=[__(type='TEXT', data='Text', node_id='f0000002'),
                                                __(tag='img', attrs=__(src='test.jpg'), nodes=[], node_id='f0000003'),
                                                __(type='TEXT', data='More', node_id='f0000004')],
                                         node_id='f0000001')

    def test_convert__void_element_meta(self):                                  # Test <meta> gets node_id
        html = "<head><meta charset='utf-8'></head>"
        with Html__To__Html_Dict__With__Node_Ids(html) as _:
            with graph_deterministic_ids():
                result    = _.convert()
            meta_node = result['nodes'][0]

            assert meta_node['tag'] == 'meta'
            assert STRING__NODE_ID  in meta_node                                 # <meta> has node_id
            assert obj(result)      == __(tag='head',
                                          attrs=__(),
                                          nodes=[__(tag='meta',
                                                    attrs=__(charset='utf-8'),
                                                    nodes=[],
                                                    node_id='f0000002')],
                                          node_id='f0000001')

    # ═══════════════════════════════════════════════════════════════════════════
    # Uniqueness Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert__all_node_ids_unique(self):                                # Test all node_ids are unique
        html = """<div>
            <p>Text 1</p>
            <p>Text 2</p>
            <p>Text 3</p>
        </div>"""
        with Html__To__Html_Dict__With__Node_Ids(html) as _:
            with graph_deterministic_ids():
                result   = _.convert()

            node_ids = self.collect_all_node_ids(result)

            assert len(node_ids) == len(set(node_ids))                          # All unique
            assert node_ids     == ['f0000001', 'f0000002', 'f0000003', 'f0000004',
                                    'f0000005', 'f0000006', 'f0000007']
            assert obj(result)   == __(tag='div',
                                       attrs=__(),
                                       nodes=[__(tag='p',
                                                 attrs=__(),
                                                 nodes=[__(type='TEXT', data='Text 1', node_id='f0000003')],
                                                 node_id='f0000002'),
                                              __(tag='p',
                                                 attrs=__(),
                                                 nodes=[__(type='TEXT', data='Text 2', node_id='f0000005')],
                                                 node_id='f0000004'),
                                              __(tag='p',
                                                 attrs=__(),
                                                 nodes=[__(type='TEXT', data='Text 3', node_id='f0000007')],
                                                 node_id='f0000006')],
                                       node_id='f0000001')

    def test_convert__complex_structure_unique_ids(self):                       # Test complex nested structure
        html = """<div class="outer">
            <header>
                <h1>Title</h1>
                <nav><a href="#">Link</a></nav>
            </header>
            <main>
                <article>
                    <p>Paragraph with <strong>bold</strong> and <em>italic</em>.</p>
                </article>
            </main>
        </div>"""
        with Html__To__Html_Dict__With__Node_Ids(html) as _:
            with graph_deterministic_ids():
                result   = _.convert()
            node_ids = self.collect_all_node_ids(result)

            assert len(node_ids) > 10                                           # Many nodes
            assert len(node_ids) == len(set(node_ids))                          # All unique
            assert obj(result)   == __(tag='div',
                                       attrs=__(_class='outer'),
                                       nodes=[__(tag='header',
                                                 attrs=__(),
                                                 nodes=[__(tag='h1',
                                                           attrs=__(),
                                                           nodes=[__(type='TEXT',
                                                                     data='Title',
                                                                     node_id='f0000004')],
                                                           node_id='f0000003'),
                                                        __(tag='nav',
                                                           attrs=__(),
                                                           nodes=[__(tag='a',
                                                                     attrs=__(href='#'),
                                                                     nodes=[__(type='TEXT',
                                                                               data='Link',
                                                                               node_id='f0000007')],
                                                                     node_id='f0000006')],
                                                           node_id='f0000005')],
                                                 node_id='f0000002'),
                                              __(tag='main',
                                                 attrs=__(),
                                                 nodes=[__(tag='article',
                                                           attrs=__(),
                                                           nodes=[__(tag='p',
                                                                     attrs=__(),
                                                                     nodes=[__(type='TEXT',
                                                                               data='Paragraph with ',
                                                                               node_id='f0000011'),
                                                                            __(tag='strong',
                                                                               attrs=__(),
                                                                               nodes=[__(type='TEXT',
                                                                                         data='bold',
                                                                                         node_id='f0000013')],
                                                                               node_id='f0000012'),
                                                                            __(type='TEXT',
                                                                               data=' and ',
                                                                               node_id='f0000014'),
                                                                            __(tag='em',
                                                                               attrs=__(),
                                                                               nodes=[__(type='TEXT',
                                                                                         data='italic',
                                                                                         node_id='f0000016')],
                                                                               node_id='f0000015'),
                                                                            __(type='TEXT',
                                                                               data='.',
                                                                               node_id='f0000017')],
                                                                     node_id='f0000010')],
                                                           node_id='f0000009')],
                                                 node_id='f0000008')],
                                       node_id='f0000001')

    # ═══════════════════════════════════════════════════════════════════════════
    # Backward Compatibility Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert__backward_compatible_structure(self):                      # Test structure matches parent except node_id
        html = "<div class='test'>Hello</div>"

        with graph_deterministic_ids():
            result_old = Html__To__Html_Dict(html).convert()
            result_new = Html__To__Html_Dict__With__Node_Ids(html).convert()

        assert result_old['tag']   == result_new['tag']                         # Same tag
        assert result_old['attrs'] == result_new['attrs']                       # Same attrs
        assert len(result_old['nodes']) == len(result_new['nodes'])             # Same node count

        old_text = result_old['nodes'][0]                                       # Text nodes match
        new_text = result_new['nodes'][0]
        assert old_text['type'] == new_text['type']
        assert old_text['data'] == new_text['data']
        assert obj(result_old)  == __(tag     = 'div',
                                      attrs   = __(_class   = 'test'    ),
                                      nodes   = [__(type    = 'TEXT'    ,
                                                    data    = 'Hello'   )])
        assert obj(result_new)  == __(tag     = 'div',
                                      attrs   = __(_class   = 'test'    ),
                                      nodes   = [__(type    = 'TEXT'    ,
                                                    data    = 'Hello'   ,
                                                    node_id = 'f0000002')],
                                      node_id = 'f0000001')

    def test_convert__only_adds_node_id_field(self):                            # Test only node_id is added
        html = "<p>Test</p>"

        result_old = Html__To__Html_Dict(html).convert()
        result_new = Html__To__Html_Dict__With__Node_Ids(html).convert()

        old_keys = set(result_old.keys())
        new_keys = set(result_new.keys())

        assert new_keys - old_keys == {STRING__NODE_ID}                         # Only node_id added

    # ═══════════════════════════════════════════════════════════════════════════
    # Round-Trip Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert__preserves_structure_for_round_trip(self):                 # Test structure supports round-trip
        html = "<div><p>Hello <b>World</b></p></div>"
        with Html__To__Html_Dict__With__Node_Ids(html) as _:
            with graph_deterministic_ids():
                result = _.convert()

            assert result['tag']                                      == 'div'          # Structure preserved
            assert result['nodes'][0]['tag']                          == 'p'
            assert result['nodes'][0]['nodes'][0]['data']             == 'Hello '
            assert result['nodes'][0]['nodes'][1]['tag']              == 'b'
            assert result['nodes'][0]['nodes'][1]['nodes'][0]['data'] == 'World'
            assert obj(result)                                        == __(tag='div',
                                                                            attrs=__(),
                                                                            nodes=[__(tag='p',
                                                                                      attrs=__(),
                                                                                      nodes=[__(type='TEXT', data='Hello ', node_id='f0000003'),
                                                                                             __(tag='b',
                                                                                                attrs=__(),
                                                                                                nodes=[__(type='TEXT',
                                                                                                          data='World',
                                                                                                          node_id='f0000005')],
                                                                                                node_id='f0000004')],
                                                                                      node_id='f0000002')],
                                                                            node_id='f0000001')

    # ═══════════════════════════════════════════════════════════════════════════
    # Edge Cases
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert__empty_element(self):                                      # Test empty element gets node_id
        html = "<div></div>"
        with Html__To__Html_Dict__With__Node_Ids(html) as _:
            with graph_deterministic_ids():
                result = _.convert()

            assert STRING__NODE_ID in result
            assert result['nodes'] == []                                        # No children
            assert obj(result) == __(tag='div', attrs=__(), nodes=[], node_id='f0000001')

    def test_convert__whitespace_only_text_ignored(self):                       # Test whitespace-only text has no node_id
        html = "<div>   </div>"
        with Html__To__Html_Dict__With__Node_Ids(html) as _:
            with graph_deterministic_ids():
                result = _.convert()

            assert STRING__NODE_ID in result                                    # Element has node_id
            assert result['nodes'] == []                                        # Whitespace stripped
            assert obj(result) == __(tag='div', attrs=__(), nodes=[], node_id='f0000001')

    def test_convert__attributes_preserved(self):                               # Test attributes not affected
        html = "<div id='main' class='container' data-value='123'>Text</div>"
        with Html__To__Html_Dict__With__Node_Ids(html) as _:
            with graph_deterministic_ids():
                result = _.convert()

            assert result['attrs']['id']         == 'main'
            assert result['attrs']['class']      == 'container'
            assert result['attrs']['data-value'] == '123'
            assert STRING__NODE_ID               in result                                    # node_id also present
            assert obj(result)                   == __(tag='div',
                                                       attrs=__(id='main', _class='container', data_value='123'),
                                                       nodes=[__(type='TEXT', data='Text', node_id='f0000002')],
                                                       node_id='f0000001')


    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Test
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert__realistic_html(self):                                     # Test with realistic HTML structure
        html = """<!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Test Page</title>
            </head>
            <body>
                <div class="container">
                    <h1>Welcome</h1>
                    <p>This is a <a href="#">link</a> in a paragraph.</p>
                </div>
            </body>
        </html>"""
        with Html__To__Html_Dict__With__Node_Ids(html) as _:
            with graph_deterministic_ids():
                result   = _.convert()
            node_ids = self.collect_all_node_ids(result)

            assert result['tag']           == 'html'                            # Parsed correctly
            assert STRING__NODE_ID in result                                    # Has node_id
            assert len(node_ids)           > 10                                 # Many nodes
            assert len(node_ids)          == len(set(node_ids))                          # All unique
            assert obj(result)            == __(tag='html',
                                                attrs=__(lang='en'),
                                                nodes=[__(tag='head',
                                                          attrs=__(),
                                                          nodes=[__(tag='meta',
                                                                    attrs=__(charset='UTF-8'),
                                                                    nodes=[],
                                                                    node_id='f0000003'),
                                                                 __(tag='title',
                                                                    attrs=__(),
                                                                    nodes=[__(type='TEXT',
                                                                              data='Test Page',
                                                                              node_id='f0000005')],
                                                                    node_id='f0000004')],
                                                          node_id='f0000002'),
                                                       __(tag='body',
                                                          attrs=__(),
                                                          nodes=[__(tag='div',
                                                                    attrs=__(_class='container'),
                                                                   nodes=[__(tag='h1',
                                                                             attrs=__(),
                                                                             nodes=[__(type='TEXT',
                                                                                       data='Welcome',
                                                                                       node_id='f0000009')],
                                                                             node_id='f0000008'),
                                                                          __(tag='p',
                                                                             attrs=__(),
                                                                             nodes=[__(type='TEXT',
                                                                                       data='This is a ',
                                                                                       node_id='f0000011'),
                                                                                    __(tag='a',
                                                                                       attrs=__(href='#'),
                                                                                       nodes=[__(type='TEXT',
                                                                                                 data='link',
                                                                                                 node_id='f0000013')],
                                                                                       node_id='f0000012'),
                                                                                    __(type='TEXT',
                                                                                       data=' in a paragraph.',
                                                                                       node_id='f0000014')],
                                                                             node_id='f0000010')],
                                                                   node_id='f0000007')],
                                                         node_id='f0000006')],
                                               node_id='f0000001')