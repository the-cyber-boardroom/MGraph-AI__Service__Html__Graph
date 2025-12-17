from unittest                                                                           import TestCase
from osbot_utils.testing.__                                                             import __
from osbot_utils.testing.__helpers                                                      import obj
from mgraph_db.mgraph.actions.MGraph__Data                                              import MGraph__Data
from mgraph_db.utils.testing.mgraph_test_ids                                            import mgraph_test_ids
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                       import Node_Id
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph                        import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__Tree_View import Html_MGraph__To__Tree_View
from tests.unit.service.html_graph.test_Html_MGraph                                     import SIMPLE_HTML_DICT
from tests.unit.service.html_graph__export.test_Html_MGraph__Data__Extractor            import COMPLEX_HTML_DICT


class test_Html_MGraph__To__Tree_View(TestCase):

    @classmethod
    def setUpClass(cls):
        with mgraph_test_ids() as _:
            cls.simple_html_dict    = SIMPLE_HTML_DICT
            cls.complex_html_dict   = COMPLEX_HTML_DICT
            cls.html_mgraph_simple  = Html_MGraph.from_html_dict(cls.simple_html_dict)
            cls.html_mgraph_complex = Html_MGraph.from_html_dict(cls.complex_html_dict)

    def test_setUp_Class(self):
        with self.html_mgraph_simple as _:
            assert type(_                    ) is Html_MGraph
            assert type(_.root_id            ) is Node_Id
            assert type(_.mgraph.data()      ) is MGraph__Data
            assert _.mgraph.data().nodes_ids() == ['c0000001', 'c0000002', 'c0000003' ,'c0000004' , 'c0000005']
            assert _.root_id                   == 'c0000001'

        with self.html_mgraph_complex as _:
            assert type(_                    ) is Html_MGraph
            assert type(_.root_id            ) is Node_Id
            assert type(_.mgraph.data()      ) is MGraph__Data
            assert _.mgraph.data().nodes_ids() == ['c0000006' , 'c0000007', 'c0000008' ,'c0000009' , 'c0000010',
                                                   'c0000011' , 'c0000012', 'c0000013', 'c0000014' , 'c0000015']

            assert _.root_id                   == 'c0000006'

    def test_export_tree(self):
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_simple) as _:
            assert type(_) is Html_MGraph__To__Tree_View
            tree_view = _.export_tree()
            assert obj(tree_view) == __(id       = 'c0000001',
                                        value    = 'c0000001',
                                        children = __(tag=[__(id='c0000002', value='div', children=__())],
                                                    attr=[__(id='c0000003', value='main', children=__()),
                                                          __(id='c0000004',
                                                             value='content',
                                                             children=__())],
                                                    text=[__(id='c0000005',
                                                             value='Hello World',
                                                             children=__())]))


    def test_export_as_text(self):
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_simple) as _:
            assert type(_) is Html_MGraph__To__Tree_View
            tree__as_text = _.export_tree__as_text()
            assert tree__as_text == """c0000001
    tag:
        div
    attr:
        main
        content
    text:
        Hello World"""

        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_complex) as _:
            assert _.export_tree__as_text() == ('c0000006\n'
                                                 '    tag:\n'
                                                 '        div\n'
                                                 '    attr:\n'
                                                 '        main\n'
                                                 '        content\n'
                                                 '    child:\n'
                                                 '        c0000010\n'
                                                 '            tag:\n'
                                                 '                h1\n'
                                                 '            text:\n'
                                                 '                Title\n'
                                                 '        c0000013\n'
                                                 '            tag:\n'
                                                 '                p\n'
                                                 '            text:\n'
                                                 '                Paragraph')


