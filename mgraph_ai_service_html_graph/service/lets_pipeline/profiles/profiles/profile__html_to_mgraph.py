# ═══════════════════════════════════════════════════════════════════════════════
# Profile: html-to-mgraph
# Standard profile that converts HTML to MGraph document
# ═══════════════════════════════════════════════════════════════════════════════

from mgraph_ai_service_html_graph.service.lets_pipeline.profiles.schemas.Schema__LETS__Profile          import Schema__LETS__Profile
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.implementations.Html_LETS__Html__To__Dict  import Html_LETS__Html__To__Dict
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.implementations.Html_LETS__Dict__To__MGraph import Html_LETS__Dict__To__MGraph


PROFILE__HTML_TO_MGRAPH = Schema__LETS__Profile(profile_id    = 'html-to-mgraph'                        ,
                                                profile_name  = 'HTML to MGraph'                        ,
                                                description   = 'Parse HTML and build MGraph document'  ,
                                                lets_pipeline = [Html_LETS__Html__To__Dict             ,
                                                                 Html_LETS__Dict__To__MGraph           ])
