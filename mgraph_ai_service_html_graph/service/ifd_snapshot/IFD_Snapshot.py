# ═══════════════════════════════════════════════════════════════════════════════
# IFD Snapshot - Main facade for snapshot generation
# Orchestrates dependency extraction and output building
# ═══════════════════════════════════════════════════════════════════════════════

import os
from typing                                                                                import List
from osbot_utils.type_safe.Type_Safe                                                       import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path          import Safe_Str__File__Path
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                             import type_safe
from osbot_utils.utils.Files                                                               import file_contents
from mgraph_ai_service_html_graph.service.ifd_snapshot.IFD_Dependency_Extractor            import IFD_Dependency_Extractor
from mgraph_ai_service_html_graph.service.ifd_snapshot.IFD_Snapshot__Builder               import IFD_Snapshot__Builder
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Snapshot_Config import Schema__IFD_Snapshot_Config
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Snapshot_Result import Schema__IFD_Snapshot_Result
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Html_Entry      import Schema__IFD_Html_Entry


class IFD_Snapshot(Type_Safe):                                                             # Main entry point for snapshot generation
    config    : Schema__IFD_Snapshot_Config                                                # Configuration
    extractor : IFD_Dependency_Extractor                                                   # Dependency extraction
    builder   : IFD_Snapshot__Builder                                                       # Output building

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Generation Methods
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def generate(self) -> Schema__IFD_Snapshot_Result:                                     # Generate complete snapshot
        self.extractor.reset_seen_names()                                                  # Reset state for fresh extraction

        html_entries = self.discover_html_files()
        all_deps     = []

        for entry in html_entries:
            html_content = file_contents(str(entry.file_path))
            if html_content:
                deps = self.extractor.extract_from_html(html_content     = html_content            ,
                                                        html_path        = entry.file_path         ,
                                                        base_path        = self.config.version_root)
                entry.dependencies = deps
                all_deps.extend(deps)

        load_chains  = self.builder.build_load_chains(all_deps)
        manifest     = self.builder.build_manifest(self.config, html_entries, load_chains)
        content_text = self.builder.build_content_text(manifest)

        return Schema__IFD_Snapshot_Result(manifest     = manifest    ,
                                           content_text = content_text)

    @type_safe
    def generate_with_zip(self) -> Schema__IFD_Snapshot_Result:                            # Generate with zip bytes
        result           = self.generate()
        result.zip_bytes = self.builder.build_zip_bytes(result.manifest, result.content_text)
        return result

    @type_safe
    def generate_to_folder(self                                    ,                       # Generate and extract to folder
                           output_path: Safe_Str__File__Path
                      ) -> Schema__IFD_Snapshot_Result:
        result = self.generate()
        self.builder.extract_to_folder(result.manifest    ,
                                       result.content_text,
                                       output_path        )
        return result

    # ═══════════════════════════════════════════════════════════════════════════
    # HTML File Discovery
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def discover_html_files(self) -> List[Schema__IFD_Html_Entry]:                         # Find all HTML files to process
        entries = []

        # Get folders to search (default: just root of target version)
        folders = self.config.html_folders
        if not folders:
            folders = [Safe_Str__File__Path('')]                                           # Root only

        target_path = os.path.join(str(self.config.version_root),
                                   str(self.config.target_version))

        for folder in folders:
            folder_str  = str(folder) if folder else ''
            search_path = os.path.join(target_path, folder_str) if folder_str else target_path

            if os.path.exists(search_path) and os.path.isdir(search_path):
                for file_name in os.listdir(search_path):
                    if file_name.endswith('.html'):
                        full_path = os.path.join(search_path, file_name)

                        entry = Schema__IFD_Html_Entry(file_name    = Safe_Str__File__Path(file_name),
                                                       file_path    = Safe_Str__File__Path(full_path),
                                                       dependencies = []                              )
                        entries.append(entry)

        return entries

    # ═══════════════════════════════════════════════════════════════════════════
    # API Methods
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def manifest_dict(self) -> dict:                                                       # Return manifest as dict (for REST API)
        result = self.generate()
        return result.manifest.json()

    @type_safe
    def content_text(self) -> str:                                                    # Return content text only
        result = self.generate()
        return result.content_text

    @type_safe
    def zip_bytes(self) -> bytes:                                                          # Return zip bytes only
        result = self.generate_with_zip()
        return result.zip_bytes
