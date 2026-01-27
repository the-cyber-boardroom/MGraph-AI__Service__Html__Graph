# ═══════════════════════════════════════════════════════════════════════════════
# Html Graph Client Constants
# Environment variable names and default values for Html Graph service client
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.primitives.core.Safe_Float                           import Safe_Float

# ═══════════════════════════════════════════════════════════════════════════════
# Environment Variable Names
# ═══════════════════════════════════════════════════════════════════════════════

ENV_VAR__HTML_GRAPH__BASE_URL  = 'URL__TARGET_SERVER__HTML_GRAPH_SERVICE'        # Base URL for remote service
ENV_VAR__HTML_GRAPH__KEY_NAME  = 'AUTH__TARGET_SERVER__HTML_GRAPH__KEY_NAME'     # API key header name
ENV_VAR__HTML_GRAPH__KEY_VALUE = 'AUTH__TARGET_SERVER__HTML_GRAPH__KEY_VALUE'    # API key value
ENV_VAR__HTML_GRAPH__NAMESPACE = 'HTML_GRAPH__NAMESPACE'                         # Cache namespace
ENV_VAR__HTML_GRAPH__TIMEOUT   = 'HTML_GRAPH__TIMEOUT'                           # Request timeout

# ═══════════════════════════════════════════════════════════════════════════════
# Default Values
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT__HTML_GRAPH__NAMESPACE = 'html-graph'                                    # Default namespace
DEFAULT__HTML_GRAPH__TIMEOUT   = Safe_Float(30.0)                                # Default timeout in seconds
