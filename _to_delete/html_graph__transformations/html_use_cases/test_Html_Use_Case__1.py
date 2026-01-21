from unittest                                                                                                   import TestCase

import pytest

from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service                        import Html_Graph__Export__Service
from mgraph_ai_service_html_graph.service.html_graph__transformations.html_use_cases.Html_Use_Case__1           import Html_Use_Case__1
from mgraph_ai_service_html_graph.service.html_graph__transformations.html_use_cases.Html_Use_Case__Dot_Export  import Html_Use_Case__Dot_Export
from osbot_utils.utils.Env import load_dotenv, get_env
from osbot_utils.utils.Files                                                                                    import path_combine
from tests.qa.dev.test_QA__Dev__Consolidate_Nodes                                                               import HTML__USE_CASE_3


class test_Html_Use_Case__1(TestCase):
    @classmethod
    def setUpClass(cls):                                                                            # One-time setup for all tests
        if not get_env("URL__MGRAPH_DB_SERVERLESS"):
            pytest.skip("Can't test the screenshots if env URL__MGRAPH_DB_SERVERLESS is not set")
        cls.use_case_1          = Html_Use_Case__1()
        cls.transformation_name = cls.use_case_1.name
        cls.html_graph_service  = Html_Graph__Export__Service()

    def test_use_case_1(self):
        html                = HTML__USE_CASE_3
        # html__osbot_dict    = Html__To__Html_Dict            (html=html).convert()
        # html_dict           = Html_Dict__OSBot__To__Html_Dict(         ).convert(osbot_dict=html__osbot_dict)
        # html_mgraph__config = Schema__Config__Html_Dict__To__Html_MGraph()
        # html_mgraph         = Html_MGraph.from_html_dict(html_dict = html_dict,
        #                                                  config    = html_mgraph__config)
        #
        # mgraph              = html_mgraph.mgraph
        html_mgraph = self.html_graph_service.html_to_mgraph_with_transformation(html                = html                    ,
                                                                                 transformation_name = self.transformation_name)
        dot_code = Html_Use_Case__Dot_Export(html_mgraph=html_mgraph).dot_string(self.transformation_name)

        load_dotenv()
        png_file = path_combine(__file__,'../use-case-1.png')

        with html_mgraph.mgraph.screenshot() as _:
            _.save_to(png_file)
            _.create_screenshot__from__dot_code(dot_code=dot_code)
        #    _.dot()
