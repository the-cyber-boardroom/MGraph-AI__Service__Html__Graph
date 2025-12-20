from unittest                                                    import TestCase
from osbot_utils.testing.test_data.const__test__data__html       import TEST__DATA__HTML__SIMPLE, TEST__DATA__HTML__MIXED_CONTENT
from tests.qa.dev.QA__Dev__Consolidate_Nodes                     import QA__Dev__Consolidate_Nodes, QA__Dev__Consolidate_Nodes_Config
from tests.unit.service.html_render.test_Html_MGraph__To__Png    import HTML__WITH_ONE_PARAGRAPH, HTML__WITH_SOME_TAGS, HTML__BOOTSTRAP_EXAMPLE

HTML__USE_CASE_1  = "<html></html>"
HTML__USE_CASE_2  = "<html><body lang='en' answer='42'>some <b>bold</b> is here</body></html>"
HTML__USE_CASE_3  = """<html>
    <body>
        <div>
            This is a <a href=''>link</a> with some <b>bold</b> in the mix
        </div>
        <div>
            this is the <i>2nd div</i> in here
        </div>
    </body>
</html>"""
HTML__USE_CASE_4  = TEST__DATA__HTML__SIMPLE
HTML__USE_CASE_5  = TEST__DATA__HTML__MIXED_CONTENT
HTML__USE_CASE_6 = HTML__WITH_SOME_TAGS
HTML__USE_CASE_7 = HTML__BOOTSTRAP_EXAMPLE

class test_QA__Dev__Consolidate_Nodes(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.html              = HTML__WITH_ONE_PARAGRAPH
        cls.html              = HTML__USE_CASE_3

        with QA__Dev__Consolidate_Nodes_Config() as _:
            cls.config     = _
            _.create_png   = True
            _.html         = cls.html

        cls.consolidate_nodes = QA__Dev__Consolidate_Nodes(config=cls.config).setup()


    def test_mgraph__simple(self):
        with self.consolidate_nodes as _:
            print()
            print()
            print(self.html)

            #_.html_mgraph().print_obj()

            #_.print_tree__as_text()
            #_.print_tree()
            _.configure_mgraph()
            _.print_json()


            #_.create_png__from__html_mgraph()
            _.create_png__from__mgraph()




