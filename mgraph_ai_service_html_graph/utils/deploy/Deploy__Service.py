import mgraph_ai_service_html_graph__render_ui
from osbot_fast_api_serverless.deploy.Deploy__Serverless__Fast_API        import Deploy__Serverless__Fast_API
from mgraph_ai_service_html_graph.config                                  import SERVICE_NAME, LAMBDA_DEPENDENCIES__HTML_GRAPH__SERVICE
from mgraph_ai_service_html_graph.fast_api.lambda_handler                 import run

class Deploy__Service(Deploy__Serverless__Fast_API):

    def deploy_lambda(self):
        with super().deploy_lambda() as _:
            _.add_folder(mgraph_ai_service_html_graph__render_ui.path)
            # Add any service-specific environment variables here
            # Example: _.set_env_variable('BASE_API_KEY', get_env('BASE_API_KEY'))
            return _

    def handler(self):
        return run

    def lambda_dependencies(self):
        return LAMBDA_DEPENDENCIES__HTML_GRAPH__SERVICE

    def lambda_name(self):
        return SERVICE_NAME