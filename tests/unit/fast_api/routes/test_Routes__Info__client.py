from unittest                                       import TestCase
from osbot_utils.utils.Version                      import Version as Version__OSBot_Utils
from osbot_fast_api.utils.Version                   import version__osbot_fast_api
from osbot_fast_api_serverless.utils.Version        import version__osbot_fast_api_serverless
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs  import setup__html_graph_service__fast_api_test_objs, TEST_API_KEY__NAME, TEST_API_KEY__VALUE


class test_Routes__Info__client(TestCase):
    @classmethod
    def setUpClass(cls):
        with setup__html_graph_service__fast_api_test_objs() as _:
            cls.client = _.fast_api__client
            cls.client.headers[TEST_API_KEY__NAME] = TEST_API_KEY__VALUE

    def test__info_version(self):
        response = self.client.get('/info/versions')
        assert response.status_code == 200
        assert response.json()      == { 'osbot_fast_api'           : version__osbot_fast_api            ,
                                         'osbot_fast_api_serverless': version__osbot_fast_api_serverless,
                                         'osbot_utils'              : Version__OSBot_Utils().value()    }

    def test__info_status(self):
        response = self.client.get('/info/status')
        result = response.json()
        assert response.status_code == 200
        assert response.json()      == { 'environment': 'local'                            ,
                                         'name'       : 'osbot_fast_api_serverless'        ,
                                         'status'     : 'operational'                      ,
                                         'version'    : version__osbot_fast_api_serverless }