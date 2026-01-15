from mgraph_ai_service_html_graph.service.html_graph.Html_Dict__OSBot__To__Html_Dict    import Html_Dict__OSBot__To__Html_Dict
from mgraph_ai_service_html_graph.service.html_graph.Html_Dict__To__Html_MGraph         import Schema__Config__Html_Dict__To__Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph                        import Html_MGraph
from osbot_utils.helpers.html.transformers.Html__To__Html_Dict                          import Html__To__Html_Dict
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html               import Safe_Str__Html


class Html__To__Html_MGraph(Type_Safe):
    config: Schema__Config__Html_Dict__To__Html_MGraph=None

    def convert(self, html  : Safe_Str__Html):
        html_dict__osbot = Html__To__Html_Dict            (html=html).convert()
        html_dict        = Html_Dict__OSBot__To__Html_Dict(              ).convert(html_dict__osbot)
        html_mgraph      = Html_MGraph.from_html_dict(html_dict=html_dict, config=self.config)
        return html_mgraph

