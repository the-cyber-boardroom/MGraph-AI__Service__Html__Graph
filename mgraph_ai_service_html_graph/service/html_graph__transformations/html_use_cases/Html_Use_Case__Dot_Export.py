from osbot_utils.type_safe.Type_Safe                             import Type_Safe
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph import Html_MGraph


class Html_Use_Case__Dot_Export(Type_Safe):
    html_mgraph : Html_MGraph

    def mgraph(self):
        return self.html_mgraph.mgraph

    def dot_string(self, transformation):
        if transformation == "html_use_case__1":
            return self.dot_string__use_case_1()
        elif transformation == "html_use_case__2":
            return self.dot_string__use_case_2()
        return ""

    def dot_string__use_case_1(self):
        with self.mgraph().export().export_dot() as _:

            self.apply__config__use_case_1(_)
            #.show_edge__predicate__str()

            #.show_node__id ()
            #.show_node__type ()
            #.show_edge__id()
            #.show_node__value__key()
            #.show_edge__id__str()
            #.show_edge__type()

            return _.process_graph()

    def dot_string__use_case_2(self):
        with self.mgraph().export().export_dot() as _:

            #self.apply__config__use_case_1(_)
            self.apply__config__use_case_2(_)
            return _.process_graph()

    def apply__config__use_case_1(self, export_dot):
        (
            export_dot.show_node__value ()
                      .show_node__path            ()
                      .show_edge__path__str       ()
                      .set_graph__rank_dir__lr    ()
                      .set_node__shape__type__box ()
                      .set_node__shape__rounded   ()
                      .set_value_type_fill_color  (str , '#B3D1F8')
         )
        return self

    def apply__config__use_case_2(self, export_dot):
        (
            export_dot#.show_edge__id  ()
                     #.set_render__label_show_var_name()
                      .show_node__value()
                      .show_node__path()
                      #.show_node__id  ()
                      .set_node__font__size(20)
                      .show_edge__path__str()
                      #.show_edge__predicate ()
                      #.set_graph__rank_dir__tb  ()
                      .set_graph__rank_dir__lr  ()

                      .set_node__shape__type__box ()
                      .set_node__shape__rounded   ()
                      .set_value_type_fill_color  (str , '#B3D1F8')
        )
        return self