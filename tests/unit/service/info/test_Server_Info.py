from unittest                                                             import TestCase
from osbot_fast_api.utils.Fast_API__Server_Info                           import Fast_API__Server_Info
from osbot_utils.utils.Misc                                               import list_set
from mgraph_ai_service_html_graph.service.info.Service_Info                     import Service_Info
from mgraph_ai_service_html_graph.service.info.schemas.Enum__Service_Status     import Enum__Service_Status
from mgraph_ai_service_html_graph.service.info.schemas.Schema__Service__Status  import Schema__Service__Status
from mgraph_ai_service_html_graph.utils.Version                                 import version__mgraph_ai_service_html_graph


class test_Server_Info(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_info = Service_Info()

    def test___init__(self):
        with self.server_info as _:
            assert type(_) == Service_Info

    def test_status(self):
        with self.server_info.service_info() as _:
            assert type(_)       == Schema__Service__Status
            assert _.name        == 'mgraph_ai_service_html_graph'
            assert _.status      == Enum__Service_Status.operational
            assert _.version     == version__mgraph_ai_service_html_graph
            assert _.environment == self.server_info.environment()

    def test_versions(self):
        with self.server_info.versions() as _:
            assert list_set(_.json()) == ['osbot_fast_api',
                                          'osbot_fast_api_serverless',
                                          'osbot_utils']

    def test_server_info(self):
        with self.server_info.server_info() as _:
            assert type(_) is Fast_API__Server_Info