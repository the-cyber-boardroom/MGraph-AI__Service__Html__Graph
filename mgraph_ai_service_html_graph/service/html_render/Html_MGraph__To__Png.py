from mgraph_ai_service_html_graph.service.html_graph.Html_Dict__OSBot__To__Html_Dict import Html_Dict__OSBot__To__Html_Dict
from osbot_utils.helpers.html.transformers.Html__To__Html_Dict import Html__To__Html_Dict

from osbot_utils.decorators.methods.cache_on_self                                   import cache_on_self
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Screenshot       import Html_MGraph__Screenshot
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path   import Safe_Str__File__Path
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph                    import Html_MGraph
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe


class Html_MGraph__To__Png(Type_Safe):
    html_mgraph : Html_MGraph
    target_file : Safe_Str__File__Path

    @cache_on_self
    def html_mgraph__screenshot(self):
        return Html_MGraph__Screenshot(mgraph=self.html_mgraph.mgraph, target_file=self.target_file).setup()

    @cache_on_self
    def setup__style(self):
        with self.html_mgraph__screenshot() as _:
            (_.full_detail()
              .default_colors()
              .show_tags(True)
              .show_attrs(True)
              .show_text(True)
              .set_max_text_length(40)
              .set_element_shape('box'))

        return self

    def to_png(self):
        self.setup__style()
        # with self.html_mgraph__screenshot() as _:
        #     #_.structure_only()
        #     _.show_attrs(False)

        self.html_mgraph__screenshot().dot()



    @classmethod
    def from_html(cls, html, target_file):
        html_dict__osbot    = Html__To__Html_Dict(html=html).convert()
        html_dict           = Html_Dict__OSBot__To__Html_Dict().convert(html_dict__osbot    )
        html_mgraph         = Html_MGraph.from_html_dict(html_dict)
        html_mgraph_to_png  = Html_MGraph__To__Png(html_mgraph = html_mgraph,
                                                   target_file = target_file)
        return html_mgraph_to_png