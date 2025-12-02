from unittest                          import TestCase
from mgraph_ai_service_html__graph.config      import SERVICE_NAME


class test_config(TestCase):

    def test__config_vars(self):
        assert SERVICE_NAME                   == 'mgraph_ai_service_html__graph'