import requests
import pytest
from unittest                                                                        import TestCase
from osbot_utils.helpers.duration.decorators.capture_duration                        import capture_duration
from osbot_utils.helpers.duration.decorators.print_duration                          import print_duration
from osbot_utils.utils.Files                                                         import path_combine, file_exists
from osbot_utils.utils.Env                                                           import load_dotenv, env_var_set
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                    import Html_MGraph
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__To__Png           import Html_MGraph__To__Png


class test_Html_MGraph__To__Png(TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        if env_var_set('URL__MGRAPH_DB_SERVERLESS') is False:
            pytest.skip('skipping create_screenshot test, because we need the URL__MGRAPH_DB_SERVERLESS to be configured')

        cls.html_mgraph_simple         = Html_MGraph.from_html(SIMPLE_HTML)
        cls.html_mgraph_nested         = Html_MGraph.from_html(NESTED_HTML)
        cls.target_folder              = path_combine(__file__         ,'../pngs'             )
        cls.target_file                = path_combine(cls.target_folder,'tests__html-mgraph__to_png.png')

        cls.html_mgraph_to_png__simple = Html_MGraph__To__Png(html_mgraph=cls.html_mgraph_simple, target_file=cls.target_file)
        cls.html_mgraph_to_png__nested = Html_MGraph__To__Png(html_mgraph=cls.html_mgraph_nested, target_file=cls.target_file)

    def test_to_png__html_mgraph_simple(self):
        with self.html_mgraph_to_png__simple as _:
            _.to_png()
            assert file_exists(self.target_file)

    def test_to_png__html_mgraph_nested(self):
        with self.html_mgraph_to_png__nested as _:
            _.to_png()
            assert file_exists(self.target_file)

    def test_html__to__png(self):
        html_mgraph__with_one_paragraph        = Html_MGraph.from_html(HTML__WITH_ONE_PARAGRAPH)
        html_mgraph_to_png__with_one_paragraph = Html_MGraph__To__Png(html_mgraph = html_mgraph__with_one_paragraph,
                                                                      target_file = self.target_file               )

        html_mgraph__with_some_tags         = Html_MGraph.from_html(HTML__WITH_SOME_TAGS)
        html_mgraph_to_png__with_some_tags  = Html_MGraph__To__Png(html_mgraph = html_mgraph__with_some_tags,
                                                                   target_file = self.target_file           )

    def test_from_html(self):
        html = HTML__BOOTSTRAP_EXAMPLE
        kwargs = dict(html        = html,
                      target_file = self.target_file)
        with Html_MGraph__To__Png.from_html(**kwargs) as _:
            _.to_png()

    def test_url_to_png(self):
        url, file_name  = "https://www.google.com/404" , "html-mgraph__google-404.png"
        file_name = "layout-tests.png"
        target_file = path_combine(self.target_folder, file_name)
        with print_duration(action_name="get html"):
            html = requests.get(url).text

        kwargs = dict(html        = html,
                      target_file = target_file)

        with print_duration(action_name="created_png"):
            with Html_MGraph__To__Png.from_html(**kwargs) as _:
                _.to_png()

    def test_url_to_dot_code(self):
        url = "https://www.google.com/404"
        with print_duration(action_name="got html"):
            html = requests.get(url).text

        html = HTML__WITH_SOME_TAGS

        with capture_duration(action_name="create dot_code") as duration:
            with Html_MGraph__To__Png.from_html(html=html) as _:
                dot_code = _.to_dot_code()

        #print(dot_code)

        stats = _.html_mgraph.stats()
        print()
        print(f"url     : " + url)
        print(f"duration: {duration.seconds}")
        print(f"size    : {len(dot_code)}")
        print(f"stats   : {stats}")


# ═══════════════════════════════════════════════════════════════════════════════
# Test Data
# ═══════════════════════════════════════════════════════════════════════════════

SIMPLE_HTML = '<div class="main" id="content">Hello World</div>'

NESTED_HTML = '''<div class="main" id="content">
    <h1>Title</h1>
    <p>Paragraph</p>
</div>'''

HTML__WITH_ONE_PARAGRAPH = "<html><body><p>an paragraph</p></body></html>"

HTML__WITH_SOME_TAGS = """<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>Test Page</title>
    </head>
    <body>
        <h1>Hello World</h1>
        <div>
            <p>This is a test paragraph.</p>
            <p>This is the 2nd paragraph.</p>
        </div>
        <div>
            another div with <b>a bold</b> element
        </div>
    </body>
</html>"""

HTML__BOOTSTRAP_EXAMPLE = """
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>Bootstrap Example</title>
        <link href="bootstrap.min.css" rel="stylesheet" />
    </head>
    <body>
        <nav class="navbar navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="#">Brand</a>
                <ul class="navbar-nav">
                    <li class="nav-item"><a class="nav-link" href="#">Home</a></li>
                </ul>
            </div>
        </nav>
    </body>
</html>
"""