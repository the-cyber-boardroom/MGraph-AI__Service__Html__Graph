# import pytest
# from unittest                                                                                         import TestCase
#
# from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Html__Request import Schema__Graph__From_Html__Request
# from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service              import Html_Graph__Export__Service
# from mgraph_ai_service_html_graph.service.html_graph__transformations.Html_Use_Case__Dot_Export import Html_Use_Case__Dot_Export
# from mgraph_ai_service_html_graph.service.html_graph__transformations.html_use_cases.Html_Use_Case__1 import Html_Use_Case__1
# from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__To__Dot import Html_MGraph__To__Dot
# from mgraph_db.mgraph.MGraph import MGraph
# from osbot_utils.utils.Env import get_env, load_dotenv
# from osbot_utils.utils.Files import path_combine
#
#
# class test_Html_Use_Case__2__create_screenshot(TestCase):
#     @classmethod
#     def setUpClass(cls):                                                                            # One-time setup for all tests
#         load_dotenv()
#         if not get_env("URL__MGRAPH_DB_SERVERLESS"):
#             pytest.skip("Can't test the screenshots if env URL__MGRAPH_DB_SERVERLESS is not set")
#         cls.use_case_1          = Html_Use_Case__1()
#         cls.transformation_name = cls.use_case_1.name
#         cls.html_graph_service  = Html_Graph__Export__Service()
#         cls.png_file = path_combine(__file__,'../use-case-1.png')
#
#     def setUp(self):
#         self.dot_code = None
#
#     def tearDown(self):
#         if self.dot_code:
#             with MGraph().screenshot() as _:
#                 _.save_to(self.png_file)
#                 _.create_screenshot__from__dot_code(dot_code=self.dot_code)
#
#     def test_use_case_1__using__to_dot(self):
#         html          = HTML__BODY__SIMPLE_BOLD
#         request       = Schema__Graph__From_Html__Request(html=html)
#         response      = self.html_graph_service.to_dot(request      = request                    ,
#                                                      transformation = self.transformation_name)
#         self.dot_code = response.dot
#
#     def test_use_case_1__using__exporter(self):
#         html          = HTML__NESTED_STRUCTURE
#         graph_service = Html_Graph__Export__Service()
#         with Html_MGraph__To__Dot() as _:
#             html_mgraph   = graph_service.html_to_mgraph_with_transformation(html, self.transformation_name)
#
#             _.use_clusters = False
#             _.show_legend  = False
#             _.show_head    = False
#             _.show_scripts = False
#             _.show_styles  = False
#             _.show_attrs   = False
#             self.dot_code  = _.convert(html_mgraph)
#
#
#
#
# HTML__SIMPLE_BOLD       = """<div><b>hello</b></div>"""                                                 # Single wrapper: div -> b -> "hello"
# HTML__BODY__SIMPLE_BOLD = """<html><body><div><b>hello</b></div></body></html>"""
# HTML__MIXED_CONTENT     = """<div>aa <b>bb</b> cc</div>"""                                            # Mixed: text + bold + text
# HTML__MULTIPLE_TAGS     = """<div>A <b>B</b> C <i>D</i> E</div>"""                                    # Multiple formatting tags
# HTML__NESTED_STRUCTURE = """<html>
#     <body>
#         <div>
#             This is a <a href=''>link</a> with some <b>bold</b> in the mix
#         </div>
#         <div>
#             this is the <i>2nd div</i> in here
#         </div>
#     </body>
# </html>"""