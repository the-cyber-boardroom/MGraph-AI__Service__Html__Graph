# ═══════════════════════════════════════════════════════════════════════════════
# Test__Schema__IFD_Dependency - Schema validation tests
# Pure data container tests - NO mocks or patches
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                              import TestCase
from osbot_utils.utils.Objects                                                             import base_classes
from osbot_utils.type_safe.Type_Safe                                                       import Type_Safe
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Dependency      import Schema__IFD_Dependency
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__IFD_Version
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__Logical_Name
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__Resource_Type
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__File_Type
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_UInt__Load_Order


class Test__Schema__IFD_Dependency(TestCase):

    def test__init__(self):                                                                # Test auto-initialization
        with Schema__IFD_Dependency() as _:
            assert type(_)                is Schema__IFD_Dependency
            assert base_classes(_)        == [Type_Safe, object]
            assert type(_.source_version) is Safe_Str__IFD_Version
            assert type(_.logical_name)   is Safe_Str__Logical_Name
            assert type(_.resource_type)  is Safe_Str__Resource_Type
            assert type(_.file_type)      is Safe_Str__File_Type
            assert type(_.load_order)     is Safe_UInt__Load_Order

    def test__init____with_values(self):                                                   # Test creation with values
        with Schema__IFD_Dependency(original_path  = '../v0.2.0/js/app.js'        ,
                                    resolved_path  = '/project/v0.2.0/js/app.js'  ,
                                    source_version = 'v0.2.0'                     ,
                                    resource_type  = 'js'                         ,
                                    file_type      = 'base'                       ,
                                    logical_name   = 'js/app'                     ,
                                    load_order     = 0                            ) as _:

            assert str(_.original_path)  == '../v0.2.0/js/app.js'
            assert str(_.resolved_path)  == '/project/v0.2.0/js/app.js'
            assert str(_.source_version) == 'v0.2.0'
            assert str(_.resource_type)  == 'js'
            assert str(_.file_type)      == 'base'
            assert str(_.logical_name)   == 'js/app'
            assert int(_.load_order)     == 0

    def test_json_serialization(self):                                                     # Test round-trip serialization
        original = Schema__IFD_Dependency(original_path  = '../v0.2.0/js/app.js'        ,
                                          resolved_path  = '/project/v0.2.0/js/app.js'  ,
                                          source_version = 'v0.2.0'                     ,
                                          resource_type  = 'js'                         ,
                                          file_type      = 'base'                       ,
                                          logical_name   = 'js/app'                     ,
                                          load_order     = 5                            )

        json_data = original.json()
        restored  = Schema__IFD_Dependency.from_json(json_data)

        assert str(restored.original_path)  == str(original.original_path)
        assert str(restored.source_version) == str(original.source_version)
        assert str(restored.logical_name)   == str(original.logical_name)
        assert int(restored.load_order)     == int(original.load_order)
