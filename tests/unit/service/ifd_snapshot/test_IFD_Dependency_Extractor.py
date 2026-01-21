# ═══════════════════════════════════════════════════════════════════════════════
# Test__IFD_Dependency_Extractor - Unit tests for dependency extraction
# Uses real Html_MGraph - NO mocks or patches
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                              import TestCase

from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List import Type_Safe__List
from osbot_utils.utils.Objects                                                             import base_classes
from osbot_utils.type_safe.Type_Safe                                                       import Type_Safe
from mgraph_ai_service_html_graph.service.ifd_snapshot.IFD_Dependency_Extractor            import IFD_Dependency_Extractor
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Dependency      import Schema__IFD_Dependency
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__IFD_Version
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__Logical_Name


class Test__IFD_Dependency_Extractor(TestCase):

    def test__init__(self):                                                                # Test auto-initialization
        with IFD_Dependency_Extractor() as _:
            assert type(_)                     is IFD_Dependency_Extractor
            assert base_classes(_)             == [Type_Safe, object]
            assert type(_.seen_logical_names)  is Type_Safe__List
            assert len(_.seen_logical_names)   == 0

    def test_extract_from_html__single_script(self):                                       # Extract single external script
        html = '''<html>
            <head><script src="../v0.1.0/js/app.js"></script></head>
            <body></body>
        </html>'''

        with IFD_Dependency_Extractor() as _:
            deps = _.extract_from_html(html_content = html                ,
                                       html_path    = 'v0.1.1/index.html' ,
                                       base_path    = '/project'          )

            assert len(deps)                    == 1
            assert type(deps[0])                is Schema__IFD_Dependency
            assert str(deps[0].source_version)  == 'v0.1.0'
            assert str(deps[0].resource_type)   == 'js'
            assert str(deps[0].logical_name)    == 'js/app'
            assert str(deps[0].file_type)       == 'base'
            assert int(deps[0].load_order)      == 0

    def test_extract_from_html__single_css(self):                                          # Extract single external stylesheet
        html = '''<html>
            <head><link rel="stylesheet" href="../v0.2.0/css/common.css"></head>
            <body></body>
        </html>'''

        with IFD_Dependency_Extractor() as _:
            deps = _.extract_from_html(html_content = html                ,
                                       html_path    = 'v0.2.1/index.html' ,
                                       base_path    = '/project'          )

            assert len(deps)                    == 1
            assert str(deps[0].source_version)  == 'v0.2.0'
            assert str(deps[0].resource_type)   == 'css'
            assert str(deps[0].logical_name)    == 'css/common'
            assert str(deps[0].file_type)       == 'base'

    def test_extract_from_html__multiple_css_same_name(self):                              # Multiple CSS files with same logical name
        html = '''<html><head>
            <link rel="stylesheet" href="../v0.1.0/css/common.css">
            <link rel="stylesheet" href="../v0.1.2/css/common.css">
        </head><body></body></html>'''

        with IFD_Dependency_Extractor() as _:
            deps = _.extract_from_html(html, 'v0.1.3/index.html', '/project')

            assert len(deps)                    == 2
            assert str(deps[0].source_version)  == 'v0.1.0'
            assert str(deps[0].file_type)       == 'base'
            assert str(deps[1].source_version)  == 'v0.1.2'
            assert str(deps[1].file_type)       == 'surgical'

    def test_extract_from_html__mixed_resources(self):                                     # Both CSS and JS dependencies
        html = '''<html><head>
            <link rel="stylesheet" href="../v0.2.0/css/common.css">
            <script src="../v0.2.0/js/services/api-client.js"></script>
            <script src="../v0.2.3/js/services/api-client.js"></script>
        </head><body></body></html>'''

        with IFD_Dependency_Extractor() as _:
            deps = _.extract_from_html(html, 'v0.2.5/index.html', '/project')

            assert len(deps)              == 3

            css_deps = [d for d in deps if str(d.resource_type) == 'css']
            js_deps  = [d for d in deps if str(d.resource_type) == 'js']

            assert len(css_deps)          == 1
            assert len(js_deps)           == 2

    def test_extract_from_html__load_order_preserved(self):                                # Load order matches HTML order
        html = '''<html><head>
            <link rel="stylesheet" href="../v0.2.0/css/a.css">
            <link rel="stylesheet" href="../v0.2.0/css/b.css">
            <script src="../v0.2.0/js/first.js"></script>
            <script src="../v0.2.0/js/second.js"></script>
        </head><body></body></html>'''

        with IFD_Dependency_Extractor() as _:
            deps = _.extract_from_html(html, 'v0.2.1/index.html', '/project')

            assert len(deps)              == 4
            assert int(deps[0].load_order) == 0                                            # css/a
            assert int(deps[1].load_order) == 1                                            # css/b
            assert int(deps[2].load_order) == 2                                            # js/first
            assert int(deps[3].load_order) == 3                                            # js/second

    def test_extract_from_html__ignores_inline_scripts(self):                              # Inline scripts should be skipped
        html = '''<html><head>
            <script>console.log('inline');</script>
            <script src="../v0.1.0/js/app.js"></script>
        </head><body></body></html>'''

        with IFD_Dependency_Extractor() as _:
            deps = _.extract_from_html(html, 'v0.1.1/index.html', '/project')

            assert len(deps)                 == 1                                          # Only external script
            assert str(deps[0].logical_name) == 'js/app'

    def test_extract_from_html__ignores_inline_styles(self):                               # Inline styles should be skipped
        html = '''<html><head>
            <style>.test { color: red; }</style>
            <link rel="stylesheet" href="../v0.1.0/css/common.css">
        </head><body></body></html>'''

        with IFD_Dependency_Extractor() as _:
            deps = _.extract_from_html(html, 'v0.1.1/index.html', '/project')

            assert len(deps)                 == 1                                          # Only external stylesheet
            assert str(deps[0].logical_name) == 'css/common'

    def test_extract_from_html__ignores_non_versioned_paths(self):                         # CDN and other non-versioned paths
        html = '''<html><head>
            <link rel="stylesheet" href="https://cdn.example.com/style.css">
            <script src="https://cdn.example.com/lib.js"></script>
            <script src="../v0.1.0/js/app.js"></script>
        </head><body></body></html>'''

        with IFD_Dependency_Extractor() as _:
            deps = _.extract_from_html(html, 'v0.1.1/index.html', '/project')

            assert len(deps)                    == 1                                       # Only versioned path
            assert str(deps[0].source_version)  == 'v0.1.0'

    def test_extract_version__valid_patterns(self):                                        # Test version extraction
        with IFD_Dependency_Extractor() as _:
            assert str(_.extract_version('../v0.2.0/css/common.css'))  == 'v0.2.0'
            assert str(_.extract_version('../v0.2.10/js/app.js'))      == 'v0.2.10'
            assert str(_.extract_version('../v1.0.0/js/main.js'))      == 'v1.0.0'
            assert str(_.extract_version('../v12.34.567/x.js'))        == 'v12.34.567'

    def test_extract_version__no_version(self):                                            # Non-versioned paths return None
        with IFD_Dependency_Extractor() as _:
            assert _.extract_version('css/common.css')       is None
            assert _.extract_version('https://cdn.js/lib')   is None
            assert _.extract_version('./local/file.js')      is None

    def test_extract_logical_name__various_paths(self):                                    # Test logical name extraction
        with IFD_Dependency_Extractor() as _:
            assert str(_.extract_logical_name('../v0.2.0/css/common.css'))                  == 'css/common'
            assert str(_.extract_logical_name('../v0.2.0/js/services/api-client.js'))       == 'js/services/api-client'
            assert str(_.extract_logical_name('../v0.2.0/components/config/config.js'))     == 'components/config/config'

    def test_classify_file_type__base_first(self):                                         # First occurrence is base
        with IFD_Dependency_Extractor() as _:
            result = _.classify_file_type(Safe_Str__Logical_Name('js/app'))
            assert str(result) == 'base'

    def test_classify_file_type__surgical_after_base(self):                                # Subsequent occurrences are surgical
        with IFD_Dependency_Extractor() as _:
            _.classify_file_type(Safe_Str__Logical_Name('js/app'))                         # First = base
            result = _.classify_file_type(Safe_Str__Logical_Name('js/app'))                # Second = surgical
            assert str(result) == 'surgical'

    def test_classify_file_type__different_names_are_base(self):                           # Different names are each base
        with IFD_Dependency_Extractor() as _:
            result1 = _.classify_file_type(Safe_Str__Logical_Name('js/app'))
            result2 = _.classify_file_type(Safe_Str__Logical_Name('css/style'))

            assert str(result1) == 'base'
            assert str(result2) == 'base'

    def test_reset_seen_names(self):                                                       # Reset clears classification state
        with IFD_Dependency_Extractor() as _:
            _.classify_file_type(Safe_Str__Logical_Name('js/app'))
            _.classify_file_type(Safe_Str__Logical_Name('js/app'))

            assert len(_.seen_logical_names) == 1

            _.reset_seen_names()

            assert len(_.seen_logical_names) == 0

            # After reset, same name is base again
            result = _.classify_file_type(Safe_Str__Logical_Name('js/app'))
            assert str(result) == 'base'
