import pytest
from unittest                                                                                           import TestCase
from mgraph_ai_service_html_graph.service.html_graph__export.Html_Graph__Export__Service                import Html_Graph__Export__Service
from mgraph_ai_service_html_graph.service.html_graph__transformations.html_use_cases.Html_Use_Case__1   import Html_Use_Case__1
from mgraph_ai_service_html_graph.service.html_graph__transformations.html_use_cases.Html_Use_Case__2 import Html_Use_Case__2
from mgraph_ai_service_html_graph.service.html_graph__transformations.html_use_cases.Html_Use_Case__3 import Html_Use_Case__3
from mgraph_ai_service_html_graph.service.html_graph__transformations.html_use_cases.Html_Use_Case__Performance_Stats import Html_Use_Case__Performance_Stats
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html import Html_MGraph__Document__To__Html
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document import Html__To__Html_MGraph__Document
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document import Html_MGraph__Document
from mgraph_db.mgraph.MGraph                                                                            import MGraph
from osbot_utils.utils.Env                                                                              import get_env, load_dotenv
from osbot_utils.utils.Files                                                                            import path_combine


class test_Html_Use_Case__create_screenshot(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.load_env_vars()
        cls.use_case          = Html_Use_Case__1()
        #cls.use_case          = Html_Use_Case__2()
        cls.use_case          = Html_Use_Case__3()
        #cls.use_case          = Html_Use_Case__Performance_Stats()
        cls.transformation_name = cls.use_case.name
        cls.html_graph_service  = Html_Graph__Export__Service()
        cls.png_file            = path_combine(__file__, '../use-case.png')

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

    def test_use_case__simple_bold(self):                                   # Test with "simple bold"
        html   = HTML__BODY__SIMPLE_BOLD
        result = self.html_graph_service.export(html           = html,
                                                engine         = 'dot',
                                                transformation = self.transformation_name)
        self.dot_code = result.dot

    def test_use_case__nested_structure(self):                                        # Test with "nested HTML structure."
        html   = HTML__NESTED_STRUCTURE
        result = self.html_graph_service.export(html           = html,
                                                engine         = 'dot',
                                                transformation = self.transformation_name)
        self.dot_code = result.dot

    def test_use_case__multiple_layers(self):                                        # Test with "HTML__MULTIPLE_LAYERS."
        html   = HTML__MULTIPLE_LAYERS
        result = self.html_graph_service.export(html           = html,
                                                engine         = 'dot',
                                                transformation = self.transformation_name)
        self.dot_code = result.dot



    def test__html_round_trip__confirm(self):
        html   = HTML__NESTED_STRUCTURE
        with Html__To__Html_MGraph__Document().convert(html=html) as document:
            assert type(document) is Html_MGraph__Document

            mgraph_body = document.body_graph
            mgraph_body.mgraph.index().index_data.print_obj()

            html_roundtrip = Html_MGraph__Document__To__Html().convert(document=document)

            assert html == html_roundtrip

    def test__html_round_trip__change_body(self):
        html   = HTML__NESTED_STRUCTURE
        with Html__To__Html_MGraph__Document().convert(html=html) as document:
            assert type(document) is Html_MGraph__Document

            html_roundtrip = Html_MGraph__Document__To__Html().convert(document=document)

            #assert html == html_roundtrip
            print(html_roundtrip)


HTML__SIMPLE_BOLD       = """<div><b>hello</b></div>"""
HTML__BODY__SIMPLE_BOLD = """<html><body><div><b>hello</b></div></body></html>"""
HTML__MIXED_CONTENT     = """<div>aa <b>bb</b> cc</div>"""
HTML__MULTIPLE_TAGS     = """<div>A <b>B</b> C <i>D</i> E</div>"""
HTML__NESTED_STRUCTURE  = """\
<!DOCTYPE html>
<html>
    <body>
        <div>
            This is a <a href="">link</a> with some <b>bold</b> in the mix
        </div>
        <div>
            this is the <i>2nd div</i> in here
        </div>
    </body>
</html>
"""

HTML__MULTIPLE_LAYERS  = """\
<!DOCTYPE html>
<html>
    <body>
        <nav>
            <div>
                This is a <a href="">link</a> with some <b>bold</b> in the mix
            </div>
        </nav>
        <article>
            <div>
                <span>
                     <div>
                        content <b>with multiple</b> single parents
                    </div>
                </span>
            <div> 
            <div>
                this is the <i>nested div</i> inside the article
            </div>
        </article>            
    </body>
</html>
"""