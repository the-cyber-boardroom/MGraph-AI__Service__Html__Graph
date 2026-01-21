# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html_To_Cache__Input - Input for HTML to cache FLeT
# Simple: just HTML content and where to store it in the data layer
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                      import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html import Safe_Str__Html


DEFAULT__HTML_TO_CACHE__DATA_KEY     = 'html'                                             # Default data layer path
DEFAULT__HTML_TO_CACHE__DATA_FILE_ID = 'raw'                                              # Default file name


class Schema__Html_To_Cache__Input(Type_Safe):                                            # Input for HTML to cache
    html         : Safe_Str__Html                                                         # HTML content to save
    data_key     : str = DEFAULT__HTML_TO_CACHE__DATA_KEY                                 # Data layer path
    data_file_id : str = DEFAULT__HTML_TO_CACHE__DATA_FILE_ID                             # File identifier
