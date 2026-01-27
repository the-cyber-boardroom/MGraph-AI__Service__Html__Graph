# ═══════════════════════════════════════════════════════════════════════════════
# Html_Graph__Service__Client__Requests
# Unified request handler for Html Graph client (IN_MEMORY and REMOTE modes)
# This is the injection point where TestClient vs requests.Session decision happens
# ═══════════════════════════════════════════════════════════════════════════════

import requests
from typing                                                                                         import Any, Optional, Dict
from mgraph_ai_service_html_graph.schemas.client.Schema__Html_Graph__Client__Requests__Result       import Schema__Html_Graph__Client__Requests__Result
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode import Enum__Fast_API__Service__Registry__Client__Mode
from osbot_utils.decorators.methods.cache_on_self                                                   import cache_on_self
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str                                                 import Safe_Str
from starlette.testclient                                                                           import TestClient
from mgraph_ai_service_html_graph.client.Html_Graph__Service__Client__Config                        import Html_Graph__Service__Client__Config



class Html_Graph__Service__Client__Requests(Type_Safe):                         # Unified request handler
    config: Html_Graph__Service__Client__Config                                 # Client configuration

    @cache_on_self
    def test_client(self) -> TestClient:                                        # Get TestClient for IN_MEMORY mode
        if self.config.fast_api_app is None:
            raise ValueError("fast_api_app must be configured for IN_MEMORY mode")
        return TestClient(self.config.fast_api_app)

    @cache_on_self
    def session(self) -> requests.Session:                                      # Get session for REMOTE mode
        session = requests.Session()
        if self.config.api_key_header and self.config.api_key:
            session.headers[str(self.config.api_key_header)] = str(self.config.api_key)
        return session

    def execute(self, method  : Safe_Str                ,                       # Execute HTTP request
                      path    : Safe_Str                ,                       # Request path
                      body    : Any           = None    ,                       # Request body
                      headers : Optional[Dict] = None                           # Additional headers
               ) -> Schema__Html_Graph__Client__Requests__Result:               # Unified result

        request_headers = {**self.auth_headers(), **(headers or {})}            # Merge headers

        if self.config.mode == Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY:                    # Execute based on mode
            response = self.execute_in_memory(method, path, body, request_headers)
        else:
            response = self.execute_remote(method, path, body, request_headers)

        return self.build_result(response, path)                                # Convert to unified result

    def execute_in_memory(self, method  : Safe_Str ,                            # Execute via TestClient
                                path    : Safe_Str ,                            # Request path
                                body    : Any      ,                            # Request body
                                headers : Dict                                  # Headers
                         ):                                                     # Returns response object
        method_func = getattr(self.test_client(), str(method).lower())
        if body:
            if type(body) is bytes:
                headers["Content-Type"] = "application/octet-stream"
                return method_func(str(path), data=body, headers=headers)
            else:
                return method_func(str(path), json=body, headers=headers)
        return method_func(str(path), headers=headers)

    def execute_remote(self, method  : Safe_Str ,                               # Execute via requests
                             path    : Safe_Str ,                               # Request path
                             body    : Any      ,                               # Request body
                             headers : Dict                                     # Headers
                      ):                                                        # Returns response object
        url         = f"{self.config.base_url}{path}"
        method_func = getattr(self.session(), str(method).lower())
        timeout     = float(self.config.timeout)

        if body:
            if type(body) is bytes:
                headers["Content-Type"] = "application/octet-stream"
                return method_func(url, data=body, headers=headers, timeout=timeout)
            else:
                return method_func(url, json=body, headers=headers, timeout=timeout)
        return method_func(url, headers=headers, timeout=timeout)

    def auth_headers(self) -> Dict[str, str]:                                   # Get authentication headers
        headers = {}
        if self.config.api_key_header and self.config.api_key:
            headers[str(self.config.api_key_header)] = str(self.config.api_key)
        return headers

    def build_result(self, response   ,                                         # Build unified result
                           path: Safe_Str                                       # Request path
                    ) -> Schema__Html_Graph__Client__Requests__Result:          # Unified result

        json_data = None                                                        # Try to extract JSON
        try:
            json_data = response.json()
        except:
            pass

        text_data = None                                                        # Try to extract text
        try:
            text_data = response.text
        except:
            pass

        return Schema__Html_Graph__Client__Requests__Result(status_code = response.status_code                                  ,
                                                            json        = json_data                                             ,
                                                            text        = text_data                                             ,
                                                            content     = response.content if hasattr(response, 'content') else b"",
                                                            headers     = dict(response.headers) if hasattr(response, 'headers') else {},
                                                            path        = path                                                  )
