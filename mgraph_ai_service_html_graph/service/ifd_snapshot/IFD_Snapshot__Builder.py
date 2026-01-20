# ═══════════════════════════════════════════════════════════════════════════════
# IFD Snapshot Builder - Build snapshot outputs (manifest, text, zip, folder)
# Uses Temp_Zip_In_Memory for in-memory zip creation
# ═══════════════════════════════════════════════════════════════════════════════

import io
import zipfile
from typing                                                                                import List
from osbot_utils.type_safe.Type_Safe                                                       import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                       import Safe_UInt
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path          import Safe_Str__File__Path
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                             import type_safe
from osbot_utils.testing.Temp_Zip_In_Memory                                                import Temp_Zip_In_Memory
from osbot_utils.utils.Files                                                               import file_contents
from osbot_utils.utils.Json                                                                import json_dumps
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Dependency      import Schema__IFD_Dependency
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Load_Chain      import Schema__IFD_Load_Chain
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Html_Entry      import Schema__IFD_Html_Entry
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Manifest        import Schema__IFD_Manifest
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Snapshot_Config import Schema__IFD_Snapshot_Config
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__IFD_Version
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__Logical_Name


class IFD_Snapshot__Builder(Type_Safe):                                                     # Build snapshot outputs

    # ═══════════════════════════════════════════════════════════════════════════
    # Load Chain Building
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def build_load_chains(self                                     ,                       # Group dependencies into load chains
                          dependencies: List[Schema__IFD_Dependency]
                     ) -> List[Schema__IFD_Load_Chain]:
        chains_by_name = {}                                                                # Dict[logical_name, List[dep]]

        for dep in dependencies:
            name = str(dep.logical_name)
            if name not in chains_by_name:
                chains_by_name[name] = []
            chains_by_name[name].append(dep)

        # Build chain objects, sorted by version within each chain
        chains = []
        for name, deps in chains_by_name.items():
            sorted_deps = sorted(deps, key=lambda d: str(d.source_version))
            chain       = Schema__IFD_Load_Chain(logical_name  = Safe_Str__Logical_Name(name),
                                                 resource_type = deps[0].resource_type       ,
                                                 files         = sorted_deps                 )
            chains.append(chain)

        return chains

    # ═══════════════════════════════════════════════════════════════════════════
    # Manifest Building
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def build_manifest(self                                        ,                       # Build complete manifest
                       config       : Schema__IFD_Snapshot_Config  ,
                       html_entries : List[Schema__IFD_Html_Entry] ,
                       load_chains  : List[Schema__IFD_Load_Chain]
                  ) -> Schema__IFD_Manifest:
        versions_set = set()
        file_count   = Safe_UInt(0)

        for chain in load_chains:
            for dep in chain.files:
                versions_set.add(str(dep.source_version))
                file_count = Safe_UInt(int(file_count) + 1)

        versions_list    = [Safe_Str__IFD_Version(v) for v in sorted(versions_set)]
        snapshot_version = Safe_Str__IFD_Version(f"{config.target_version}__snapshot")

        return Schema__IFD_Manifest(snapshot_version    = snapshot_version       ,
                                    source_version      = config.target_version  ,
                                    html_entry_points   = html_entries           ,
                                    load_chains         = load_chains            ,
                                    versions_referenced = versions_list          ,
                                    file_count          = file_count             )

    # ═══════════════════════════════════════════════════════════════════════════
    # Content Text Building
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def build_content_text(self, manifest: Schema__IFD_Manifest) -> str:              # Build formatted text dump
        lines = []

        # Header
        lines.append('# ═══════════════════════════════════════════════════════════════════════════════')
        lines.append('# IFD Snapshot Content Dump')
        lines.append(f'# Version: {manifest.snapshot_version}')
        lines.append(f'# Created: {manifest.created_at}')
        lines.append('# ═══════════════════════════════════════════════════════════════════════════════')
        lines.append('')

        # HTML Entry Points
        lines.append('## HTML Entry Points')
        for entry in manifest.html_entry_points:
            lines.append(f'- {entry.file_name}')
        lines.append('')

        # Versions Referenced
        lines.append('## Versions Referenced')
        versions_str = ', '.join(str(v) for v in manifest.versions_referenced)
        lines.append(versions_str)
        lines.append('')

        # File Tree
        lines.append('## File Tree')
        tree = self.build_tree_structure(manifest)
        lines.append(str(tree))
        lines.append('')

        # File Contents
        lines.append('## Files')
        lines.append('')

        for chain in manifest.load_chains:
            for dep in chain.files:
                lines.append('# ═══════════════════════════════════════════════════════════════════════════════')
                lines.append(f'### {dep.source_version}/{dep.logical_name}.{dep.resource_type}')
                lines.append('# ═══════════════════════════════════════════════════════════════════════════════')
                lines.append('')

                content = file_contents(str(dep.resolved_path))
                if content:
                    lines.append(content)
                else:
                    lines.append(f'# ERROR: Could not read file: {dep.resolved_path}')

                lines.append('')

        return '\n'.join(lines)

    # ═══════════════════════════════════════════════════════════════════════════
    # Tree Structure Building
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def build_tree_structure(self, manifest: Schema__IFD_Manifest) -> str:            # Build ASCII tree of all files
        lines = ['snapshot/']
        lines.append('├── manifest.json')
        lines.append('├── content.txt')

        # HTML files
        lines.append('├── html/')
        html_entries = list(manifest.html_entry_points)
        for i, entry in enumerate(html_entries):
            prefix = '│   └── ' if i == len(html_entries) - 1 else '│   ├── '
            lines.append(f'{prefix}{entry.file_name}')

        # Source files by version
        lines.append('└── src/')

        # Group files by version
        files_by_version = {}
        for chain in manifest.load_chains:
            for dep in chain.files:
                version = str(dep.source_version)
                if version not in files_by_version:
                    files_by_version[version] = []
                files_by_version[version].append(dep)

        sorted_versions = sorted(files_by_version.keys())
        for vi, version in enumerate(sorted_versions):
            is_last_version = (vi == len(sorted_versions) - 1)
            version_prefix  = '    └── ' if is_last_version else '    ├── '
            lines.append(f'{version_prefix}{version}/')

            deps         = files_by_version[version]
            inner_prefix = '        ' if is_last_version else '    │   '

            # Sort files alphabetically
            sorted_deps = sorted(deps, key=lambda d: str(d.logical_name))
            for fi, dep in enumerate(sorted_deps):
                is_last_file = (fi == len(sorted_deps) - 1)
                file_prefix  = f'{inner_prefix}└── ' if is_last_file else f'{inner_prefix}├── '
                file_name    = f'{dep.logical_name}.{dep.resource_type}'
                lines.append(f'{file_prefix}{file_name}')

        return '\n'.join(lines)

    # ═══════════════════════════════════════════════════════════════════════════
    # Zip Building
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def build_zip_bytes(self                                       ,                       # Build in-memory zip
                        manifest : Schema__IFD_Manifest            ,
                        content  : str
                   ) -> bytes:
        with Temp_Zip_In_Memory() as zip_mem:
            # Add manifest and content
            manifest_json = json_dumps(manifest.json())
            zip_mem.add_file_from_content('manifest.json', manifest_json)
            zip_mem.add_file_from_content('content.txt'  , str(content) )

            # Add HTML entry points
            for entry in manifest.html_entry_points:
                html_content = file_contents(str(entry.file_path))
                if html_content:
                    target = f'html/{entry.file_name}'
                    zip_mem.add_file_from_content(target, html_content)

            # Add source files
            for chain in manifest.load_chains:
                for dep in chain.files:
                    file_content = file_contents(str(dep.resolved_path))
                    if file_content:
                        target = f'src/{dep.source_version}/{dep.logical_name}.{dep.resource_type}'
                        zip_mem.add_file_from_content(target, file_content)

            return zip_mem.zip_bytes()

    # ═══════════════════════════════════════════════════════════════════════════
    # Folder Extraction
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def extract_to_folder(self                                     ,                       # Extract snapshot to folder
                          manifest    : Schema__IFD_Manifest       ,
                          content     : str                   ,
                          output_path : Safe_Str__File__Path
                     ) -> bool:
        # Build zip first (reuse logic), then extract
        zip_bytes = self.build_zip_bytes(manifest, content)

        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zf:
            zf.extractall(str(output_path))

        return True
