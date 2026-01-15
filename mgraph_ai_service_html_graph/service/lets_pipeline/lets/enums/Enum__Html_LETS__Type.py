# ═══════════════════════════════════════════════════════════════════════════════
# Enum__Html_LETS__Type - Maps LETS names to their class implementations
# Enum values ARE the class types - enables @type_safe string auto-conversion
# ═══════════════════════════════════════════════════════════════════════════════

from enum                                                                        import Enum
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.implementations.Html_LETS__Html__From__Raw import Html_LETS__Html__From__Raw
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.implementations.Html_LETS__Html__To__Dict  import Html_LETS__Html__To__Dict
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.implementations.Html_LETS__Dict__To__MGraph import Html_LETS__Dict__To__MGraph


class Enum__Html_LETS__Type(Enum):                                               # LETS name → class mapping
    HTML_FROM_RAW  = Html_LETS__Html__From__Raw                                  # Raw HTML input
    HTML_TO_DICT   = Html_LETS__Html__To__Dict                                   # HTML → Dictionary
    DICT_TO_MGRAPH = Html_LETS__Dict__To__MGraph                                 # Dictionary → MGraph

    # Future LETS types:
    # MGRAPH_TO_HTML_DICT = Html_LETS__MGraph__To__Html_Dict
    # MGRAPH_TO_HTML      = Html_LETS__MGraph__To__Html
    # HTML_DICT_TO_HTML   = Html_LETS__Html_Dict__To__Html
    # HTML_FROM_URL       = Html_LETS__Html__From__Url
