from typing                                                                                 import Tuple
from fastapi                                                                                import FastAPI
from mgraph_ai_service_cache.fast_api.Cache_Service__Fast_API                               import Cache_Service__Fast_API
from mgraph_ai_service_cache.service.cache.Cache__Service                                   import Cache__Service
from mgraph_ai_service_cache_client.client.Client__Cache__Service                           import Client__Cache__Service
from mgraph_ai_service_cache_client.client.client_contract.Cache__Service__Fast_API__Client import Cache__Service__Fast_API__Client
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API__Config                        import Serverless__Fast_API__Config
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                              import type_safe

@type_safe
def cache__service__fast_api_app() -> Tuple[FastAPI, Cache__Service]:
    serverless_config       = Serverless__Fast_API__Config              (enable_api_key = False                )
    cache_service__fast_api = Cache_Service__Fast_API                   (config         = serverless_config ).setup()
    fast_api_app            = cache_service__fast_api.app()
    return fast_api_app, cache_service__fast_api.cache_service

@type_safe
def client_cache_service() -> Tuple[Cache__Service__Fast_API__Client, Cache__Service]:
    fast_api_app, cache_service  = cache__service__fast_api_app()
    client__cache_service        = Client__Cache__Service().set__fast_api_app(fast_api_app).client()
    return client__cache_service, cache_service