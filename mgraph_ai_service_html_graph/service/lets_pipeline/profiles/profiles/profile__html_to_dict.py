# ═══════════════════════════════════════════════════════════════════════════════
# Profile: html-to-dict
# Simple profile that converts HTML to dictionary
# ═══════════════════════════════════════════════════════════════════════════════

from mgraph_ai_service_html_graph.service.lets_pipeline.profiles.schemas.Schema__LETS__Profile         import Schema__LETS__Profile
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.implementations.Html_LETS__Html__To__Dict import Html_LETS__Html__To__Dict


PROFILE__HTML_TO_DICT = Schema__LETS__Profile(profile_id    = 'html-to-dict'                      ,
                                              profile_name  = 'HTML to Dictionary'                ,
                                              description   = 'Parse HTML into dictionary with node IDs',
                                              lets_pipeline = [Html_LETS__Html__To__Dict]         )
