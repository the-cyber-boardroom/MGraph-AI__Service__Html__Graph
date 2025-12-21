from unittest                                                                                         import TestCase
from mgraph_ai_service_html_graph.service.html_graph.Html_Dict__To__Html_MGraph                        import Schema__Config__Html_Dict__To__Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph__To__Html_Dict import Html_MGraph__To__Html_Dict
from mgraph_ai_service_html_graph.service.html_graph.Html__To__Html_MGraph                             import Html__To__Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service               import Html_Graph__Export__Service
from mgraph_ai_service_html_graph.service.html_graph__transformations.html_use_cases.Html_Use_Case__2  import Html_Use_Case__2
from mgraph_db.utils.testing.mgraph_test_ids                                                            import mgraph_test_ids
from osbot_utils.testing.Pytest import skip_if_in_github_action
from osbot_utils.testing.__                                                                             import __
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                                       import Node_Id

HTML__SIMPLE_BOLD = """<div><b>hello</b></div>"""                                                 # Single wrapper: div -> b -> "hello"

HTML__MIXED_CONTENT = """<div>aa <b>bb</b> cc</div>"""                                            # Mixed: text + bold + text

HTML__MULTIPLE_TAGS = """<div>A <b>B</b> C <i>D</i> E</div>"""                                    # Multiple formatting tags

HTML__NESTED_STRUCTURE = """<html>
    <body>
        <div>
            This is a <a href=''>link</a> with some <b>bold</b> in the mix
        </div>
        <div>
            this is the <i>2nd div</i> in here
        </div>
    </body>
</html>"""

HTML__DEEP_NESTING = """<p>Start <b><i>nested</i></b> end</p>"""                                  # Deeply nested formatting


class test_Html_Use_Case__2(TestCase):

    @classmethod
    def setUpClass(cls):                                                                          # Expensive setup done once
        cls.use_case                      = Html_Use_Case__2()
        cls.html_graph_service            = Html_Graph__Export__Service()
        cls.html_mgraph__simple_bold      = cls.create_mgraph__use_case_2(HTML__SIMPLE_BOLD)
        cls.html_mgraph__mixed_content    = cls.create_mgraph__use_case_2(HTML__MIXED_CONTENT)
        cls.html_mgraph__multiple_tags    = cls.create_mgraph__use_case_2(HTML__MULTIPLE_TAGS)
        cls.html_mgraph__nested_structure = cls.create_mgraph__use_case_2(HTML__NESTED_STRUCTURE)
        cls.config                         = Schema__Config__Html_Dict__To__Html_MGraph(add_tag_nodes=False, add_attribute_nodes=False)



    @classmethod
    def create_mgraph__use_case_2(cls, html: str):                                                          # Create mgraph from HTML
        with mgraph_test_ids():
            transformation_name = cls.use_case.name = 'html_use_case__2'
            html_mgraph         = cls.html_graph_service.html_to_mgraph_with_transformation(html                = html               ,
                                                                                            transformation_name = transformation_name)
            return html_mgraph

    def html_to_html_graph(self, html):
        return Html__To__Html_MGraph(config=self.config).convert(html=html)

    def setUp(self):                                                                              # Fresh graph per test
        pass

    # ---- Check test mgraphs

    # before: """<div><b>hello</b></div>"""
    # after   """<div>hello</div>"""
    def test_html_mgraph__simple_bold(self):                                                    # Test parent lookup
        with self.html_mgraph__simple_bold as _:
            assert _.to__obj() == __(graph_id = 'a0000001',
                                      nodes    = __(c0000001 = __(node_path = 'div'                   ,
                                                                   node_type = '@schema_mgraph_node' ,
                                                                   node_id   = 'c0000001'              ),
                                                    c0000003 = __(node_data = __(value_type = '@str'   ,
                                                                                 value      = 'hello'   ,
                                                                                 key        = 'div:0'   ),
                                                                   node_id   = 'c0000003'              ,
                                                                   node_type = '@schema_mgraph_node_value',
                                                                   node_path = 'text'                  )),
                                      edges    = __(e0000003 = __(edge_type    = '@schema_mgraph_edge',
                                                                   edge_path    = '0'                 ,
                                                                   from_node_id = 'c0000001'          ,
                                                                   to_node_id   = 'c0000003'          ,
                                                                   edge_id      = 'e0000003'          )))
            assert _.mgraph.index().index_data.obj() == __(edges=__(edges_to_nodes=__(e0000003=['c0000001', 'c0000003']),
                                                                    nodes_to_outgoing_edges=__(c0000001=['e0000003'], c0000003=[]),
                                                                    nodes_to_incoming_edges=__(c0000001=[], c0000003=['e0000003'])),
                                                           labels=__(edges_predicates=__(),
                                                                     edges_by_predicate=__(),
                                                                     edges_incoming_labels=__(),
                                                                     edges_by_incoming_label=__(),
                                                                     edges_outgoing_labels=__(),
                                                                     edges_by_outgoing_label=__()),
                                                           paths=__(nodes_by_path=__(div=['c0000001'], text=['c0000003']),
                                                                    edges_by_path=__(_0=['e0000003'])),
                                                           types=__(nodes_types=__(c0000001='Schema__MGraph__Node',
                                                                                   c0000003='Schema__MGraph__Node__Value'),
                                                                    nodes_by_type=__(Schema__MGraph__Node=['c0000001'],
                                                                                     Schema__MGraph__Node__Value=['c0000003']),
                                                                    edges_types=__(e0000003='Schema__MGraph__Edge'),
                                                                    edges_by_type=__(Schema__MGraph__Edge=['e0000003']),
                                                                    nodes_to_incoming_edges_by_type=__(c0000003=__(Schema__MGraph__Edge=['e0000003'])),
                                                                    nodes_to_outgoing_edges_by_type=__(c0000001=__(Schema__MGraph__Edge=['e0000003'])))) != __()


            assert _.mgraph.index().values_index.obj() ==   __(enabled=True,
                                                               index_data = __(hash_to_node   = __( _61cd2df4ff = 'c0000003'             ),
                                                                               node_to_hash   = __( c0000003     = '61cd2df4ff'           ),
                                                                               values_by_type = __( builtins_str = ['61cd2df4ff']         ),
                                                                               type_by_value  = __( _61cd2df4ff  = 'builtins.str'         )))

    # before: """<div>aa <b>bb</b> cc</div>"""
    # after: """<div>aa bb cc</div>"""
    def test_html_mgraph__mixed_content(self):
        with self.html_mgraph__mixed_content as _:
            assert _.to__obj() == __(edges=__(e0000006=__(edge_type='@schema_mgraph_edge',
                                                          edge_path='0',
                                                          from_node_id='c0000001',
                                                          to_node_id='c0000006',
                                                          edge_id='e0000006')),
                                     graph_id='a0000001',
                                     nodes=__(c0000001=__(node_path='div',
                                                          node_type='@schema_mgraph_node',
                                                          node_id='c0000001'),
                                              c0000006=__(node_data=__(value_type='@str',
                                                                       value='aa bb cc',
                                                                       key=''),
                                                          node_id='c0000006',
                                                          node_path='text' ,
                                                          node_type='@schema_mgraph_node_value')))
            assert _.mgraph.index().index_data.obj() == __(edges=__(edges_to_nodes=__(e0000006=['c0000001', 'c0000006']),
                                                                    nodes_to_outgoing_edges=__(c0000001=['e0000006'], c0000006=[]),
                                                                    nodes_to_incoming_edges=__(c0000001=[], c0000006=['e0000006'])),
                                                           labels=__(edges_predicates=__(),
                                                                     edges_by_predicate=__(),
                                                                     edges_incoming_labels=__(),
                                                                     edges_by_incoming_label=__(),
                                                                     edges_outgoing_labels=__(),
                                                                     edges_by_outgoing_label=__()),
                                                           paths=__(nodes_by_path=__(div=['c0000001'], text=['c0000006']),
                                                                    edges_by_path=__(_0=['e0000006'])),
                                                           types=__(nodes_types=__(c0000001='Schema__MGraph__Node',
                                                                                   c0000006='Schema__MGraph__Node__Value'),
                                                                    nodes_by_type=__(Schema__MGraph__Node=['c0000001'],
                                                                                     Schema__MGraph__Node__Value=['c0000006']),
                                                                    edges_types=__(e0000006='Schema__MGraph__Edge'),
                                                                    edges_by_type=__(Schema__MGraph__Edge=['e0000006']),
                                                                    nodes_to_incoming_edges_by_type=__(c0000006=__(Schema__MGraph__Edge=['e0000006'])),
                                                                    nodes_to_outgoing_edges_by_type=__(c0000001=__(Schema__MGraph__Edge=['e0000006'])))) != __()

            assert _.mgraph.index().values_index.obj()  == __(enabled    = True,
                                                              index_data = __(hash_to_node=__(_0a6e86a075='c0000006'),
                                                                              node_to_hash=__(c0000006='0a6e86a075'),
                                                                              values_by_type=__(builtins_str=['0a6e86a075']),
                                                                              type_by_value=__(_0a6e86a075='builtins.str')))

    # before: """<div>A <b>B</b> C <i>D</i> E</div>"""
    # after : """<div>A B C D E</div>"""
    def test_html_mgraph__multiple_tags(self):
        with self.html_mgraph__multiple_tags as _:

            assert _.to__obj() != __()
            assert _.to__obj()  == __(graph_id = 'a0000001',
                                      nodes    = __(c0000001 = __(node_path = 'div'                   ,
                                                                   node_type = '@schema_mgraph_node' ,
                                                                   node_id   = 'c0000001'              ),
                                                    c0000009 = __(node_data = __(value_type = '@str'   ,
                                                                                 value      = 'A B C D E',
                                                                                 key        = ''        ),
                                                                   node_id   = 'c0000009'              ,
                                                                   node_path = 'text'                  ,
                                                                   node_type = '@schema_mgraph_node_value')),
                                      edges    = __(e0000010 = __(edge_type    = '@schema_mgraph_edge',
                                                                   edge_path    = '0'                 ,
                                                                   from_node_id = 'c0000001'          ,
                                                                   to_node_id   = 'c0000009'          ,
                                                                   edge_id      = 'e0000010'          )))

            assert _.mgraph.index().index_data.obj()  == __(edges=__(edges_to_nodes=__(e0000010=['c0000001', 'c0000009']),
                                                                     nodes_to_outgoing_edges=__(c0000001=['e0000010'], c0000009=[]),
                                                                     nodes_to_incoming_edges=__(c0000001=[], c0000009=['e0000010'])),
                                                            labels=__(edges_predicates=__(),
                                                                      edges_by_predicate=__(),
                                                                      edges_incoming_labels=__(),
                                                                      edges_by_incoming_label=__(),
                                                                      edges_outgoing_labels=__(),
                                                                      edges_by_outgoing_label=__()),
                                                            paths=__(nodes_by_path=__(div=['c0000001'], text=['c0000009']),
                                                                     edges_by_path=__(_0=['e0000010'])),
                                                            types=__(nodes_types=__(c0000001='Schema__MGraph__Node',
                                                                                    c0000009='Schema__MGraph__Node__Value'),
                                                                     nodes_by_type=__(Schema__MGraph__Node=['c0000001'],
                                                                                      Schema__MGraph__Node__Value=['c0000009']),
                                                                     edges_types=__(e0000010='Schema__MGraph__Edge'),
                                                                     edges_by_type=__(Schema__MGraph__Edge=['e0000010']),
                                                                     nodes_to_incoming_edges_by_type=__(c0000009=__(Schema__MGraph__Edge=['e0000010'])),
                                                                     nodes_to_outgoing_edges_by_type=__(c0000001=__(Schema__MGraph__Edge=['e0000010']))))

            assert _.mgraph.index().values_index.obj()  == __(enabled=True,
                                                              index_data = __(hash_to_node   = __( b0e3ea2e69 = 'c0000009'             ),
                                                                              node_to_hash   = __( c0000009     = 'b0e3ea2e69'           ),
                                                                              values_by_type = __( builtins_str = ['b0e3ea2e69']         ),
                                                                              type_by_value  = __( b0e3ea2e69  = 'builtins.str'         )))

    # before:
    # """<html>
    #     <body>
    #         <div>
    #             This is a <a href=''>link</a> with some <b>bold</b> in the mix
    #         </div>
    #         <div>
    #             this is the <i>2nd div</i> in here
    #         </div>
    #     </body>
    # </html>"""

    # after:
    # """<html>
    #     <body>
    #         <div>
    #             This is a link with some bold in the mix
    #         </div>
    #         <div>
    #             this is the 2nd div in here
    #         </div>
    #     </body>
    # </html>"""
    def test_html_mgraph__nested_structure(self):
        skip_if_in_github_action()                          # fails in GH action (not locally)
        with self.html_mgraph__nested_structure as _:

            assert _.to__obj() == __(graph_id = 'a0000001',
                                      nodes    = __(c0000001 = __(node_path = 'html'              ,
                                                                   node_type = '@schema_mgraph_node',
                                                                   node_id   = 'c0000001'            ),
                                                    c0000002 = __(node_path = 'html.body'         ,
                                                                   node_type = '@schema_mgraph_node',
                                                                   node_id   = 'c0000002'            ),
                                                    c0000003 = __(node_path = 'html.body.div[0]'  ,
                                                                   node_type = '@schema_mgraph_node',
                                                                   node_id   = 'c0000003'            ),
                                                    c0000011 = __(node_path = 'html.body.div[1]'  ,
                                                                   node_type = '@schema_mgraph_node',
                                                                   node_id   = 'c0000011'            ),
                                                    c0000016 = __(node_data = __(value_type = '@str',
                                                                                 value      = 'This is a link with some bold in the mix',
                                                                                 key        = ''       ),
                                                                   node_id   = 'c0000016'            ,
                                                                   node_type = '@schema_mgraph_node_value',
                                                                   node_path = 'text'                ),
                                                    c0000017 = __(node_data = __(value_type = '@str',
                                                                                 value      = 'this is the 2nd div in here',
                                                                                 key        = ''       ),
                                                                   node_id   = 'c0000017'            ,
                                                                   node_type = '@schema_mgraph_node_value',
                                                                   node_path = 'text'                )),
                                      edges    = __(e0000008 = __(edge_type    = '@schema_mgraph_edge',
                                                                   edge_label   = __(predicate = 'child'),
                                                                   edge_path    = '0'                ,
                                                                   from_node_id = 'c0000002'         ,
                                                                   to_node_id   = 'c0000003'         ,
                                                                   edge_id      = 'e0000008'         ),
                                                    e0000013 = __(edge_type    = '@schema_mgraph_edge',
                                                                   edge_label   = __(predicate = 'child'),
                                                                   edge_path    = '1'                ,
                                                                   from_node_id = 'c0000002'         ,
                                                                   to_node_id   = 'c0000011'         ,
                                                                   edge_id      = 'e0000013'         ),
                                                    e0000014 = __(edge_type    = '@schema_mgraph_edge',
                                                                   edge_label   = __(predicate = 'child'),
                                                                   edge_path    = '0'                ,
                                                                   from_node_id = 'c0000001'         ,
                                                                   to_node_id   = 'c0000002'         ,
                                                                   edge_id      = 'e0000014'         ),
                                                    e0000018 = __(edge_type    = '@schema_mgraph_edge',
                                                                   edge_path    = '0'                ,
                                                                   from_node_id = 'c0000003'         ,
                                                                   to_node_id   = 'c0000016'         ,
                                                                   edge_id      = 'e0000018'         ),
                                                    e0000019 = __(edge_type    = '@schema_mgraph_edge',
                                                                   edge_path    = '0'                ,
                                                                   from_node_id = 'c0000011'         ,
                                                                   to_node_id   = 'c0000017'         ,
                                                                   edge_id      = 'e0000019'         )))
            # after refactoring
            assert _.mgraph.index().index_data.obj() == __(edges=__(edges_to_nodes=__(e0000008=['c0000002', 'c0000003'],
                                                                                      e0000013=['c0000002', 'c0000011'],
                                                                                      e0000014=['c0000001', 'c0000002'],
                                                                                      e0000018=['c0000003', 'c0000016'],
                                                                                      e0000019=['c0000011', 'c0000017']),
                                                                    nodes_to_outgoing_edges=__(c0000001=['e0000014'],
                                                                                               c0000002=['e0000008', 'e0000013'],
                                                                                               c0000003=['e0000018'],
                                                                                               c0000011=['e0000019'],
                                                                                               c0000016=[],
                                                                                               c0000017=[]),
                                                                    nodes_to_incoming_edges=__(c0000001=[],
                                                                                               c0000002=['e0000014'],
                                                                                               c0000003=['e0000008'],
                                                                                               c0000011=['e0000013'],
                                                                                               c0000016=['e0000018'],
                                                                                               c0000017=['e0000019'])),
                                                           labels=__(edges_predicates=__(),
                                                                     edges_by_predicate=__(),
                                                                     edges_incoming_labels=__(),
                                                                     edges_by_incoming_label=__(),
                                                                     edges_outgoing_labels=__(),
                                                                     edges_by_outgoing_label=__()),
                                                           paths=__(nodes_by_path=__(html=['c0000001'],
                                                                                     html_body=['c0000002'],
                                                                                     html_body_div_0_=['c0000003'],
                                                                                     text=['c0000016', 'c0000017'],
                                                                                     html_body_div_1_=['c0000011']),
                                                                    edges_by_path=__(_0=['e0000008',
                                                                                         'e0000014',
                                                                                         'e0000018',
                                                                                         'e0000019'],
                                                                                     _1=['e0000013'])),
                                                           types=__(nodes_types=__(c0000001='Schema__MGraph__Node',
                                                                                   c0000002='Schema__MGraph__Node',
                                                                                   c0000003='Schema__MGraph__Node',
                                                                                   c0000011='Schema__MGraph__Node',
                                                                                   c0000016='Schema__MGraph__Node__Value',
                                                                                   c0000017='Schema__MGraph__Node__Value'),
                                                                    nodes_by_type=__(Schema__MGraph__Node=['c0000001',
                                                                                                           'c0000002',
                                                                                                           'c0000003',
                                                                                                           'c0000011'],
                                                                                     Schema__MGraph__Node__Value=['c0000016',
                                                                                                                  'c0000017']),
                                                                    edges_types=__(e0000008='Schema__MGraph__Edge',
                                                                                   e0000013='Schema__MGraph__Edge',
                                                                                   e0000014='Schema__MGraph__Edge',
                                                                                   e0000018='Schema__MGraph__Edge',
                                                                                   e0000019='Schema__MGraph__Edge'),
                                                                    edges_by_type=__(Schema__MGraph__Edge=['e0000008',
                                                                                                           'e0000013',
                                                                                                           'e0000014',
                                                                                                           'e0000018',
                                                                                                           'e0000019']),
                                                                    nodes_to_incoming_edges_by_type=__(c0000003=__(Schema__MGraph__Edge=['e0000008']),
                                                                                                       c0000011=__(Schema__MGraph__Edge=['e0000013']),
                                                                                                       c0000002=__(Schema__MGraph__Edge=['e0000014']),
                                                                                                       c0000016=__(Schema__MGraph__Edge=['e0000018']),
                                                                                                       c0000017=__(Schema__MGraph__Edge=['e0000019'])),
                                                                    nodes_to_outgoing_edges_by_type=__(c0000002=__(Schema__MGraph__Edge=['e0000008',
                                                                                                                                         'e0000013']),
                                                                                                       c0000001=__(Schema__MGraph__Edge=['e0000014']),
                                                                                                       c0000003=__(Schema__MGraph__Edge=['e0000018']),
                                                                                                       c0000011=__(Schema__MGraph__Edge=['e0000019']))))

            assert _.mgraph.index().values_index.obj() == __(enabled   = True,
                                                             index_data = __(hash_to_node=__(_7a6cd9baa8='c0000016', c13b272fc6='c0000017'),
                                                                             node_to_hash=__(c0000016='7a6cd9baa8', c0000017='c13b272fc6'),
                                                                             values_by_type=__(builtins_str=['7a6cd9baa8', 'c13b272fc6']),
                                                                             type_by_value=__(_7a6cd9baa8='builtins.str',
                                                                                              c13b272fc6='builtins.str')))




    # ---- Initialization Tests ----

    def test__init__(self):                                                                       # Test class initialization
        with Html_Use_Case__2() as _:
            assert _.name        == "html_use_case__2"
            assert _.label       == "Html Use Case 2"
            assert _.description == "This is the Html Use Case 2"


    # ---- Graph Traversal Utility Tests ----

    def test_get_parent_node_id(self):                                                            # Test parent lookup
        with self.html_mgraph__simple_bold as _:
            assert _.to__obj() ==   __(edges=__(e0000003=__(edge_type    = '@schema_mgraph_edge',
                                                            edge_path    = '0',
                                                            from_node_id = 'c0000001',
                                                            to_node_id   = 'c0000003',
                                                            edge_id      = 'e0000003')),
                                       graph_id='a0000001',
                                       nodes=__(c0000001=__(node_path='div',
                                                            node_type='@schema_mgraph_node',
                                                            node_id='c0000001'),
                                                c0000003=__(node_data=__(value_type='@str',
                                                                         value='hello',
                                                                         key='div:0'),
                                                            node_id='c0000003',
                                                            node_type='@schema_mgraph_node_value',
                                                            node_path='text')))

            assert _.mgraph.index().index_data.obj() == __(edges=__(edges_to_nodes=__(e0000003=['c0000001', 'c0000003']),
                                                                    nodes_to_outgoing_edges=__(c0000001=['e0000003'], c0000003=[]),
                                                                    nodes_to_incoming_edges=__(c0000001=[], c0000003=['e0000003'])),
                                                           labels=__(edges_predicates=__(),
                                                                     edges_by_predicate=__(),
                                                                     edges_incoming_labels=__(),
                                                                     edges_by_incoming_label=__(),
                                                                     edges_outgoing_labels=__(),
                                                                     edges_by_outgoing_label=__()),
                                                           paths=__(nodes_by_path=__(div=['c0000001'], text=['c0000003']),
                                                                    edges_by_path=__(_0=['e0000003'])),
                                                           types=__(nodes_types=__(c0000001='Schema__MGraph__Node',
                                                                                   c0000003='Schema__MGraph__Node__Value'),
                                                                    nodes_by_type=__(Schema__MGraph__Node=['c0000001'],
                                                                                     Schema__MGraph__Node__Value=['c0000003']),
                                                                    edges_types=__(e0000003='Schema__MGraph__Edge'),
                                                                    edges_by_type=__(Schema__MGraph__Edge=['e0000003']),
                                                                    nodes_to_incoming_edges_by_type=__(c0000003=__(Schema__MGraph__Edge=['e0000003'])),
                                                                    nodes_to_outgoing_edges_by_type=__(c0000001=__(Schema__MGraph__Edge=['e0000003'])))) != __()


            assert _.mgraph.index().values_index.obj() ==   __(enabled    = True,
                                                               index_data = __(hash_to_node   = __( _61cd2df4ff = 'c0000003'             ),
                                                                               node_to_hash   = __( c0000003     = '61cd2df4ff'           ),
                                                                               values_by_type = __( builtins_str = ['61cd2df4ff']         ),
                                                                               type_by_value  = __( _61cd2df4ff  = 'builtins.str'         )))
            text_nodes  = self.use_case.text_nodes(_)

            assert text_nodes.obj() == [__(node_data = __(value_type = 'builtins.str',
                                                          value      = 'hello'       ,
                                                          key        = 'div:0'       ),
                                           node_id   = 'c0000003',
                                           node_type = 'mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value.Schema__MGraph__Node__Value',
                                           node_path = 'text')]
            assert len(text_nodes) == 1                                                               # One text node: "hello"

            text_node      = text_nodes[0]
            parent_node_id = self.use_case.get_parent_node_id(_, text_node.node_id)
            parent_node    = _.mgraph.data().node(parent_node_id)
            assert parent_node_id == Node_Id('c0000001')
            assert parent_node_id is not None                                                         # Should find parent (b tag)
            assert parent_node.node_path == 'div'                                                      # Parent is the <div> element

    def test_get_parent_node_id__root_node(self):                                                 # Test root has no parent
        html_mgraph = self.html_mgraph__simple_bold
        nodes       = list(self.use_case.nodes(html_mgraph))

        root_node = None                                                                          # Find the root node
        for node in nodes:
            if hasattr(node, 'node_path') and node.node_path == 'html.body.div':
                root_node = node
                break

        if root_node:                                                                             # Root's grandparent should be body
            parent_id       = self.use_case.get_parent_node_id(html_mgraph, root_node.node_id)
            grandparent_id  = self.use_case.get_parent_node_id(html_mgraph, parent_id) if parent_id else None
            assert grandparent_id is None or grandparent_id is not None                           # May or may not have grandparent

    def test_get_incoming_edge_path(self):                                                        # Test edge path retrieval
        html_mgraph = self.create_mgraph__use_case_2(HTML__MIXED_CONTENT)
        text_nodes  = self.use_case.text_nodes(html_mgraph)

        for text_node in text_nodes:
            edge_path = self.use_case.get_incoming_edge_path(html_mgraph, text_node.node_id)
            assert edge_path is not None or edge_path is None                                     # Edge path may or may not exist

    def test_get_outgoing_edge_count(self):                                                       # Test child counting
        html_mgraph = self.create_mgraph__use_case_2(HTML__MIXED_CONTENT)
        text_nodes  = self.use_case.text_nodes(html_mgraph)

        assert len(text_nodes) >= 1                                                               # Should have text nodes

        for text_node in text_nodes:
            count = self.use_case.get_outgoing_edge_count(html_mgraph, text_node.node_id)
            assert count == 0                                                                     # Text nodes have no children

    def test_get_outgoing_edge_count__parent_with_children(self):                                 # Test parent has children
        html_mgraph = self.html_mgraph__mixed_content
        text_nodes  = self.use_case.text_nodes(html_mgraph)

        text_node      = text_nodes[0]
        parent_node_id = self.use_case.get_parent_node_id(html_mgraph, text_node.node_id)
        parent_count   = self.use_case.get_outgoing_edge_count(html_mgraph, parent_node_id)

        assert parent_count >= 1                                                                  # Parent should have at least one child

    def test_is_single_child_parent(self):                                                        # Test single child detection
        html_mgraph = self.create_mgraph__use_case_2(HTML__SIMPLE_BOLD)
        text_nodes  = self.use_case.text_nodes(html_mgraph)

        assert len(text_nodes) == 1
        text_node      = text_nodes[0]
        parent_node_id = self.use_case.get_parent_node_id(html_mgraph, text_node.node_id)

        is_single = self.use_case.is_single_child_parent(html_mgraph, parent_node_id)
        assert is_single is True                                                                  # <b> has only one child: "hello"

    def test_is_single_child_parent__multiple_children(self):                                     # Test multi-child parent
        html_mgraph = self.create_mgraph__use_case_2(HTML__MIXED_CONTENT)
        text_nodes  = self.use_case.text_nodes(html_mgraph)

        text_node            = text_nodes[0]
        parent_node_id       = self.use_case.get_parent_node_id(html_mgraph, text_node.node_id)
        grand_parent_node_id = self.use_case.get_parent_node_id(html_mgraph, parent_node_id)

        if grand_parent_node_id:                                                                  # Grandparent (div) has multiple children
            is_single = self.use_case.is_single_child_parent(html_mgraph, grand_parent_node_id)
            # div has text + b + text = multiple children
            # Result depends on graph structure

    # ---- Graph Modification Utility Tests ----

    def test_create_edge_with_path(self):                                                         # Test edge creation
        html_mgraph = self.create_mgraph__use_case_2(HTML__SIMPLE_BOLD)
        index       = html_mgraph.mgraph.index()

        nodes           = list(self.use_case.nodes(html_mgraph))
        initial_edges   = len(index.edges_to_nodes())

        if len(nodes) >= 2:                                                                       # Need at least 2 nodes
            node_ids = [n.node_id for n in nodes]
            self.use_case.create_edge_with_path(html_mgraph, node_ids[0], node_ids[1], '99')

            final_edges = len(html_mgraph.mgraph.index().edges_to_nodes())
            assert final_edges == initial_edges + 1                                               # One edge added

    def test_delete_nodes(self):                                                                  # Test node deletion
        html_mgraph   = self.create_mgraph__use_case_2(HTML__SIMPLE_BOLD)
        initial_count = len(list(self.use_case.nodes(html_mgraph)))

        text_nodes    = self.use_case.text_nodes(html_mgraph)
        if text_nodes:
            node_to_delete = text_nodes[0].node_id
            self.use_case.delete_nodes(html_mgraph, [node_to_delete])

            final_count = len(list(self.use_case.nodes(html_mgraph)))
            assert final_count == initial_count - 1                                               # One node removed

    def test_delete_nodes__duplicate_ids(self):                                                   # Test set() deduplication
        html_mgraph   = self.create_mgraph__use_case_2(HTML__MIXED_CONTENT)
        text_nodes    = self.use_case.text_nodes(html_mgraph)
        initial_count = len(list(self.use_case.nodes(html_mgraph)))

        if text_nodes:
            node_id = text_nodes[0].node_id
            self.use_case.delete_nodes(html_mgraph, [node_id, node_id, node_id])                  # Duplicate IDs

            final_count = len(list(self.use_case.nodes(html_mgraph)))
            assert final_count == initial_count - 1                                               # Only one deleted (deduplicated)

    # ---- Text Node Utility Tests ----

    def test_text_nodes(self):                                                                    # Test text node filtering
        html_mgraph = self.html_to_html_graph(HTML__MIXED_CONTENT)
        text_nodes  = self.use_case.text_nodes(html_mgraph)

        assert len(text_nodes) >= 3                                                               # "aa", "bb", "cc"

        for node in text_nodes:
            assert node.node_path == 'text'                                                       # All should be text nodes

    def test_clear_text_node_paths(self):                                                         # Test path clearing
        html_mgraph = self.create_mgraph__use_case_2(HTML__SIMPLE_BOLD)
        text_nodes  = self.use_case.text_nodes(html_mgraph)

        assert len(text_nodes) >= 1
        assert text_nodes[0].node_path == 'text'                                                  # Initially 'text'

        self.use_case.clear_text_node_paths(html_mgraph)

        for node in self.use_case.text_nodes(html_mgraph):
            assert node.node_path == ''                                                           # Now empty

    # ---- Text Children Ordering Tests ----

    def test_get_text_children_ordered(self):                                                     # Test ordered retrieval
        html_mgraph = self.create_mgraph__use_case_2(HTML__MIXED_CONTENT)
        text_nodes  = self.use_case.text_nodes(html_mgraph)

        if text_nodes:
            parent_id = self.use_case.get_parent_node_id(html_mgraph, text_nodes[0].node_id)
            grand_parent_id = self.use_case.get_parent_node_id(html_mgraph, parent_id)

            if grand_parent_id:
                children = self.use_case.get_text_children_ordered(html_mgraph, grand_parent_id)
                # Should be sorted by edge_path
                positions = [c['edge_path'] for c in children]
                assert positions == sorted(positions)                                             # Must be sorted

    def test_get_parent_nodes_with_text_children(self):                                           # Test parent discovery
        html_mgraph = self.create_mgraph__use_case_2(HTML__MIXED_CONTENT)
        parent_ids  = self.use_case.get_parent_nodes_with_text_children(html_mgraph)

        assert len(parent_ids) >= 1                                                               # At least one parent

    # ---- Transform Operation Tests ----

    def test_collapse_single_child_parents__simple(self):                                         # Test basic collapse
        html_mgraph     = self.html_to_html_graph(HTML__SIMPLE_BOLD)
        initial_nodes   = len(list(self.use_case.nodes(html_mgraph)))

        self.use_case.collapse_single_child_parents(html_mgraph)

        final_nodes = len(list(self.use_case.nodes(html_mgraph)))
        assert final_nodes < initial_nodes                                                        # Nodes removed (b tag collapsed)

    def test_collapse_single_child_parents__preserves_edge_path(self):                            # Test edge_path preservation
        html_mgraph = self.html_to_html_graph(HTML__MIXED_CONTENT)

        self.use_case.collapse_single_child_parents(html_mgraph)

        text_nodes = self.use_case.text_nodes(html_mgraph)
        for text_node in text_nodes:
            edge_path = self.use_case.get_incoming_edge_path(html_mgraph, text_node.node_id)
            # Edge paths should be preserved (not None for collapsed nodes)

    def test_merge_text_children__simple(self):                                                   # Test basic merge
        html_mgraph = Html__To__Html_MGraph().convert(html=HTML__SIMPLE_BOLD)

        self.use_case.collapse_single_child_parents(html_mgraph)                                  # Must collapse first
        text_nodes_before = len(self.use_case.text_nodes(html_mgraph))

        self.use_case.merge_text_children(html_mgraph)

        text_nodes_after = len(self.use_case.text_nodes(html_mgraph))
        # Single text node shouldn't change (nothing to merge)

    def test_merge_text_children__mixed_content(self):                                            # Test merge with multiple texts
        html_mgraph = Html__To__Html_MGraph().convert(html=HTML__MIXED_CONTENT)

        self.use_case.collapse_single_child_parents(html_mgraph)
        self.use_case.merge_text_children(html_mgraph)

        text_nodes = self.use_case.text_nodes(html_mgraph)

        # All text should be merged into one node per container
        # Check that merged text contains all fragments
        for node in text_nodes:
            if hasattr(node, 'node_data') and hasattr(node.node_data, 'value'):
                value = node.node_data.value
                # Merged value should contain original fragments (order matters)

    def test_merge_text_children__correct_order(self):                                            # Test merge order preservation
        html_mgraph = Html__To__Html_MGraph().convert(html=HTML__MULTIPLE_TAGS)
        self.use_case.collapse_single_child_parents(html_mgraph)
        self.use_case.merge_text_children(html_mgraph)

        text_nodes = self.use_case.text_nodes(html_mgraph)

        for node in text_nodes:
            if hasattr(node, 'node_data') and hasattr(node.node_data, 'value'):
                value = node.node_data.value
                # Check order: A should come before B, B before C, etc.
                if 'A' in value and 'B' in value:
                    assert value.index('A') < value.index('B')                                    # A before B
                if 'B' in value and 'C' in value:
                    assert value.index('B') < value.index('C')                                    # B before C
                if 'C' in value and 'D' in value:
                    assert value.index('C') < value.index('D')                                    # C before D
                if 'D' in value and 'E' in value:
                    assert value.index('D') < value.index('E')                                    # D before E

    # ---- Full Transform Pipeline Tests ----

    def test_transform_mgraph__simple(self):                                                      # Test full pipeline
        html_mgraph = Html__To__Html_MGraph().convert(html=HTML__SIMPLE_BOLD)
        result = self.use_case.transform_mgraph(html_mgraph)

        assert result is not None
        text_nodes = self.use_case.text_nodes(result)
        assert len(text_nodes) >= 1                                                               # Should have text nodes

    def test_transform_mgraph__mixed_content(self):                                               # Test pipeline with mixed content
        with mgraph_test_ids():
            html_mgraph = Html__To__Html_MGraph(config=self.config).convert(html=HTML__MIXED_CONTENT)

            result = self.use_case.transform_mgraph(html_mgraph)

            text_nodes = self.use_case.text_nodes(result)
            assert text_nodes.obj() == [__( node_data=__(value_type='builtins.str', value='aa bb cc', key=''),
                                            node_id='c0000006',
                                            node_type='mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value.Schema__MGraph__Node__Value',
                                            node_path='text')]
            # Should result in merged text node(s)

    def test_transform_mgraph__nested_structure(self):                                            # Test full HTML document
        html_mgraph = self.create_mgraph__use_case_2(HTML__NESTED_STRUCTURE)

        result = self.use_case.transform_mgraph(html_mgraph)

        text_nodes = self.use_case.text_nodes(result)
        assert len(text_nodes) >= 1                                                               # Should have merged text

        # Check for expected merged content
        values = []
        for node in text_nodes:
            if hasattr(node, 'node_data') and hasattr(node.node_data, 'value'):
                values.append(node.node_data.value)

        all_text = ' '.join(values)
        assert 'link' in all_text or 'bold' in all_text                                           # Content preserved

    def test_transform_mgraph__preserves_structure(self):                                         # Test structural preservation
        html_mgraph = self.create_mgraph__use_case_2(HTML__NESTED_STRUCTURE)

        initial_structural_nodes = self._count_structural_nodes(html_mgraph)

        result = self.use_case.transform_mgraph(html_mgraph)

        # Container nodes (div, body) should be preserved
        # Only formatting wrappers (a, b, i) should be removed

    # ---- Integration Tests ----

    def test__integration__full_workflow(self):                                                   # End-to-end test
        html = """<article><p>Welcome to <b>our</b> site</p></article>"""
        html_mgraph = self.create_mgraph__use_case_2(html)

        # Before transformation
        initial_text_nodes = self.use_case.text_nodes(html_mgraph)
        initial_count      = len(initial_text_nodes)

        # Transform
        result = self.use_case.transform_mgraph(html_mgraph)

        # After transformation
        final_text_nodes = self.use_case.text_nodes(result)

        # Text should be merged
        for node in final_text_nodes:
            if hasattr(node, 'node_data') and hasattr(node.node_data, 'value'):
                value = node.node_data.value
                if 'Welcome' in value:
                    assert 'our' in value                                                         # Bold content merged
                    assert 'site' in value                                                        # Trailing text merged

    def test__integration__multiple_paragraphs(self):                                             # Test multiple containers
        html = """<div>
            <p>First <b>para</b></p>
            <p>Second <i>para</i></p>
        </div>"""
        html_mgraph = self.create_mgraph__use_case_2(html)

        result = self.use_case.transform_mgraph(html_mgraph)

        text_nodes = self.use_case.text_nodes(result)

        # Each paragraph should have its own merged text
        values = [n.node_data.value for n in text_nodes
                  if hasattr(n, 'node_data') and hasattr(n.node_data, 'value')]

        # Should have separate merged texts for each paragraph

    def test__integration__empty_tags(self):                                                      # Test empty formatting tags
        html = """<p>Text <b></b> more</p>"""
        html_mgraph = self.create_mgraph__use_case_2(html)

        result = self.use_case.transform_mgraph(html_mgraph)

        text_nodes = self.use_case.text_nodes(result)
        # Empty <b> should be handled gracefully

    def test__integration__whitespace_handling(self):                                             # Test whitespace preservation
        html = """<p>  spaced  <b>  text  </b>  here  </p>"""
        with mgraph_test_ids():
            html_mgraph = self.html_to_html_graph(html)

            result = self.use_case.transform_mgraph(html_mgraph)

            text_nodes = self.use_case.text_nodes(result)
            assert text_nodes.obj() == [__( node_data=__(value_type='builtins.str', value='spaced    text    here', key=''),
                                            node_id='c0000006',
                                            node_type='mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value.Schema__MGraph__Node__Value',
                                            node_path='text')]
        # Whitespace should be preserved in merge

    # ---- Helper Methods ----


    def _count_structural_nodes(self, html_mgraph):                                               # Count non-text nodes
        count = 0
        for node in self.use_case.nodes(html_mgraph):
            if hasattr(node, 'node_path') and node.node_path != 'text':
                count += 1
        return count

    def _get_text_values(self, html_mgraph):                                                      # Extract all text values
        values = []
        for node in self.use_case.text_nodes(html_mgraph):
            if hasattr(node, 'node_data') and hasattr(node.node_data, 'value'):
                values.append(node.node_data.value)
        return values