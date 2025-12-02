import re
import types
import pytest
from unittest                                            import TestCase
from osbot_utils.utils.Json                              import str_to_json
#from tests.unit.Service__Fast_API__Test_Objs             import setup_local_stack
from mgraph_ai_service_html__graph.fast_api.lambda_handler      import run


class test_lambda_handler(TestCase):

    @classmethod
    def setUpClass(cls):
        #setup_local_stack()
        cls.handler = staticmethod(run)

    def test__setUpClass(self):
        assert type(self.handler) is types.FunctionType

    def test_run(self):
        expected_error = ("The adapter was unable to infer a handler to use for the event. "
                          "This is likely related to how the Lambda function was invoked. "
                          "(Are you testing locally? Make sure the request payload is valid for a supported handler.)")
        with pytest.raises(RuntimeError, match=re.escape(expected_error)):
            self.handler(event={}, context=None)

        event = {'version'       : '2.0',
                 'requestContext': {'http': {'method'  : 'GET',
                                           'path'     : '/',
                                           'sourceIp' : '127.0.0.1'}}}

        response = self.handler(event=event)
        assert type(response) is dict
        assert response.get('statusCode') == 401

        assert str_to_json(response.get('body')).get('message') == 'Client API key is missing, you need to set it on a header or cookie'
