from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document                      import Html_MGraph__Document
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html_Dict   import Html_MGraph__Document__To__Html_Dict
from osbot_utils.helpers.html.transformers.Html_Dict__To__Html                                          import Html_Dict__To__Html
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe


class Html_MGraph__Document__To__Html(Type_Safe):                               # Convert Html_MGraph__Document to HTML string
    """Converts Html_MGraph__Document to HTML string.

    Pipeline:
        Html_MGraph__Document
            → Html_MGraph__Document__To__Html_Dict → Html_Dict
            → Html_Dict__To__Html → HTML String

    This class composes existing converters for simplicity.
    """

    def convert(self, document: Html_MGraph__Document) -> str:                  # Convert Document to HTML string
        html_dict = Html_MGraph__Document__To__Html_Dict().convert(document)    # Document → Html_Dict
        html_str  = Html_Dict__To__Html(root=html_dict).convert()          # Html_Dict → HTML

        return html_str