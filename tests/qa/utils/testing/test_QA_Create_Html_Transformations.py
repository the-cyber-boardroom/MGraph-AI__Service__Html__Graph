from unittest                                                                    import TestCase
from mgraph_ai_service_html_graph.fast_api.routes.Routes__Timestamps             import Routes__Timestamps
from mgraph_ai_service_html_graph.utils.testing.QA_Create_Html_Transformations   import QA_Create_Html_Transformations
from osbot_utils.utils.Files                                                     import path_combine


class test_QA_Create_Html_Transformations(TestCase):
    @classmethod
    def setUpClass(cls):                                                                             # Setup shared test objects
        cls.routes_timestamps           = Routes__Timestamps()
        cls.target_folder               = path_combine(__file__,'../_traces')
        cls.create_html_transformations = QA_Create_Html_Transformations(target_folder = cls.target_folder)



    def test__simple_html(self):

        with self.create_html_transformations as _:
            _.create__for__simple_html          ()
            #_.create__for__html_with_some_tags  ()
            #_.create__for__html_bootstrap_example ()
            # _.create__for__html__with_size      (1)
            # _.create__for__html__with_size      (5)
            # _.create__for__html__with_size      (10)
            # _.create__for__html__with_size      (20)
            # _.create__for__html__with_size      (30)
            # _.create__for__html__with_size      (40)
            # _.create__for__html__with_size      (50)
            # _.create__for__html__with_size      (100)
            #_.create__for__url('https://www.example.com')
            #_.create__for__url('https://www.bbc.co.uk/404')
            #_.create__for__url('https://docs.diniscruz.ai')
            #_.create__for__url('https://docs.diniscruz.ai/about.html')
            #_.create__for__url('https://www.gov.uk/')


            #_.speedscope__for__html_with_some_tags()

            # #response = _.speedscope__for__sizew(size=2)
            # speedscope_traces = response.traces
            # target_file = path_combine(__file__,'../_traces/speedscope-html.json')


    #def test_create_benchmark(self):
