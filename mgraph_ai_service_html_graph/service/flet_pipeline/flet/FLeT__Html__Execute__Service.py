# ═══════════════════════════════════════════════════════════════════════════════
# FLeT__Html__Execute__Service - Service layer for FLeT HTML execution
# ═══════════════════════════════════════════════════════════════════════════════

from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__Namespace                                       import Safe_Str__Cache__Namespace
from mgraph_ai_service_html_graph.schemas.flet.html.Schema__FLeT__Html__From__Cache__Request                                import Schema__FLeT__Html__From__Cache__Request
from mgraph_ai_service_html_graph.schemas.flet.html.Schema__FLeT__Html__From__Cache__Response                               import Schema__FLeT__Html__From__Cache__Response
from mgraph_ai_service_html_graph.schemas.flet.html.Schema__FLeT__Html__To__Cache__Request                                  import Schema__FLeT__Html__To__Cache__Request
from mgraph_ai_service_html_graph.schemas.flet.html.Schema__FLeT__Html__To__Cache__Response                                 import Schema__FLeT__Html__To__Cache__Response
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                                                  import Html_Cache__Client
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.FLeT__Html__From__Cache                import FLeT__Html__From__Cache
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.schemas.Schema__Html_From_Cache__Input import Schema__Html_From_Cache__Input
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.FLeT__Html__To__Cache                    import FLeT__Html__To__Cache
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Input     import Schema__Html_To_Cache__Input
from osbot_utils.type_safe.Type_Safe                                                                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                                          import Cache_Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                              import type_safe


class FLeT__Html__Execute__Service(Type_Safe):                                      # Service for FLeT HTML execution
    cache_client : Html_Cache__Client                                               # Cache client for storage

    @type_safe
    def execute_to_cache(self                                                    ,  # Execute FLeT to store HTML
                         namespace : Safe_Str__Cache__Namespace                  ,  # Cache namespace
                         cache_id  : Cache_Id                                    ,  # Target cache ID
                         request   : Schema__FLeT__Html__To__Cache__Request         # Request with HTML content
                    ) -> Schema__FLeT__Html__To__Cache__Response:
        try:
            if not request.html:
                return Schema__FLeT__Html__To__Cache__Response(success  = False   ,
                                                               cache_id = cache_id)

            if self.cache_client.entry__exists(namespace=namespace, cache_id=cache_id) is False:
                raise ValueError(f"Entity not found: {cache_id}")

            flet = FLeT__Html__To__Cache(cache_client = self.cache_client ,
                                         cache_id     = cache_id          ,
                                         namespace    = namespace         ).setup()

            if request.data_key != 'html' or request.data_file_id != 'raw':
                flet.data_key     = request.data_key
                flet.data_file_id = request.data_file_id

            input_data   = Schema__Html_To_Cache__Input(html         = request.html        ,
                                                        data_key     = request.data_key    ,
                                                        data_file_id = request.data_file_id)
            result       = flet.execute(input_data)
            flow_output  = result.flow_output
            char_count   = flow_output.char_count if flow_output else 0                          # todo: we should be using a type_safe class here
            data_key     = flow_output.data_key
            data_file_id = flow_output.data_file_id
            return Schema__FLeT__Html__To__Cache__Response(success      = result.success ,
                                                           cache_id     = cache_id       ,
                                                           char_count   = char_count     ,
                                                           data_key     = data_key       ,
                                                           data_file_id = data_file_id   ,
                                                           flow_saved   = True           )
        except ValueError as e:
            raise e
        except Exception:
            return Schema__FLeT__Html__To__Cache__Response(success  = False   ,
                                                           cache_id = cache_id)

    @type_safe
    def execute_from_cache(self                                                    ,# Execute FLeT to retrieve HTML
                           namespace : Safe_Str__Cache__Namespace                  ,# Cache namespace
                           cache_id  : Cache_Id                                    ,# Source cache ID
                           request   : Schema__FLeT__Html__From__Cache__Request     # Request options
                      ) -> Schema__FLeT__Html__From__Cache__Response:
        try:
            if self.cache_client.entry__exists(namespace=namespace, cache_id=cache_id) is False:
                raise ValueError(f"Entity not found: {cache_id}")

            flet = FLeT__Html__From__Cache(cache_client = self.cache_client ,
                                           cache_id     = cache_id          ,
                                           namespace    = namespace         ).setup()

            #if request.data_key != 'html' or request.data_file_id != 'raw':
            flet.data_key     = request.data_key
            flet.data_file_id = request.data_file_id

            input_data  = Schema__Html_From_Cache__Input(data_key     = request.data_key    ,
                                                         data_file_id = request.data_file_id)
            result      = flet.execute(input_data)
            flow_output = result.flow_output
            html        = ''
            found       = False

            if flow_output:
                html  = flow_output.html if flow_output.html else ''
                found = flow_output.found

            char_count = len(html)

            return Schema__FLeT__Html__From__Cache__Response(success    = result.success ,
                                                             cache_id   = cache_id       ,
                                                             html       = html           ,
                                                             found      = found          ,
                                                             char_count = char_count     ,
                                                             flow_saved = True           )
        except ValueError as e:
            raise e
        except Exception:
            return Schema__FLeT__Html__From__Cache__Response(success  = False   ,
                                                             cache_id = cache_id)