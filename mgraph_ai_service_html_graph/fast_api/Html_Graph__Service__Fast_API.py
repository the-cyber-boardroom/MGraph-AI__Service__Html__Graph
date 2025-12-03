import mgraph_ai_service_html_graph__render_ui
from osbot_fast_api.api.decorators.route_path                       import route_path
from osbot_fast_api.api.routes.Routes__Set_Cookie                   import Routes__Set_Cookie
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API        import Serverless__Fast_API
from osbot_fast_api_serverless.fast_api.routes.Routes__Info         import Routes__Info
from starlette.responses                                            import RedirectResponse
from starlette.staticfiles                                          import StaticFiles
from mgraph_ai_service_html_graph.config                            import FAST_API__TITLE, FAST_API__DESCRIPTION, UI__CONSOLE__ROUTE__CONSOLE, UI__CONSOLE__MAJOR__VERSION, UI__CONSOLE__LATEST__VERSION
from mgraph_ai_service_html_graph.fast_api.routes.Routes__Graph     import Routes__Graph
from mgraph_ai_service_html_graph.utils.Version                     import version__mgraph_ai_service_html_graph


ROUTES_PATHS__CONSOLE        = [f'/{UI__CONSOLE__ROUTE__CONSOLE}']

class Html_Graph__Service__Fast_API(Serverless__Fast_API):
   
    def setup(self):
        with self.config as _:
            _.name           = FAST_API__TITLE
            _.version        = version__mgraph_ai_service_html_graph
            _.description    = FAST_API__DESCRIPTION
        return super().setup()

    def setup_routes(self):
        self.add_routes(Routes__Graph       )
        self.add_routes(Routes__Info        )
        self.add_routes(Routes__Set_Cookie  )



    # todo: refactor to separate class (focused on setting up this static route)
    def setup_static_routes(self):


        path_static_folder  = mgraph_ai_service_html_graph__render_ui.path
        path_static         = f"/{UI__CONSOLE__ROUTE__CONSOLE}"
        path_name           = UI__CONSOLE__ROUTE__CONSOLE
        path_latest_version = f"/{UI__CONSOLE__ROUTE__CONSOLE}/{UI__CONSOLE__MAJOR__VERSION}/{UI__CONSOLE__LATEST__VERSION}/index.html"
        self.app().mount(path_static, StaticFiles(directory=path_static_folder), name=path_name)

        @route_path(path=f'/{UI__CONSOLE__ROUTE__CONSOLE}')
        @route_path(path=f'/{UI__CONSOLE__ROUTE__CONSOLE}/')
        async def redirect_to_latest():
            return RedirectResponse(url=path_latest_version)

        self.add_route_get(redirect_to_latest)
