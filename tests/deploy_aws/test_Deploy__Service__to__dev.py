from unittest                                    import TestCase
# from osbot_utils.utils.Dev                       import pprint
# from osbot_utils.utils.Env                       import load_dotenv
# from osbot_utils.utils.Files                     import path_combine, file_exists
from tests.deploy_aws.test_Deploy__Service__base import test_Deploy__Service__base

class test_Deploy__Service__to__dev(test_Deploy__Service__base, TestCase):
    stage = 'dev'

    # @classmethod
    # def setUpClass(cls):
    #     dot_env_file = path_combine(__file__, "../.deploy.env")
    #     assert file_exists(dot_env_file)
    #     load_dotenv(dotenv_path=dot_env_file, override=True)
    #     super().setUpClass()
    #
    # def test_4__invoke(self):
    #     self.deploy_fast_api.create()
    #     result = self.deploy_fast_api.invoke()
    #     pprint(result)