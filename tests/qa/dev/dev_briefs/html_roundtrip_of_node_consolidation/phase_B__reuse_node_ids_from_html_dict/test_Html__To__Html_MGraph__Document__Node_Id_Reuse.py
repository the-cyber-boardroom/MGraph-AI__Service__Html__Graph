# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Html__To__Html_MGraph__Document__Node_Id_Reuse - Node_Id Reuse from Html_Dict
# Verifies that node_ids from Html_Dict are preserved in the MGraph Document
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                       import TestCase

from osbot_utils.testing.Graph__Deterministic__Ids import graph_deterministic_ids
from osbot_utils.testing.__ import __
from osbot_utils.testing.__helpers import obj
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                   import Node_Id
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document  import Html_MGraph__Document
from Html__To__Html_MGraph__Document__Node_Id_Reuse                                 import Html__To__Html_MGraph__Document__Node_Id_Reuse
from Html__To__Html_Dict__With__Node_Ids                                            import Html__To__Html_Dict__With__Node_Ids
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                    import Obj_Id


class test_Html__To__Html_MGraph__Document__Node_Id_Reuse(TestCase):       # Tests for node_id reuse from Html_Dict

    # ═══════════════════════════════════════════════════════════════════════════
    # _generate_node_id() Method Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__generate_node_id__reuses_from_dict(self):                    # Test node_id reuse when present in dict
        custom_id = Obj_Id()
        with Html__To__Html_MGraph__Document__Node_Id_Reuse() as _:
            node_dict = {'tag': 'div', 'node_id': custom_id}
            result    = _._generate_node_id(node_dict)

            assert type(result)   is Node_Id
            assert str(result)    == custom_id                             # Reused from dict

    def test__generate_node_id__generates_when_missing(self):              # Test node_id generation when not in dict
        with Html__To__Html_MGraph__Document__Node_Id_Reuse() as _:
            node_dict = {'tag': 'div', 'attrs': {}}                        # No node_id
            result    = _._generate_node_id(node_dict)

            assert type(result)   is Node_Id
            assert len(str(result)) > 0                                    # Generated

    def test__generate_node_id__generates_when_none(self):                 # Test node_id generation when dict is None
        with Html__To__Html_MGraph__Document__Node_Id_Reuse() as _:
            result = _._generate_node_id(None)

            assert type(result)   is Node_Id
            assert len(str(result)) > 0                                    # Generated

    def test__generate_node_id__generates_when_empty_dict(self):           # Test node_id generation with empty dict
        with Html__To__Html_MGraph__Document__Node_Id_Reuse() as _:
            result = _._generate_node_id({})

            assert type(result)   is Node_Id
            assert len(str(result)) > 0                                    # Generated

    # ═══════════════════════════════════════════════════════════════════════════
    # convert() - assigns node ids
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert(self):                           # Test convert() still works
        html = "<html><head></head><body><div class='test'>Hello</div></body></html>"

        with Html__To__Html_MGraph__Document__Node_Id_Reuse() as _:
            with graph_deterministic_ids():
                doc = _.convert(html)

            assert type(doc)                is Html_MGraph__Document
            assert obj(doc.head_graph.to_json()) == __(nodes=__(c0000002=__(node_type='@schema_mgraph_node', node_id='c0000002'),
                                                                f0000002=__(node_path='head',
                                                                            node_type='@schema_mgraph_node',
                                                                            node_id='f0000002')),
                                                       edges=__(),
                                                       root_id='f0000002')
            assert obj(doc.body_graph.to_json()) == __(nodes=__(c0000003=__(node_type='@schema_mgraph_node', node_id='c0000003'),
                                                                f0000003=__(node_path='body',
                                                                            node_type='@schema_mgraph_node',
                                                                            node_id='f0000003'),
                                                                f0000004=__(node_path='body.div',
                                                                            node_type='@schema_mgraph_node',
                                                                            node_id='f0000004'),
                                                                f0000005=__(node_data=__(value_type='@str',
                                                                                         value='Hello',
                                                                                         key='f0000004:0'),
                                                                            node_id='f0000005',
                                                                            node_type='@schema_mgraph_node_value',
                                                                            node_path='text')),
                                                       edges=__(e0000012=__(edge_type='@schema_mgraph_edge',
                                                                            edge_label=__(predicate='child'),
                                                                            edge_path='0',
                                                                            from_node_id='f0000003',
                                                                            to_node_id='f0000004',
                                                                            edge_id='e0000012'),
                                                                e0000018=__(edge_type='@schema_mgraph_edge',
                                                                            edge_label=__(predicate='text'),
                                                                            edge_path='0',
                                                                            from_node_id='f0000004',
                                                                            to_node_id='f0000005',
                                                                            edge_id='e0000018')),
                                                       root_id='f0000003')

            with graph_deterministic_ids():
                html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()
            assert obj(html_dict) == __(tag='html',
                                        attrs=__(),
                                        nodes=[__(tag='head', attrs=__(), nodes=[], node_id='f0000002'),
                                               __(tag='body',
                                                  attrs=__(),
                                                  nodes=[__(tag='div',
                                                            attrs=__(_class='test'),
                                                            nodes=[__(type='TEXT',
                                                                      data='Hello',
                                                                      node_id='f0000005')],
                                                            node_id='f0000004')],
                                                  node_id='f0000003')],
                                        node_id='f0000001')


    # ═══════════════════════════════════════════════════════════════════════════
    # convert_from_dict() - Node_Id Reuse Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert_from_dict__reuses_head_node_id(self):                 # Test head node_id is reused
        html_dict = {'tag'  : 'html'                              ,
                     'attrs': {}                                  ,
                     'nodes': [{'tag'    : 'head'                 ,
                                'node_id': 'a0000001'       ,
                                'attrs'  : {}                     ,
                                'nodes'  : []                     },
                               {'tag'    : 'body'                 ,
                                'attrs'  : {}                     ,
                                'nodes'  : []                     }]}

        with Html__To__Html_MGraph__Document__Node_Id_Reuse() as _:
            doc = _.convert_from_dict(html_dict)

            assert str(doc.head_graph.root_id) == 'a0000001' # Reused

    def test_convert_from_dict__reuses_body_node_id(self):                 # Test body node_id is reused
        html_dict = {'tag'  : 'html'                              ,
                     'attrs': {}                                  ,
                     'nodes': [{'tag'    : 'head'                 ,
                                'attrs'  : {}                     ,
                                'nodes'  : []                     },
                               {'tag'    : 'body'                 ,
                                'node_id': 'a0000001'             ,
                                'attrs'  : {}                     ,
                                'nodes'  : []                     }]}

        with Html__To__Html_MGraph__Document__Node_Id_Reuse() as _:
            doc = _.convert_from_dict(html_dict)

            assert str(doc.body_graph.root_id) == 'a0000001' # Reused

    def test_convert_from_dict__reuses_element_node_id(self):              # Test nested element node_id is reused
        html_dict = {'tag'  : 'html'                              ,
                     'attrs': {}                                  ,
                     'nodes': [{'tag'  : 'head', 'attrs': {}, 'nodes': []},
                               {'tag'  : 'body'                   ,
                                'attrs': {}                       ,
                                'nodes': [{'tag'    : 'div'       ,
                                           'node_id': 'a0000001',
                                           'attrs'  : {}          ,
                                           'nodes'  : []          }]}]}

        with Html__To__Html_MGraph__Document__Node_Id_Reuse() as _:
            doc  = _.convert_from_dict(html_dict)
            divs = doc.get_elements_by_tag('div')

            assert len(divs)      == 1
            assert str(divs[0])   == 'a0000001'                          # Reused

    def test_convert_from_dict__reuses_text_node_id(self):                 # Test text node_id is reused
        html_dict = {'tag'  : 'html'                              ,
                     'attrs': {}                                  ,
                     'nodes': [{'tag': 'head', 'attrs': {}, 'nodes': []},
                               {'tag'  : 'body'                   ,
                                'attrs': {}                       ,
                                'nodes': [{'tag'  : 'p'           ,
                                           'attrs': {}            ,
                                           'nodes': [{'type'   : 'TEXT'        ,
                                                      'data'   : 'Hello World' ,
                                                      'node_id': 'a0000001' }]}]}]}

        with Html__To__Html_MGraph__Document__Node_Id_Reuse() as _:
            with graph_deterministic_ids():
                doc = _.convert_from_dict(html_dict)
            assert obj(doc.body_graph.to_json()) == __(nodes=__(c0000003=__(node_type='@schema_mgraph_node', node_id='c0000003'),
                                                                c0000018=__(node_path='body',
                                                                            node_type='@schema_mgraph_node',
                                                                            node_id='c0000018'),
                                                                c0000020=__(node_path='body.p',
                                                                            node_type='@schema_mgraph_node',
                                                                            node_id='c0000020'),
                                                                a0000001=__(node_data=__(value_type='@str',
                                                                                         value='Hello World',
                                                                                         key='c0000020:0'),
                                                                            node_id='a0000001',
                                                                            node_type='@schema_mgraph_node_value',
                                                                            node_path='text')),
                                                       edges=__(e0000012=__(edge_type='@schema_mgraph_edge',
                                                                            edge_label=__(predicate='child'),
                                                                            edge_path='0',
                                                                            from_node_id='c0000018',
                                                                            to_node_id='c0000020',
                                                                            edge_id='e0000012'),
                                                                e0000015=__(edge_type='@schema_mgraph_edge',
                                                                            edge_label=__(predicate='text'),
                                                                            edge_path='0',
                                                                            from_node_id='c0000020',
                                                                            to_node_id='a0000001',
                                                                            edge_id='e0000015')),
                                                       root_id='c0000018')


    # ═══════════════════════════════════════════════════════════════════════════
    # Backward Compatibility Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert_from_dict__backward_compatible_no_node_ids(self):     # Test works without node_ids
        html_dict = {'tag'  : 'html'                              ,
                     'attrs': {'lang': 'en'}                      ,
                     'nodes': [{'tag': 'head', 'attrs': {}, 'nodes': []},
                               {'tag': 'body', 'attrs': {}, 'nodes': []}]}

        with Html__To__Html_MGraph__Document__Node_Id_Reuse() as _:
            doc = _.convert_from_dict(html_dict)

            assert type(doc)                is Html_MGraph__Document
            assert doc.head_graph.root_id   is not None                    # Generated
            assert doc.body_graph.root_id   is not None                    # Generated

    def test_convert__backward_compatible(self):                           # Test convert() still works
        html = "<html><head></head><body></body></html>"

        with Html__To__Html_MGraph__Document__Node_Id_Reuse() as _:
            doc = _.convert(html)

            assert type(doc)                is Html_MGraph__Document
            assert doc.head_graph.root_id   is not None
            assert doc.body_graph.root_id   is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # Mixed Node_Id Tests (Some Present, Some Missing)
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert_from_dict__mixed_node_ids(self):                      # Test mix of present and missing node_ids
        html_dict = {'tag'  : 'html'                              ,
                     'attrs': {}                                  ,
                     'nodes': [{'tag'    : 'head'                 ,
                                'node_id': 'a0000001'             ,          # Has node_id
                                'attrs'  : {}                     ,
                                'nodes'  : []                     },
                               {'tag'  : 'body'                   ,          # No node_id
                                'attrs': {}                       ,
                                'nodes': [{'tag'    : 'div'       ,
                                           'node_id': 'a0000002',          # Has node_id
                                           'attrs'  : {}          ,
                                           'nodes'  : []          },
                                          {'tag'  : 'span'        ,          # No node_id
                                           'attrs': {}            ,
                                           'nodes': []            }]}]}

        with Html__To__Html_MGraph__Document__Node_Id_Reuse() as _:
            with graph_deterministic_ids():
                doc = _.convert_from_dict(html_dict)

            assert str(doc.head_graph.root_id) == 'a0000001'            # Reused
            assert doc.body_graph.root_id      is not None                 # Generated

            divs  = doc.get_elements_by_tag('div')
            spans = doc.get_elements_by_tag('span')

            assert str(divs[0])   == 'a0000002'                          # Reused
            assert spans[0]       is not None                              # Generated
            assert obj(doc.head_graph.to_json()) == __(nodes=__(c0000002=__(node_type='@schema_mgraph_node', node_id='c0000002'),
                                                                a0000001=__(node_path='head',
                                                                            node_type='@schema_mgraph_node',
                                                                            node_id='a0000001')),
                                                       edges=__(),
                                                       root_id='a0000001')
            assert obj(doc.body_graph.to_json()) == __(nodes=__(c0000003=__(node_type='@schema_mgraph_node', node_id='c0000003'),
                                                                c0000017=__(node_path='body',
                                                                            node_type='@schema_mgraph_node',
                                                                            node_id='c0000017'),
                                                                a0000002=__(node_path='body.div',
                                                                            node_type='@schema_mgraph_node',
                                                                            node_id='a0000002'),
                                                                c0000020=__(node_path='body.span',
                                                                            node_type='@schema_mgraph_node',
                                                                            node_id='c0000020')),
                                                       edges=__(e0000012=__(edge_type='@schema_mgraph_edge',
                                                                            edge_label=__(predicate='child'),
                                                                            edge_path='0',
                                                                            from_node_id='c0000017',
                                                                            to_node_id='a0000002',
                                                                            edge_id='e0000012'),
                                                                e0000015=__(edge_type='@schema_mgraph_edge',
                                                                            edge_label=__(predicate='child'),
                                                                            edge_path='1',
                                                                            from_node_id='c0000017',
                                                                            to_node_id='c0000020',
                                                                            edge_id='e0000015')),
                                                       root_id='c0000017')

    # ═══════════════════════════════════════════════════════════════════════════
    # End-to-End Pipeline Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_full_pipeline__html_to_dict_with_node_ids_to_mgraph(self):    # Test full pipeline preserves node_ids
        html = "<html><head></head><body><div class='test'>Hello</div></body></html>"

        # Step 1: Parse HTML to dict WITH node_ids
        html_dict = Html__To__Html_Dict__With__Node_Ids(html).convert()


        # Capture the node_ids from the dict
        body_dict     = html_dict['nodes'][1]                              # body
        div_dict      = body_dict['nodes'][0]                              # div
        body_node_id  = body_dict.get('node_id')
        div_node_id   = div_dict.get('node_id')

        assert body_node_id is not None                                    # Has node_id from parser
        assert div_node_id  is not None                                    # Has node_id from parser

        # Step 2: Convert to MGraph Document
        with Html__To__Html_MGraph__Document__Node_Id_Reuse() as _:
            doc = _.convert_from_dict(html_dict)

            # Verify node_ids are reused
            assert str(doc.body_graph.root_id) == body_node_id             # Same as dict
            
            divs = doc.get_elements_by_tag('div')
            assert len(divs)    == 1
            assert str(divs[0]) == div_node_id                             # Same as dict

    def test_full_pipeline__node_ids_shared_across_graphs(self):           # Test node_ids shared in attrs_graph
        html_dict = {'tag'  : 'html'                              ,
                     'attrs': {}                                  ,
                     'nodes': [{'tag': 'head', 'attrs': {}, 'nodes': []},
                               {'tag'  : 'body'                   ,
                                'attrs': {}                       ,
                                'nodes': [{'tag'    : 'div'       ,
                                           'node_id': 'a0000001',
                                           'attrs'  : {'class': 'container'},
                                           'nodes'  : []          }]}]}

        with Html__To__Html_MGraph__Document__Node_Id_Reuse() as _:
            doc = _.convert_from_dict(html_dict)

            # Node_id should be same in body_graph and attrs_graph
            divs_in_body  = doc.get_elements_by_tag('div')
            divs_in_attrs = doc.attrs_graph.get_elements_by_tag('div')

            assert len(divs_in_body)  == 1
            assert len(divs_in_attrs) == 1
            assert str(divs_in_body[0])  == 'a0000001'
            assert str(divs_in_attrs[0]) == 'a0000001'
            assert divs_in_body[0] == divs_in_attrs[0]                     # Same Node_Id object

    # ═══════════════════════════════════════════════════════════════════════════
    # Complex Structure Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_convert_from_dict__deep_nesting_preserves_node_ids(self):     # Test deep nesting preserves all node_ids
        html_dict = {'tag'  : 'html'                                       ,
                     'attrs': {}                                           ,
                     'nodes': [{'tag': 'head', 'attrs': {}, 'nodes': []}   ,
                               {'tag'    : 'body'                          ,
                                'node_id': 'a0000001'                      ,
                                'attrs'  : {}                              ,
                                'nodes'  : [{'tag'    : 'div'              ,
                                             'node_id': 'a0000002'          ,
                                             'attrs'  : {}                 ,
                                             'nodes'  : [{'tag'    : 'p'   ,
                                                          'node_id': 'a0000003',
                                                          'attrs'  : {}    ,
                                                          'nodes'  : [{'tag'    : 'span'    ,
                                                                       'node_id': 'a0000004',
                                                                       'attrs'  : {}        ,
                                                                       'nodes'  : []        }]}]}]}]}

        with Html__To__Html_MGraph__Document__Node_Id_Reuse() as _:
            with graph_deterministic_ids():
                doc = _.convert_from_dict(html_dict)

            assert str(doc.body_graph.root_id) == 'a0000001'

            divs  = doc.get_elements_by_tag('div')
            ps    = doc.get_elements_by_tag('p')
            spans = doc.get_elements_by_tag('span')

            assert str(divs[0])  == 'a0000002'
            assert str(ps[0])    == 'a0000003'
            assert str(spans[0]) == 'a0000004'
            assert type(doc) is Html_MGraph__Document
            assert obj(doc.body_graph.to_json())   == __(nodes = __(c0000003 = __(node_type = '@schema_mgraph_node',
                                                                                  node_id   = 'c0000003'             ),
                                                                    a0000001 = __(node_path = 'body',
                                                                                  node_type = '@schema_mgraph_node',
                                                                                  node_id   = 'a0000001'             ),
                                                                    a0000002 = __(node_path = 'body.div',
                                                                                  node_type = '@schema_mgraph_node',
                                                                                  node_id   = 'a0000002'             ),
                                                                    a0000003 = __(node_path = 'body.div.p',
                                                                                  node_type = '@schema_mgraph_node',
                                                                                  node_id   = 'a0000003'             ),
                                                                    a0000004 = __(node_path = 'body.div.p.span',
                                                                                  node_type = '@schema_mgraph_node',
                                                                                  node_id   = 'a0000004'             )),
                                                         edges = __(e0000012 = __(edge_type   = '@schema_mgraph_edge',
                                                                                  edge_label  = __(predicate = 'child'),
                                                                                  edge_path   = '0',
                                                                                  from_node_id= 'a0000001',
                                                                                  to_node_id  = 'a0000002',
                                                                                  edge_id     = 'e0000012'           ),
                                                                    e0000015 = __(edge_type   = '@schema_mgraph_edge',
                                                                                  edge_label  = __(predicate = 'child'),
                                                                                  edge_path   = '0',
                                                                                  from_node_id= 'a0000002',
                                                                                  to_node_id  = 'a0000003',
                                                                                  edge_id     = 'e0000015'           ),
                                                                    e0000018 = __(edge_type   = '@schema_mgraph_edge',
                                                                                  edge_label  = __(predicate = 'child'),
                                                                                  edge_path   = '0',
                                                                                  from_node_id= 'a0000003',
                                                                                  to_node_id  = 'a0000004',
                                                                                  edge_id     = 'e0000018'           )),
                                                            root_id = 'a0000001')
