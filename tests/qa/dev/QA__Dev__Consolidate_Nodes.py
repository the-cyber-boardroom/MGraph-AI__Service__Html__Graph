from mgraph_ai_service_html_graph.service.html_graph.Html_Dict__To__Html_MGraph import Schema__Config__Html_Dict__To__Html_MGraph
from osbot_utils.decorators.methods.cache_on_self import cache_on_self

from mgraph_ai_service_html_graph.service.html_graph.Html_Dict__OSBot__To__Html_Dict        import Html_Dict__OSBot__To__Html_Dict
from osbot_utils.helpers.html.transformers.Html__To__Html_Dict                              import Html__To__Html_Dict
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                   import Safe_Str__Html
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__Tree_View     import Html_MGraph__To__Tree_View
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__To__Png                  import Html_MGraph__To__Png
from osbot_utils.utils.Dev                                                                  import pprint
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path           import Safe_Str__File__Path
from osbot_utils.utils.Env                                                                  import load_dotenv
from osbot_utils.utils.Files                                                                import path_combine
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph                            import Html_MGraph
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from tests.qa                                                                               import dev

QA__DEV__DOT_ENV_FILE                = '.qa.env'
QA__DEV__PNG__FILE_NAME__MGRAPH      = 'mgraph.png'
QA__DEV__PNG__FILE_NAME__HTML_MGRAPH = 'html-mgraph.png'

class QA__Dev__Consolidate_Nodes_Config(Type_Safe):
    create_png  : bool
    html         : Safe_Str__Html

class QA__Dev__Consolidate_Nodes(Type_Safe):
    config      : QA__Dev__Consolidate_Nodes_Config
    dot_env_file: Safe_Str__File__Path

    @cache_on_self
    def html(self) :
        return self.config.html

    @cache_on_self
    def html__osbot_dict(self):
        return Html__To__Html_Dict(html=self.html()).convert()

    @cache_on_self
    def html_dict(self):
        return Html_Dict__OSBot__To__Html_Dict().convert(osbot_dict=self.html__osbot_dict())

    @cache_on_self
    def html_mgraph(self):
        return Html_MGraph.from_html_dict(html_dict = self.html_dict()          ,
                                          config    = self.html_mgraph__config())

    @cache_on_self
    def html_mgraph__config(self):
        return Schema__Config__Html_Dict__To__Html_MGraph()

    @cache_on_self
    def mgraph(self):
        return self.html_mgraph().mgraph

    def setup(self):
        self.dot_env_file = path_combine(dev.path, QA__DEV__DOT_ENV_FILE)
        load_dotenv(self.dot_env_file)
        return self

    def create_png__from__html_mgraph(self):
        if self.config.create_png:
            png_file = path_combine(dev.path, QA__DEV__PNG__FILE_NAME__HTML_MGRAPH)
            with Html_MGraph__To__Png(html_mgraph=self.html_mgraph(), target_file=png_file) as _:
                _.to_png()

    def create_png__from__mgraph(self):
        if self.config.create_png:
            png_file = path_combine(dev.path, QA__DEV__PNG__FILE_NAME__MGRAPH)

            with self.mgraph().screenshot() as _:
                _.save_to(png_file)
                export_dot = _.export().export_dot()

                (export_dot#.show_node__value()
                            #.show_node__id ()
                            #.show_node__type ()
                            .show_node__value ()
                            .show_node__path  ()
                            #.show_node__value__key()
                            #.set_render__label_show_var_name()
                           #.show_edge__id__str()
                           #.show_edge__type()
                           .show_edge__path__str ()
                           #.show_edge__predicate()
                           #.show_edge__id()
                          .set_node__shape__type__box()
                          .set_node__shape__rounded()
                 )


                _.dot()

    def configure_mgraph(self):
        with self.html_mgraph__config() as _:
                _.add_tag_nodes       = False
                _.add_attribute_nodes = False
        return self
    def print_json(self):

        json_data = self.mgraph().export().to__json()
        pprint(json_data)

    def print_tree(self):
        with Html_MGraph__To__Tree_View(html_mgraph= self.html_mgraph()) as _:
            tree_text = _.export_tree()
            print('\n\n===== Tree text ====')
            pprint(tree_text)

    def print_tree__as_text(self):
        with Html_MGraph__To__Tree_View(html_mgraph= self.html_mgraph()) as _:
            tree_text = _.export_tree__as_text()
            print('\n\n===== Tree (as text) ====')
            print(tree_text)

