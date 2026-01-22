import mgraph_ai_service_html_graph__render_ui
from osbot_fast_api_serverless.deploy.Deploy__Serverless__Fast_API        import Deploy__Serverless__Fast_API
from mgraph_ai_service_html_graph.config                                  import SERVICE_NAME, LAMBDA_DEPENDENCIES__HTML_GRAPH__SERVICE
from mgraph_ai_service_html_graph.fast_api.lambda_handler                 import run
from osbot_utils.utils.Env                                                import get_env


class Deploy__Service(Deploy__Serverless__Fast_API):

    def deploy_lambda(self):
        with super().deploy_lambda() as _:
            _.add_folder(mgraph_ai_service_html_graph__render_ui.path)
            _.set_env_variable('AUTH__TARGET_SERVER__CACHE_SERVICE__BASE_URL' , get_env('AUTH__TARGET_SERVER__CACHE_SERVICE__BASE_URL' ))
            _.set_env_variable('AUTH__TARGET_SERVER__CACHE_SERVICE__KEY_NAME' , get_env('AUTH__TARGET_SERVER__CACHE_SERVICE__KEY_NAME' ))
            _.set_env_variable('AUTH__TARGET_SERVER__CACHE_SERVICE__KEY_VALUE', get_env('AUTH__TARGET_SERVER__CACHE_SERVICE__KEY_VALUE' ))

            return _

    def handler(self):
        return run

    def lambda_dependencies(self):
        return LAMBDA_DEPENDENCIES__HTML_GRAPH__SERVICE

    def lambda_name(self):
        return SERVICE_NAME