from unittest                                                               import TestCase
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Document import Html_MGraph__Document

class test_Html_MGraph__Document(TestCase):                                     # Test document orchestrator

    def test__init__(self):                                                     # Test initialization
        with Html_MGraph__Document() as _:
            assert type(_) is Html_MGraph__Document
            assert _.head_graph    is None
            assert _.body_graph    is None
            assert _.attrs_graph   is None
            assert _.scripts_graph is None
            assert _.styles_graph  is None

    def test_setup_initializes_all_graphs(self):                                # Test setup creates all graphs
        with Html_MGraph__Document().setup() as _:
            assert _.root_id        is not None
            assert _.head_graph     is not None
            assert _.body_graph     is not None
            assert _.attrs_graph    is not None
            assert _.scripts_graph  is not None
            assert _.styles_graph   is not None

            assert _.head_graph   .root_id is not None                          # Each graph has its root
            assert _.body_graph   .root_id is not None
            assert _.attrs_graph  .root_id is not None
            assert _.scripts_graph.root_id is not None
            assert _.styles_graph .root_id is not None

    def test_stats(self):                                                       # Test comprehensive stats
        with Html_MGraph__Document().setup() as _:
            stats = _.stats()

            assert 'document'   in stats
            assert 'head'       in stats
            assert 'body'       in stats
            assert 'attributes' in stats
            assert 'scripts'    in stats
            assert 'styles'     in stats
