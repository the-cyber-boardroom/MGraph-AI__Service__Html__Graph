import pytest
from unittest                                                                        import TestCase

import requests
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path

from osbot_utils.helpers.html.transformers.Html__To__Html_Dict                       import Html__To__Html_Dict
from osbot_utils.utils.Files                                                         import path_combine, file_exists
from osbot_utils.utils.Env                                                           import load_dotenv, env_var_set
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph                     import Html_MGraph
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__To__Png           import Html_MGraph__To__Png
from mgraph_ai_service_html_graph.service.html_graph.Html_Dict__OSBot__To__Html_Dict import Html_Dict__OSBot__To__Html_Dict
from tests.unit.service.html_graph.test_Html_MGraph                                  import SIMPLE_HTML_DICT, NESTED_HTML_DICT


class test_Html_MGraph__To__Png(TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        if env_var_set('URL__MGRAPH_DB_SERVERLESS') is False:
            pytest.skip('skipping create_screenshot test, because we need the URL__MGRAPH_DB_SERVERLESS to be configured')

        cls.html_mgraph_simple         = Html_MGraph.from_html_dict(SIMPLE_HTML_DICT)
        cls.html_mgraph_nested         = Html_MGraph.from_html_dict(NESTED_HTML_DICT)
        cls.target_folder              = path_combine(__file__         ,'../pngs'             )
        cls.target_file                = path_combine(cls.target_folder,'html-mgraph.png')   # '/tmp/test.png'

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
        html_dict__osbot__with_one_paragraph   = Html__To__Html_Dict(html=HTML__WITH_ONE_PARAGRAPH).convert()
        html_dict__with_one_paragraph          = Html_Dict__OSBot__To__Html_Dict().convert(html_dict__osbot__with_one_paragraph)
        html_mgraph__with_one_paragraph        = Html_MGraph.from_html_dict(html_dict__with_one_paragraph)
        html_mgraph_to_png__with_one_paragraph = Html_MGraph__To__Png(html_mgraph = html_mgraph__with_one_paragraph,
                                                                      target_file = self.target_file               )

        #html_mgraph_to_png__with_one_paragraph.to_png()

        html_dict__osbot__with_some_tags    = Html__To__Html_Dict(html=HTML__WITH_SOME_TAGS    ).convert()
        html_dict__with_some_tags           = Html_Dict__OSBot__To__Html_Dict().convert(html_dict__osbot__with_some_tags    )
        html_mgraph__with_some_tags         = Html_MGraph.from_html_dict(html_dict__with_some_tags)
        html_mgraph_to_png__with_some_tags  = Html_MGraph__To__Png(html_mgraph = html_mgraph__with_some_tags,
                                                                   target_file = self.target_file           )
        #html_mgraph_to_png__with_some_tags.to_png()

    def test_from_html(self):
        html = HTML__BOOTSTRAP_EXAMPLE # HTML__WITH_SOME_TAGS
        kwargs = dict(html        = html,
                      target_file = self.target_file)
        with Html_MGraph__To__Png.from_html(**kwargs) as _:
            _.to_png()

    def test_url_to_png(self):
        url, file_name  = "https://www.google.com/404" , "html-mgraph__google-404.png"
        #url, file_name  = "https://www.google.com/"    , "html-mgraph__google.png"
        url, file_name  = "https://akeia.ai"          , "html-mgraph__akeia_ai.png"
        #url, file_name  = "https://text.npr.org/"          , "html-mgraph__text.npr.org.png"
        #url, file_name  = "https://news.bbc.co.uk/404"     , "html-mgraph__bbc-404.png"
        file_name = "layout-tests.png"
        target_file = path_combine(self.target_folder, file_name)
        html = requests.get(url).text
        #print(html)

        kwargs = dict(html        = html,
                      target_file = target_file)
        with Html_MGraph__To__Png.from_html(**kwargs) as _:
            _.to_png()



    def test_html__to__html_dict__using_osbot_utils(self):

        html_dict__osbot__with_one_paragraph = {'attrs': {},
                                         'nodes': [{'attrs': {},
                                                    'nodes': [{'attrs': {},
                                                               'nodes': [{'data': 'an paragraph', 'type': 'TEXT'}],
                                                               'tag': 'p'}],
                                                    'tag': 'body'}],
                                         'tag': 'html'}
        html_dict__osbot__with_some_tags     = {'attrs': {'lang': 'en'},
                                         'nodes': [{'attrs': {},
                                                    'nodes': [{'attrs': {'charset': 'UTF-8'},
                                                               'nodes': [],
                                                               'tag': 'meta'},
                                                              {'attrs': {},
                                                               'nodes': [{'data': 'Test Page', 'type': 'TEXT'}],
                                                               'tag': 'title'}],
                                                    'tag': 'head'},
                                                   {'attrs': {},
                                                    'nodes': [{'attrs': {},
                                                               'nodes': [{'data': 'Hello World', 'type': 'TEXT'}],
                                                               'tag': 'h1'},
                                                              {'attrs': {},
                                                               'nodes': [{'attrs': {},
                                                                          'nodes': [{'data': 'This is a test '
                                                                                             'paragraph.',
                                                                                     'type': 'TEXT'}],
                                                                          'tag': 'p'},
                                                                         {'attrs': {},
                                                                          'nodes': [{'data': 'This is the 2nd '
                                                                                             'paragraph.',
                                                                                     'type': 'TEXT'}],
                                                                          'tag': 'p'}],
                                                               'tag': 'div'},
                                                              {'attrs': {},
                                                               'nodes': [{'data': '\n            another div with ',
                                                                          'type': 'TEXT'},
                                                                         {'attrs': {},
                                                                          'nodes': [{'data': 'a bold', 'type': 'TEXT'}],
                                                                          'tag': 'b'},
                                                                         {'data': ' element\n        ',
                                                                          'type': 'TEXT'}],
                                                               'tag': 'div'}],
                                                    'tag': 'body'}],
                                         'tag': 'html'}

        html_dict__with_one_paragraph = Html_Dict__OSBot__To__Html_Dict().convert(html_dict__osbot__with_one_paragraph)
        html_dict__with_some_tags     = Html_Dict__OSBot__To__Html_Dict().convert(html_dict__osbot__with_some_tags    )

        assert Html__To__Html_Dict(html=HTML__WITH_ONE_PARAGRAPH).convert() == html_dict__osbot__with_one_paragraph
        assert Html__To__Html_Dict(html=HTML__WITH_SOME_TAGS    ).convert() == html_dict__osbot__with_some_tags

        assert html_dict__with_one_paragraph == {'attrs': {},
                                                 'child_nodes': [{'attrs': {},
                                                                  'child_nodes': [{'attrs': {},
                                                                                   'child_nodes': [],
                                                                                   'position': 0,
                                                                                   'tag': 'p',
                                                                                   'text_nodes': [{'data': 'an paragraph',
                                                                                                   'position': 0}]}],
                                                                  'position': 0,
                                                                  'tag': 'body',
                                                                  'text_nodes': []}],
                                                 'tag': 'html',
                                                 'text_nodes': []}

        assert html_dict__with_some_tags == {'attrs': {'lang': 'en'},
                                             'child_nodes': [{'attrs': {},
                                                              'child_nodes': [{'attrs': {'charset': 'UTF-8'},
                                                                               'child_nodes': [],
                                                                               'position': 0,
                                                                               'tag': 'meta',
                                                                               'text_nodes': []},
                                                                              {'attrs': {},
                                                                               'child_nodes': [],
                                                                               'position': 1,
                                                                               'tag': 'title',
                                                                               'text_nodes': [{'data': 'Test Page',
                                                                                               'position': 0}]}],
                                                              'position': 0,
                                                              'tag': 'head',
                                                              'text_nodes': []},
                                                             {'attrs': {},
                                                              'child_nodes': [{'attrs': {},
                                                                               'child_nodes': [],
                                                                               'position': 0,
                                                                               'tag': 'h1',
                                                                               'text_nodes': [{'data': 'Hello World',
                                                                                               'position': 0}]},
                                                                              {'attrs': {},
                                                                               'child_nodes': [{'attrs': {},
                                                                                                'child_nodes': [],
                                                                                                'position': 0,
                                                                                                'tag': 'p',
                                                                                                'text_nodes': [{'data': 'This '
                                                                                                                        'is '
                                                                                                                        'a '
                                                                                                                        'test '
                                                                                                                        'paragraph.',
                                                                                                                'position': 0}]},
                                                                                               {'attrs': {},
                                                                                                'child_nodes': [],
                                                                                                'position': 1,
                                                                                                'tag': 'p',
                                                                                                'text_nodes': [{'data': 'This '
                                                                                                                        'is '
                                                                                                                        'the '
                                                                                                                        '2nd '
                                                                                                                        'paragraph.',
                                                                                                                'position': 0}]}],
                                                                               'position': 1,
                                                                               'tag': 'div',
                                                                               'text_nodes': []},
                                                                              {'attrs': {},
                                                                               'child_nodes': [{'attrs': {},
                                                                                                'child_nodes': [],
                                                                                                'position': 1,
                                                                                                'tag': 'b',
                                                                                                'text_nodes': [{'data': 'a '
                                                                                                                        'bold',
                                                                                                                'position': 0}]}],
                                                                               'position': 2,
                                                                               'tag': 'div',
                                                                               'text_nodes': [{'data': '\n'
                                                                                                       '            '
                                                                                                       'another div with ',
                                                                                               'position': 0},
                                                                                              {'data': ' element\n        ',
                                                                                               'position': 2}]}],
                                                              'position': 1,
                                                              'tag': 'body',
                                                              'text_nodes': []}],
                                             'tag': 'html',
                                             'text_nodes': []}


HTML__WITH_ONE_PARAGRAPH = "<html><body><p>an paragraph</p></body></html>"
HTML__WITH_SOME_TAGS     = """<!DOCTYPE html>
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