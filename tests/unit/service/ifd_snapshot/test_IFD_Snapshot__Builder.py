# ═══════════════════════════════════════════════════════════════════════════════
# Test__IFD_Snapshot_Builder - Unit tests for snapshot building
# Uses real data - NO mocks or patches
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                              import TestCase
from osbot_utils.utils.Objects                                                             import base_classes
from osbot_utils.type_safe.Type_Safe                                                       import Type_Safe
from mgraph_ai_service_html_graph.service.ifd_snapshot.IFD_Snapshot__Builder               import IFD_Snapshot__Builder
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Dependency      import Schema__IFD_Dependency
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Load_Chain      import Schema__IFD_Load_Chain
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Html_Entry      import Schema__IFD_Html_Entry
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Manifest        import Schema__IFD_Manifest
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Snapshot_Config import Schema__IFD_Snapshot_Config
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__IFD_Version
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__Logical_Name
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__Resource_Type
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__File_Type


class Test__IFD_Snapshot_Builder(TestCase):

    def test__init__(self):                                                                # Test auto-initialization
        with IFD_Snapshot__Builder() as _:
            assert type(_) is IFD_Snapshot__Builder
            assert base_classes(_) == [Type_Safe, object]

    def test_build_load_chains__groups_by_logical_name(self):                              # Dependencies grouped into chains
        deps = [
            Schema__IFD_Dependency(original_path  = '../v0.2.0/js/api.js'             ,
                                   resolved_path  = '/project/v0.2.0/js/api.js'       ,
                                   source_version = Safe_Str__IFD_Version('v0.2.0')   ,
                                   resource_type  = Safe_Str__Resource_Type('js')     ,
                                   file_type      = Safe_Str__File_Type('base')       ,
                                   logical_name   = Safe_Str__Logical_Name('js/api')  ,
                                   load_order     = 0                                 ),
            Schema__IFD_Dependency(original_path  = '../v0.2.3/js/api.js'             ,
                                   resolved_path  = '/project/v0.2.3/js/api.js'       ,
                                   source_version = Safe_Str__IFD_Version('v0.2.3')   ,
                                   resource_type  = Safe_Str__Resource_Type('js')     ,
                                   file_type      = Safe_Str__File_Type('surgical')   ,
                                   logical_name   = Safe_Str__Logical_Name('js/api')  ,
                                   load_order     = 1                                 ),
            Schema__IFD_Dependency(original_path  = '../v0.2.0/css/style.css'         ,
                                   resolved_path  = '/project/v0.2.0/css/style.css'   ,
                                   source_version = Safe_Str__IFD_Version('v0.2.0')   ,
                                   resource_type  = Safe_Str__Resource_Type('css')    ,
                                   file_type      = Safe_Str__File_Type('base')       ,
                                   logical_name   = Safe_Str__Logical_Name('css/style'),
                                   load_order     = 2                                 ),
        ]

        with IFD_Snapshot__Builder() as _:
            chains = _.build_load_chains(deps)

            assert len(chains)                   == 2

            # Find js/api chain
            js_chain = next(c for c in chains if str(c.logical_name) == 'js/api')
            assert type(js_chain)                is Schema__IFD_Load_Chain
            assert len(js_chain.files)           == 2
            assert str(js_chain.resource_type)   == 'js'

    def test_build_load_chains__sorts_by_version(self):                                    # Files sorted by version within chain
        deps = [
            Schema__IFD_Dependency(original_path  = '../v0.2.5/js/api.js'             ,
                                   resolved_path  = '/p/v0.2.5/js/api.js'             ,
                                   source_version = Safe_Str__IFD_Version('v0.2.5')   ,
                                   resource_type  = Safe_Str__Resource_Type('js')     ,
                                   file_type      = Safe_Str__File_Type('surgical')   ,
                                   logical_name   = Safe_Str__Logical_Name('js/api')  ,
                                   load_order     = 2                                 ),
            Schema__IFD_Dependency(original_path  = '../v0.2.0/js/api.js'             ,
                                   resolved_path  = '/p/v0.2.0/js/api.js'             ,
                                   source_version = Safe_Str__IFD_Version('v0.2.0')   ,
                                   resource_type  = Safe_Str__Resource_Type('js')     ,
                                   file_type      = Safe_Str__File_Type('base')       ,
                                   logical_name   = Safe_Str__Logical_Name('js/api')  ,
                                   load_order     = 0                                 ),
        ]

        with IFD_Snapshot__Builder() as _:
            chains = _.build_load_chains(deps)

            assert str(chains[0].files[0].source_version) == 'v0.2.0'                      # Base first
            assert str(chains[0].files[1].source_version) == 'v0.2.5'                      # Then surgical

    def test_build_manifest__basic(self):                                                  # Test manifest creation
        config = Schema__IFD_Snapshot_Config(version_root   = '/project/v0.2' ,
                                             target_version = 'v0.2.10'       )

        html_entries = [
            Schema__IFD_Html_Entry(file_name    = 'playground.html'                   ,
                                   file_path    = '/project/v0.2/v0.2.10/playground.html',
                                   dependencies = []                                  )
        ]

        load_chains = [
            Schema__IFD_Load_Chain(logical_name  = Safe_Str__Logical_Name('js/api')  ,
                                   resource_type = Safe_Str__Resource_Type('js')     ,
                                   files         = [
                                       Schema__IFD_Dependency(original_path  = '../v0.2.0/js/api.js',
                                                              resolved_path  = '/p/v0.2.0/js/api.js',
                                                              source_version = 'v0.2.0'             ,
                                                              resource_type  = 'js'                 ,
                                                              file_type      = 'base'               ,
                                                              logical_name   = 'js/api'             ,
                                                              load_order     = 0                    ),
                                       Schema__IFD_Dependency(original_path  = '../v0.2.3/js/api.js',
                                                              resolved_path  = '/p/v0.2.3/js/api.js',
                                                              source_version = 'v0.2.3'             ,
                                                              resource_type  = 'js'                 ,
                                                              file_type      = 'surgical'           ,
                                                              logical_name   = 'js/api'             ,
                                                              load_order     = 1                    ),
                                   ])
        ]

        with IFD_Snapshot__Builder() as _:
            manifest = _.build_manifest(config, html_entries, load_chains)

            assert type(manifest)                      is Schema__IFD_Manifest
            assert str(manifest.source_version)        == 'v0.2.10'
            assert str(manifest.snapshot_version)      == 'v0.2.10__snapshot'
            assert int(manifest.file_count)            == 2
            assert len(manifest.versions_referenced)   == 2
            assert 'v0.2.0' in [str(v) for v in manifest.versions_referenced]
            assert 'v0.2.3' in [str(v) for v in manifest.versions_referenced]

    def test_build_tree_structure__basic(self):                                            # Test tree generation
        config = Schema__IFD_Snapshot_Config(version_root   = '/project/v0.2' ,
                                             target_version = 'v0.2.10'       )

        html_entries = [
            Schema__IFD_Html_Entry(file_name    = 'playground.html'                   ,
                                   file_path    = '/project/v0.2/v0.2.10/playground.html',
                                   dependencies = []                                  )
        ]

        load_chains = [
            Schema__IFD_Load_Chain(logical_name  = Safe_Str__Logical_Name('js/api')  ,
                                   resource_type = Safe_Str__Resource_Type('js')     ,
                                   files         = [
                                       Schema__IFD_Dependency(source_version = 'v0.2.0'             ,
                                                              resource_type  = 'js'                 ,
                                                              logical_name   = 'js/api'             ,
                                                              load_order     = 0                    ),
                                   ])
        ]

        with IFD_Snapshot__Builder() as _:
            manifest = _.build_manifest(config, html_entries, load_chains)
            tree     = _.build_tree_structure(manifest)

            tree_str = str(tree)
            assert 'snapshot/'        in tree_str
            assert 'manifest.json'    in tree_str
            assert 'content.txt'      in tree_str
            assert 'html/'            in tree_str
            assert 'playground.html'  in tree_str
            assert 'src/'             in tree_str
            assert 'v0.2.0/'          in tree_str
            assert 'js/api.js'        in tree_str
