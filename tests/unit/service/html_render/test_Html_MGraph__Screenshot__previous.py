# import pytest
# from unittest                                                    import TestCase
# from osbot_utils.utils.Files                                     import file_exists, path_combine
# from osbot_utils.utils.Env                                       import env_var_set, load_dotenv
# from mgraph_db.mgraph.actions.MGraph__Screenshot                 import MGraph__Screenshot
# from osbot_utils.testing.__                                      import __
# from osbot_utils.testing.__helpers                               import obj
# from mgraph_db.mgraph.MGraph                                     import MGraph
# from osbot_utils.type_safe.Type_Safe                             import Type_Safe
# from osbot_utils.utils.Objects                                   import base_types
# from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph import Html_MGraph
# from tests.unit.service.html_graph.test_Html_MGraph              import SIMPLE_HTML_DICT
#
#
# class test_Html_MGraph__Screenshot(TestCase):
#
#     @classmethod
#     def setUpClass(cls) -> None:
#         cls.html_mgraph = Html_MGraph.from_html_dict(SIMPLE_HTML_DICT)
#
#     def test__setUpClass(self):
#         with self.html_mgraph as _:
#             assert type(_) is Html_MGraph
#             assert base_types(_)                 == [Type_Safe, object]
#             assert type(_.mgraph)                is MGraph
#             assert obj(_.mgraph.index().stats()) == __(index_data=__(edge_to_nodes=4,
#                                                                      edges_by_type=__(Schema__MGraph__Edge=4),
#                                                                      edges_by_path=__(_class=1, id=1, _0=1),
#                                                                      nodes_by_type=__(Schema__MGraph__Node=1,
#                                                                                       Schema__MGraph__Node__Value=4),
#                                                                      nodes_by_path=__(div=1,
#                                                                                       tag_div=1,
#                                                                                       attr_class=1,
#                                                                                       attr_id=1,
#                                                                                       text=1),
#                                                                      node_edge_connections=__(total_nodes=5,
#                                                                                               avg_incoming_edges=1,
#                                                                                               avg_outgoing_edges=1,
#                                                                                               max_incoming_edges=1,
#                                                                                               max_outgoing_edges=4)),
#                                                        summary=__(total_nodes=5,
#                                                                   total_edges=4,
#                                                                   total_predicates=0,
#                                                                   unique_node_paths=5,
#                                                                   unique_edge_paths=3,
#                                                                   nodes_with_paths=5,
#                                                                   edges_with_paths=3),
#                                                        paths=__(node_paths=__(div=1, tag_div=1, attr_class=1, attr_id=1, text=1),
#                                                                 edge_paths=__(_class=1, id=1, _0=1)))
#
#     def test_create_screenshot(self):
#         load_dotenv()
#         if env_var_set('URL__MGRAPH_DB_SERVERLESS') is False:
#             pytest.skip('skipping create_screenshot test, beause we need the URL__MGRAPH_DB_SERVERLESS to be configured')
#         with self.html_mgraph.mgraph.screenshot() as _:
#             assert type(_) is MGraph__Screenshot
#             target_file = path_combine(__file__,'../html-mgraph.png')
#             _.save_to(target_file).dot()
#             assert file_exists(target_file)