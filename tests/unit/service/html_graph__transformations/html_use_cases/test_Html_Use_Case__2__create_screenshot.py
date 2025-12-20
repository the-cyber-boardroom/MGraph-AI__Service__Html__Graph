from unittest                                                                                                               import TestCase

import pytest

from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service                        import Html_Graph__Export__Service
from mgraph_ai_service_html_graph.service.html_graph__transformations.html_use_cases.Html_Use_Case__2           import Html_Use_Case__2
from mgraph_ai_service_html_graph.service.html_graph__transformations.html_use_cases.Html_Use_Case__Dot_Export  import Html_Use_Case__Dot_Export
from osbot_utils.utils.Env import load_dotenv, get_env
from osbot_utils.utils.Files                                                                                    import path_combine
from tests.qa.dev.test_QA__Dev__Consolidate_Nodes                                                               import HTML__USE_CASE_3


class test_Html_Use_Case__2__create_screenshot(TestCase):
    @classmethod
    def setUpClass(cls):                                                                            # One-time setup for all tests
        if not get_env("URL__MGRAPH_DB_SERVERLESS"):
            pytest.skip("Can't test the screenshots if env URL__MGRAPH_DB_SERVERLESS is not set")
        cls.use_case_2          = Html_Use_Case__2()
        cls.transformation_name = cls.use_case_2.name
        cls.html_graph_service  = Html_Graph__Export__Service()

    def test_use_case_2(self):
        html                = HTML__USE_CASE_3
        html_mgraph = self.html_graph_service.html_to_mgraph_with_transformation(html                = html                    ,
                                                                                 transformation_name = self.transformation_name)
        dot_code = Html_Use_Case__Dot_Export(html_mgraph=html_mgraph).dot_string(self.transformation_name)

        load_dotenv()
        png_file = path_combine(__file__,'../use-case-2.png')

        with html_mgraph.mgraph.screenshot() as _:
            _.save_to(png_file)
            _.create_screenshot__from__dot_code(dot_code=dot_code)

        html_mgraph.mgraph.export().to__json__print()
