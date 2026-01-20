# ═══════════════════════════════════════════════════════════════════════════════
# Test__IFD_Snapshot__Integration - Integration tests with real fixtures
# Uses actual test fixtures - NO mocks or patches
# ═══════════════════════════════════════════════════════════════════════════════

import os
import io
import zipfile
import mgraph_ai_service_html_graph__render_ui
from unittest                                                                              import TestCase
from osbot_utils.testing.Temp_Folder                                                       import Temp_Folder
from osbot_utils.utils.Files                                                               import folder_exists
from mgraph_ai_service_html_graph.service.ifd_snapshot.IFD_Snapshot                        import IFD_Snapshot
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Snapshot_Config import Schema__IFD_Snapshot_Config
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Snapshot_Result import Schema__IFD_Snapshot_Result
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Manifest        import Schema__IFD_Manifest


class test_IFD_Snapshot__integration(TestCase):

    @classmethod
    def setUpClass(cls):                                                                   # Set up fixtures once
        #cls.fixtures_path = Path(__file__).parent / 'fixtures' / 'v0.2'
        cls.fixtures_path  = mgraph_ai_service_html_graph__render_ui.path + '/v0/v0.2'
        cls.target_version = 'v0.2.10'

        # Skip if fixtures not available
        if not folder_exists(str(cls.fixtures_path)):
            cls.skip_tests = True
        else:
            cls.skip_tests = False

    def test_snapshot_playground__generates_result(self):                                  # Full snapshot generation
        if self.skip_tests:
            self.skipTest('Fixtures not available')

        config = Schema__IFD_Snapshot_Config(version_root   = self.fixtures_path,
                                             target_version = self.target_version)

        with IFD_Snapshot(config=config) as _:
            result = _.generate()

            assert type(result)                            is Schema__IFD_Snapshot_Result
            assert type(result.manifest)                   is Schema__IFD_Manifest
            assert str(result.manifest.source_version)     == 'v0.2.10'
            assert str(result.manifest.snapshot_version)   == 'v0.2.10__snapshot'

    def test_snapshot_playground__finds_html_entry(self):                                  # Discovers playground.html
        if self.skip_tests:
            self.skipTest('Fixtures not available')

        config = Schema__IFD_Snapshot_Config(version_root   = str(self.fixtures_path),
                                             target_version = 'v0.2.10'              )

        with IFD_Snapshot(config=config) as _:
            result = _.generate()

            assert len(result.manifest.html_entry_points) == 1
            assert 'playground.html' in str(result.manifest.html_entry_points[0].file_name)

    def test_snapshot_playground__extracts_css_dependencies(self):                         # Extracts CSS files
        if self.skip_tests:
            self.skipTest('Fixtures not available')

        config = Schema__IFD_Snapshot_Config(version_root   = str(self.fixtures_path),
                                             target_version = 'v0.2.10'              )

        with IFD_Snapshot(config=config) as _:
            result = _.generate()

            # Find css chains
            css_chains = [c for c in result.manifest.load_chains
                          if str(c.resource_type) == 'css']

            assert len(css_chains) >= 1                                                    # At least common.css chain

            # Verify common.css is found
            common_chain = next((c for c in css_chains
                                 if 'common' in str(c.logical_name)), None)
            assert common_chain is not None

    def test_snapshot_playground__extracts_js_load_chain(self):                            # Extracts api-client chain
        if self.skip_tests:
            self.skipTest('Fixtures not available')

        config = Schema__IFD_Snapshot_Config(version_root   = str(self.fixtures_path),
                                             target_version = 'v0.2.10'              )

        with IFD_Snapshot(config=config) as _:
            result = _.generate()

            # Find api-client chain
            api_chain = None
            for chain in result.manifest.load_chains:
                if 'api-client' in str(chain.logical_name):
                    api_chain = chain
                    break

            assert api_chain is not None
            assert len(api_chain.files) == 4                                               # v0.2.0, v0.2.3, v0.2.5, v0.2.9

            # Verify versions in order
            versions = [str(f.source_version) for f in api_chain.files]
            assert versions == ['v0.2.0', 'v0.2.3', 'v0.2.5', 'v0.2.9']

            # Verify base/surgical classification
            assert str(api_chain.files[0].file_type) == 'base'
            assert str(api_chain.files[1].file_type) == 'surgical'
            assert str(api_chain.files[2].file_type) == 'surgical'
            assert str(api_chain.files[3].file_type) == 'surgical'

    def test_snapshot_playground__versions_referenced(self):                               # Collects all versions
        if self.skip_tests:
            self.skipTest('Fixtures not available')

        config = Schema__IFD_Snapshot_Config(version_root   = str(self.fixtures_path),
                                             target_version = 'v0.2.10'              )

        with IFD_Snapshot(config=config) as _:
            result = _.generate()

            versions = [str(v) for v in result.manifest.versions_referenced]

            assert 'v0.2.0'  in versions
            assert 'v0.2.3'  in versions
            assert 'v0.2.5'  in versions
            assert 'v0.2.9'  in versions
            assert 'v0.2.10' in versions

    def test_snapshot_playground__content_text_structure(self):                            # Content text has expected sections
        if self.skip_tests:
            self.skipTest('Fixtures not available')

        config = Schema__IFD_Snapshot_Config(version_root   = str(self.fixtures_path),
                                             target_version = 'v0.2.10'              )

        with IFD_Snapshot(config=config) as _:
            result = _.generate()

            content = str(result.content_text)

            assert '# IFD Snapshot Content Dump'  in content
            assert '## HTML Entry Points'         in content
            assert '## Versions Referenced'       in content
            assert '## File Tree'                 in content
            assert '## Files'                     in content
            assert 'snapshot/'                    in content
            assert 'api-client'                   in content

    def test_snapshot_playground__content_text_has_file_contents(self):                    # Content includes actual file content
        if self.skip_tests:
            self.skipTest('Fixtures not available')

        config = Schema__IFD_Snapshot_Config(version_root   = self.fixtures_path     ,
                                             target_version = 'v0.2.10'              )

        with IFD_Snapshot(config=config) as _:
            result = _.generate()

            content = result.content_text

            # Check for content from api-client.js base
            assert 'class ApiClient'                               in content
            assert 'this.baseUrl'                                  in content

            # Check for content from surgical overrides
            assert 'MGraph HTML Graph - Render UI - Common Styles' in content             # v0.2.3
            assert 'Additional fetch options'                      in content             # v0.2.5

    def test_snapshot_playground__zip_generation(self):                                    # Generates valid zip
        if self.skip_tests:
            self.skipTest('Fixtures not available')

        config = Schema__IFD_Snapshot_Config(version_root   = str(self.fixtures_path),
                                             target_version = 'v0.2.10'              )

        with IFD_Snapshot(config=config) as _:
            result = _.generate_with_zip()

            assert result.zip_bytes is not None
            assert len(result.zip_bytes) > 0

            # Verify zip is valid
            with zipfile.ZipFile(io.BytesIO(result.zip_bytes), 'r') as zf:
                names = zf.namelist()

                assert 'manifest.json'                                 in names
                assert 'content.txt'                                   in names
                assert any('html/' in n for n in names)
                assert any('src/' in n for n in names)
                assert any('api-client' in n for n in names)

    def test_snapshot_playground__folder_extraction(self):                                 # Extracts to folder
        if self.skip_tests:
            self.skipTest('Fixtures not available')

        config = Schema__IFD_Snapshot_Config(version_root   = str(self.fixtures_path),
                                             target_version = 'v0.2.10'              )

        with Temp_Folder() as temp_folder:
            output_path = os.path.join(temp_folder.path(), 'snapshot')

            with IFD_Snapshot(config=config) as _:
                result = _.generate_to_folder(output_path)

                # Verify folder structure
                assert os.path.exists(os.path.join(output_path, 'manifest.json'))
                assert os.path.exists(os.path.join(output_path, 'content.txt'))
                assert os.path.exists(os.path.join(output_path, 'html'))
                assert os.path.exists(os.path.join(output_path, 'src'))

                # Verify HTML file
                html_path = os.path.join(output_path, 'html', 'playground.html')
                assert os.path.exists(html_path)

    def test_snapshot_playground__manifest_dict(self):                                     # API method returns dict
        if self.skip_tests:
            self.skipTest('Fixtures not available')

        config = Schema__IFD_Snapshot_Config(version_root   = str(self.fixtures_path),
                                             target_version = 'v0.2.10'              )

        with IFD_Snapshot(config=config) as _:
            manifest_dict = _.manifest_dict()

            assert type(manifest_dict)                is dict
            assert 'source_version'                   in manifest_dict
            assert manifest_dict['source_version']    == 'v0.2.10'
            assert 'load_chains'                      in manifest_dict
            assert 'versions_referenced'              in manifest_dict
