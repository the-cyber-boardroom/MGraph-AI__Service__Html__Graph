from osbot_fast_api.utils.Fast_API__Server_Info                               import fast_api__server_info, Fast_API__Server_Info
from osbot_fast_api_serverless.services.info.schemas.Schema__Server__Versions import Schema__Server__Versions
from osbot_utils.type_safe.Type_Safe                                          import Type_Safe
from mgraph_ai_service_html_graph.service.info.schemas.Schema__Service__Status      import Schema__Service__Status, Enum__Service_Environment



class Service_Info(Type_Safe):

    def environment(self):                                                   # Determine current environment
        import os
        if os.getenv('AWS_REGION'):
            return Enum__Service_Environment.aws_lambda
        else:
            return Enum__Service_Environment.local

    def service_info(self) -> Schema__Service__Status:                               # Get current service status
        return Schema__Service__Status(environment = self.environment())

    def versions(self):
        return Schema__Server__Versions()

    def server_info(self) -> Fast_API__Server_Info:
        return fast_api__server_info
