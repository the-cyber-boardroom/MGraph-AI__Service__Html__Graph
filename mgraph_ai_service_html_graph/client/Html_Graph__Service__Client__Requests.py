# ═══════════════════════════════════════════════════════════════════════════════
# Html_Graph__Service__Client__Requests
# Transport layer for Html Graph service - extends generic Fast_API__Client__Requests
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_fast_api.services.registry.Fast_API__Client__Requests import Fast_API__Client__Requests


class Html_Graph__Service__Client__Requests(Fast_API__Client__Requests):        # Html Graph-specific transport
    pass                                                                        # service_type set at runtime by Html_Graph__Service__Client