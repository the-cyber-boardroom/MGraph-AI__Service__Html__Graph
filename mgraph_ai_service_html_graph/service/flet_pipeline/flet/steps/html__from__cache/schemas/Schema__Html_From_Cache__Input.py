# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html_From_Cache__Input - Input schema for HTML from cache FLeT
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe import Type_Safe

DEFAULT__HTML_FROM_CACHE__DATA_KEY     = 'html'
DEFAULT__HTML_FROM_CACHE__DATA_FILE_ID = 'raw'


class Schema__Html_From_Cache__Input(Type_Safe):                                          # Input for loading HTML from cache
    data_key     : str = DEFAULT__HTML_FROM_CACHE__DATA_KEY                               # Data layer path (default: 'html')
    data_file_id : str = DEFAULT__HTML_FROM_CACHE__DATA_FILE_ID                           # File identifier (default: 'raw')