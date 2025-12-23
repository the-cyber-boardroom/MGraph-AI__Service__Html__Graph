import pytest
from unittest                                                                                           import TestCase
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service                import Html_Graph__Export__Service
from mgraph_ai_service_html_graph.service.html_graph__transformations.html_use_cases.Html_Use_Case__1   import Html_Use_Case__1
from mgraph_db.mgraph.MGraph                                                                            import MGraph
from osbot_utils.utils.Env                                                                              import get_env, load_dotenv
from osbot_utils.utils.Files                                                                            import path_combine


class test_Html_Use_Case__1__create_screenshot(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.load_env_vars()
        cls.use_case_1          = Html_Use_Case__1()
        cls.transformation_name = cls.use_case_1.name
        cls.html_graph_service  = Html_Graph__Export__Service()
        cls.png_file            = path_combine(__file__, '../use-case-1.png')

    @classmethod
    def load_env_vars(cls):
        dot_env_file = path_combine(__file__, '../.use-cases.env')
        load_dotenv(dotenv_path=dot_env_file, override=True)
        if not get_env("URL__MGRAPH_DB_SERVERLESS"):
            pytest.skip("Can't test the screenshots if env URL__MGRAPH_DB_SERVERLESS is not set")

    def setUp(self):
        self.dot_code = None

    def tearDown(self):
        if self.dot_code:
            with MGraph().screenshot() as _:
                _.save_to(self.png_file)
                _.create_screenshot__from__dot_code(dot_code=self.dot_code)

    def test_use_case_1__using__export_service(self):                                   # Test with "simple bold"
        html   = HTML__BODY__SIMPLE_BOLD
        result = self.html_graph_service.export(html           = html,
                                                engine         = 'dot',
                                                transformation = self.transformation_name)
        self.dot_code = result.dot

    def test_use_case_1__nested_structure(self):                                        # Test with "nested HTML structure."
        html   = HTML__NESTED_STRUCTURE
        result = self.html_graph_service.export(html           = html,
                                                engine         = 'dot',
                                                transformation = self.transformation_name)
        self.dot_code = result.dot


HTML__SIMPLE_BOLD       = """<div><b>hello</b></div>"""
HTML__BODY__SIMPLE_BOLD = """<html><body><div><b>hello</b></div></body></html>"""
HTML__MIXED_CONTENT     = """<div>aa <b>bb</b> cc</div>"""
HTML__MULTIPLE_TAGS     = """<div>A <b>B</b> C <i>D</i> E</div>"""
HTML__NESTED_STRUCTURE  = """<html>
    <body>
        <div>
            This is a <a href=''>link</a> with some <b>bold</b> in the mix
        </div>
        <div>
            this is the <i>2nd div</i> in here
        </div>
    </body>
</html>"""