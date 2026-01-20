from unittest                                                               import TestCase
from mgraph_ai_service_html_graph.fast_api.routes.ifd.Routes__IFD__Snapshot import Routes__IFD__Snapshot
from osbot_utils.utils.Dev import pprint


class test_Routes__IFD__Snapshot(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.route_ifd_snapshot = Routes__IFD__Snapshot()


    def test_create(self):
        with self.route_ifd_snapshot as _:
            ifd_snapshot = _.create()
            ifd_content = ifd_snapshot.body.decode()
            assert '# IFD Snapshot Content Dump\n' in ifd_content

