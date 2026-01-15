# ═══════════════════════════════════════════════════════════════════════════════
# Enum__Source_Type - Indicates how the HTML was sourced
# ═══════════════════════════════════════════════════════════════════════════════

from enum                                                                        import Enum


class Enum__Source_Type(str, Enum):                                              # HTML source type
    RAW_HTML = 'raw_html'                                                        # Direct HTML submission
    URL      = 'url'                                                             # Fetched from URL
