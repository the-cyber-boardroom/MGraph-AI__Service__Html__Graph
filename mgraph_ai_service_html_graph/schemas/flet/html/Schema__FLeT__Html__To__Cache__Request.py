# ═══════════════════════════════════════════════════════════════════════════════
# Schema__FLeT__Html__To__Cache__Request - Request to execute Html-To-Cache FLeT
# ═══════════════════════════════════════════════════════════════════════════════

from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__Data_Key import Safe_Str__Cache__File__Data_Key
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__File_Id  import Safe_Str__Cache__File__File_Id
from osbot_utils.type_safe.Type_Safe                                                       import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                  import Safe_Str__Html

DEFAULT__HTML_TO_CACHE__DATA_KEY     = 'html'
DEFAULT__HTML_TO_CACHE__DATA_FILE_ID = 'raw'


class Schema__FLeT__Html__To__Cache__Request(Type_Safe):                          # Request for Html-To-Cache
    html         : Safe_Str__Html                                                 # HTML content to store
    data_key     : Safe_Str__Cache__File__Data_Key = DEFAULT__HTML_TO_CACHE__DATA_KEY
    data_file_id : Safe_Str__Cache__File__File_Id  = DEFAULT__HTML_TO_CACHE__DATA_FILE_ID
