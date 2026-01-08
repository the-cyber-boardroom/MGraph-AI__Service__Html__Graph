from unittest                                                                    import TestCase
from mgraph_ai_service_html_graph.fast_api.routes.Routes__Timestamps             import Routes__Timestamps
from mgraph_ai_service_html_graph.utils.testing.QA_Create_Html_Transformations   import QA_Create_Html_Transformations
from osbot_utils.helpers.performance.Performance_Measure__Session                import Perf
from osbot_utils.type_safe.type_safe_core.config.Type_Safe__Config               import Type_Safe__Config
from osbot_utils.utils.Files                                                     import path_combine


class test_QA_Create_Html_Transformations(TestCase):
    @classmethod
    def setUpClass(cls):                                                                             # Setup shared test objects
        cls.routes_timestamps           = Routes__Timestamps()
        cls.target_folder               = path_combine(__file__,'../_traces')
        cls.create_html_transformations = QA_Create_Html_Transformations(target_folder = cls.target_folder)

    def test_create__for__simple_html__speedscope(self):
        with Type_Safe__Config(skip_validation=True, fast_create=True):
            with self.create_html_transformations as _:
                #_.create__for__simple_html__speedscope()

                _.create__for__html__with_size      (100)

                #
                #_.create__for__html__with_size      (100)

    def test__create_for__(self):
        with Type_Safe__Config(skip_validation=True, fast_create=False):
            with self.create_html_transformations as _:
                #_.create__for__simple_html          ()
                #_.create__for__html_with_some_tags  ()
                #_.create__for__html_bootstrap_example ()
                 _.create__for__html__with_size      (1)
                # _.create__for__html__with_size      (5)
                 _.create__for__html__with_size      (10)
                # _.create__for__html__with_size      (20)
                 _.create__for__html__with_size      (30)
                # _.create__for__html__with_size      (40)
                # _.create__for__html__with_size      (50)
                #_.create__for__html__with_size      (100)
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

    def test_perf__check_ctor__MGraph__Index(self):
        from mgraph_db.mgraph.index.MGraph__Index                         import MGraph__Index
        from osbot_utils.helpers.performance.Performance_Measure__Session import Perf
        def mgraph_index():
            MGraph__Index()

        #MGraph__Index().print_obj()

        with Perf() as _:
            _.measure__quick(mgraph_index)
            _.print_report()

        # BEFORE Type_Safe__On_Demand, with MGraph__Index(Type_Safe)

        # ────────────────────────────────────────────────────────────
        #   Performance Report: mgraph_index
        # ────────────────────────────────────────────────────────────
        #
        #   Score        :     1.100 ms   (normalized)
        #   Raw Score    :     1.137 ms   (actual)
        #
        #   Samples      :           87
        #   Min          :     1.081 ms
        #   Max          :     1.551 ms
        #   Average      :     1.158 ms
        #   Median       :     1.136 ms
        #   Std Dev      :    88.942 µs
        #
        #   Variance     : 1.4x   (max/min ratio)
        #
        #   Distribution:                               count       %
        #
        #     1.081 ms - 1.128 ms   │████████████████████████████████████████    38 ( 43.7%)
        #     1.128 ms - 1.175 ms   │████████████████████████████████████        35 ( 40.2%) ◀ score
        #     1.175 ms - 1.222 ms   │█████                                        5 (  5.7%)
        #     1.222 ms - 1.269 ms   │██                                           2 (  2.3%)
        #     1.316 ms - 1.363 ms   │██                                           2 (  2.3%)
        #     1.363 ms - 1.410 ms   │█                                            1 (  1.1%)
        #     1.410 ms - 1.457 ms   │██                                           2 (  2.3%)
        #     1.504 ms - 1.551 ms   │██                                           2 (  2.3%)


    def test_perf__check_ctor__sub_indexes(self):
        from mgraph_db.mgraph.index.MGraph__Index__Edges  import MGraph__Index__Edges
        from mgraph_db.mgraph.index.MGraph__Index__Labels import MGraph__Index__Labels
        from mgraph_db.mgraph.index.MGraph__Index__Types  import MGraph__Index__Types
        from mgraph_db.mgraph.index.MGraph__Index__Values import MGraph__Index__Values

        with Perf() as _:
            _.measure(lambda: MGraph__Index__Edges())
            _.print_report()
            _.measure(lambda: MGraph__Index__Labels())
            _.print_report()
            _.measure(lambda: MGraph__Index__Types())
            _.print_report()
            _.measure(lambda: MGraph__Index__Values())
            _.print_report()
