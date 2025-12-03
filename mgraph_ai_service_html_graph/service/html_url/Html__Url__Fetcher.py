import requests
from mgraph_ai_service_html_graph.schemas.routes.Schema__Html__From_Url__Request    import Schema__Html__From_Url__Request
from mgraph_ai_service_html_graph.schemas.routes.Schema__Html__From_Url__Response   import Schema__Html__From_Url__Response
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe


DEFAULT_USER_AGENT = 'Mozilla/5.0 (compatible; MGraph-AI/1.0; +https://github.com/owasp-sbot/MGraph-AI)'


class Html__Url__Fetcher(Type_Safe):                                                              # Service to fetch HTML content from URLs

    def fetch_html(self, request: Schema__Html__From_Url__Request                                 # Fetch HTML from a URL
                   ) -> Schema__Html__From_Url__Response:
        url        = request.url
        timeout    = request.timeout or 30
        user_agent = request.user_agent or DEFAULT_USER_AGENT

        headers = {
            'User-Agent'      : user_agent                                    ,
            'Accept'          : 'text/html,application/xhtml+xml,*/*'         ,
            'Accept-Language' : 'en-US,en;q=0.9'                              ,
        }

        try:
            response = requests.get(url                    ,
                                    headers = headers      ,
                                    timeout = timeout      ,
                                    allow_redirects = True )

            response.raise_for_status()                                                           # Raise exception for 4xx/5xx

            content_type = response.headers.get('Content-Type', '')
            html_content = response.text

            return Schema__Html__From_Url__Response(html         = html_content         ,
                                                    url          = str(response.url)    ,         # Final URL after redirects
                                                    content_type = content_type         ,
                                                    status_code  = response.status_code )

        except requests.exceptions.Timeout:
            raise ValueError(f"Request timed out after {timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            raise ValueError(f"Connection error: {str(e)}")
        except requests.exceptions.HTTPError as e:
            raise ValueError(f"HTTP error: {e.response.status_code} - {e.response.reason}")
        except Exception as e:
            raise ValueError(f"Failed to fetch URL: {str(e)}")