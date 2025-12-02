import pytest
from osbot_utils.utils.Misc                                        import list_set
from osbot_fast_api_serverless.deploy.Deploy__Serverless__Fast_API import DEFAULT__ERROR_MESSAGE__WHEN_FAST_API_IS_OK
from mgraph_ai_service_html__graph.config                                 import LAMBDA_DEPENDENCIES__BASE__SERVICE
from mgraph_ai_service_html__graph.utils.Version                          import version__mgraph_ai_service_html__graph
from mgraph_ai_service_html__graph.utils.deploy.Deploy__Service           import Deploy__Service


class test_Deploy__Service__base():     # Base class for deployment tests - override stage in subclasses

    stage: str = None  # Must be set by subclass

    @classmethod
    def setUpClass(cls):
        if cls.stage is None:
            pytest.skip("Can't run when 'stage' class variable is not set")

        cls.deploy_fast_api = Deploy__Service(stage=cls.stage)

        with cls.deploy_fast_api as _:
            if _.aws_config.aws_configured() is False:
                pytest.skip("this test needs valid AWS credentials")

    def test_1__check_stages(self):
        assert self.deploy_fast_api.stage == self.stage

    def test_2__upload_dependencies(self):
        upload_results = self.deploy_fast_api.upload_lambda_dependencies_to_s3()
        assert list_set(upload_results) == LAMBDA_DEPENDENCIES__BASE__SERVICE

    def test_3__create(self):
        assert self.deploy_fast_api.create() is True

    def test_4__invoke(self):
        assert self.deploy_fast_api.invoke().get('errorMessage') == DEFAULT__ERROR_MESSAGE__WHEN_FAST_API_IS_OK

    def test_5__invoke__function_url(self):
        version = {'version': version__mgraph_ai_service_html__graph}
        assert self.deploy_fast_api.invoke__function_url('/info/health') == {'status': 'ok'}

    # def test_6__delete(self):
    #     assert self.deploy_fast_api.delete() is True









