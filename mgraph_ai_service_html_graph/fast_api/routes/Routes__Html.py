from osbot_fast_api.api.routes.Fast_API__Routes                                     import Fast_API__Routes
from mgraph_ai_service_html_graph.schemas.routes.Schema__Html__From_Url__Request    import Schema__Html__From_Url__Request
from mgraph_ai_service_html_graph.schemas.routes.Schema__Html__From_Url__Response   import Schema__Html__From_Url__Response
from mgraph_ai_service_html_graph.service.html_url.Html__Url__Fetcher               import Html__Url__Fetcher

TAG__ROUTES_HTML = 'html'
ROUTES_PATHS__HTML = [f'/{TAG__ROUTES_HTML}/from/url']


class Routes__Html(Fast_API__Routes):                                                             # Routes for HTML operations
    tag : str = TAG__ROUTES_HTML

    url_fetcher : Html__Url__Fetcher                                                              # Auto-initialized by Type_Safe

    def from__url(self   ,                                                                           # POST /html/from/url
                  request: Schema__Html__From_Url__Request
                      ) -> Schema__Html__From_Url__Response:
        return self.url_fetcher.fetch_html(request)

    def setup_routes(self):
        self.add_route_post(self.from__url)
        return self