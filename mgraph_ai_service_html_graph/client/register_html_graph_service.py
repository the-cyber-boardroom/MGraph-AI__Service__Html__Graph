# ═══════════════════════════════════════════════════════════════════════════════
# register_html_graph_service
# Registration helpers for Html Graph service
# This file lives in mgraph_ai_service_html_graph (the heavy package)
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API__Config import Serverless__Fast_API__Config

from osbot_utils.utils.Env                                                                              import get_env
from mgraph_ai_service_html_graph.fast_api.Html_Graph__Service__Fast_API                                import Html_Graph__Service__Fast_API
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                       import Fast_API__Service__Registry
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                       import fast_api__service__registry
from osbot_fast_api.services.schemas.registry.Fast_API__Service__Registry__Client__Config               import Fast_API__Service__Registry__Client__Config
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode     import Enum__Fast_API__Service__Registry__Client__Mode
from mgraph_ai_service_html_graph.client.Html_Graph__Service__Client                                    import Html_Graph__Service__Client
from mgraph_ai_service_html_graph.schemas.client.consts__html_graph_client                              import ENV_VAR__HTML_GRAPH__BASE_URL
from mgraph_ai_service_html_graph.schemas.client.consts__html_graph_client                              import ENV_VAR__HTML_GRAPH__KEY_NAME
from mgraph_ai_service_html_graph.schemas.client.consts__html_graph_client                              import ENV_VAR__HTML_GRAPH__KEY_VALUE


def register_html_graph_service__in_memory(registry      : Fast_API__Service__Registry = None,
                                           return_client : bool                        = False
                                          ):
    """Register Html Graph service config for IN_MEMORY mode.

    Creates FastAPI app and registers config. Use for testing.
    """
    if registry is None:
        registry = fast_api__service__registry

    fast_api__config = Serverless__Fast_API__Config(enable_api_key=False)
    fast_api         = Html_Graph__Service__Fast_API(config=fast_api__config).setup()                                   # Create FastAPI app

    config = Fast_API__Service__Registry__Client__Config(mode         = Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY,
                                                         fast_api_app = fast_api.app(),
                                                         fast_api     = fast_api      )                                            # Store wrapper for test access


    registry.register(Html_Graph__Service__Client, config)

    if return_client:
        return Html_Graph__Service__Client()
    else:
        return None


def register_html_graph_service__remote(registry      : Fast_API__Service__Registry = None,
                                        base_url      : str                          = None,
                                        api_key_name  : str                          = None,
                                        api_key_value : str                          = None
                                       ) -> None:
    """Register Html Graph service config for REMOTE mode.

    If credentials not provided, reads from environment variables.
    Use for production.
    """
    if registry is None:
        registry = fast_api__service__registry

    # Use provided values or fall back to env vars
    url   = base_url      or get_env(ENV_VAR__HTML_GRAPH__BASE_URL )
    name  = api_key_name  or get_env(ENV_VAR__HTML_GRAPH__KEY_NAME )
    value = api_key_value or get_env(ENV_VAR__HTML_GRAPH__KEY_VALUE)

    if not url:
        raise ValueError(f"REMOTE mode requires base_url or {ENV_VAR__HTML_GRAPH__BASE_URL} env var")

    config = Fast_API__Service__Registry__Client__Config(
        mode          = Enum__Fast_API__Service__Registry__Client__Mode.REMOTE,
        base_url      = url  ,
        api_key_name  = name ,
        api_key_value = value
    )

    registry.register(Html_Graph__Service__Client, config)


def register_html_graph_service__from_env(registry: Fast_API__Service__Registry = None
                                         ) -> None:
    """Register Html Graph service config based on environment.

    If HTML_GRAPH_BASE_URL is set, uses REMOTE mode.
    Otherwise, uses IN_MEMORY mode (for testing).
    """
    if registry is None:
        registry = fast_api__service__registry

    target_url = get_env(ENV_VAR__HTML_GRAPH__BASE_URL)

    if target_url:
        register_html_graph_service__remote(registry=registry)
    else:
        register_html_graph_service__in_memory(registry=registry)