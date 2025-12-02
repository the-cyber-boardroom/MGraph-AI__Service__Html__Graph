from fastapi                                                           import FastAPI
from osbot_fast_api.api.Fast_API                                       import ENV_VAR__FAST_API__AUTH__API_KEY__NAME, ENV_VAR__FAST_API__AUTH__API_KEY__VALUE
from osbot_utils.type_safe.Type_Safe                                   import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid  import Random_Guid
from osbot_utils.utils.Env                                             import set_env
from starlette.testclient                                              import TestClient
from mgraph_ai_service_html_graph.fast_api.Html_Graph__Service__Fast_API     import Html_Graph__Service__Fast_API

TEST_API_KEY__NAME = 'key-used-in-pytest'
TEST_API_KEY__VALUE = Random_Guid()

class Html_Graph__Service__Fast_API__Test_Objs(Type_Safe):
    fast_api        : Html_Graph__Service__Fast_API = None
    fast_api__app   : FastAPI                 = None
    fast_api__client: TestClient              = None
    setup_completed : bool                    = False

service_fast_api_test_objs = Html_Graph__Service__Fast_API__Test_Objs()

def setup__html_graph_service__fast_api_test_objs():
        with service_fast_api_test_objs as _:
            if service_fast_api_test_objs.setup_completed is False:
                _.fast_api         = Html_Graph__Service__Fast_API().setup()
                _.fast_api__app    = _.fast_api.app()
                _.fast_api__client = _.fast_api.client()
#                _.local_stack      = setup_local_stack()
                _.setup_completed  = True

                set_env(ENV_VAR__FAST_API__AUTH__API_KEY__NAME , TEST_API_KEY__NAME)
                set_env(ENV_VAR__FAST_API__AUTH__API_KEY__VALUE, TEST_API_KEY__VALUE)
        return service_fast_api_test_objs