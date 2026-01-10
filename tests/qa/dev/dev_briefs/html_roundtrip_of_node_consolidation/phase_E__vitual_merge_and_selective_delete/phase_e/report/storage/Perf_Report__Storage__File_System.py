# ═══════════════════════════════════════════════════════════════════════════════
# Perf_Report__Storage__File_System - File system storage implementation
# Saves reports to local files
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                             import List
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                          import type_safe
from osbot_utils.utils.Files                                                                            import path_combine, file_create, file_contents, folder_files, file_exists, folder_create
from osbot_utils.utils.Json                                                                             import json_loads
from phase_e.report.storage.Perf_Report__Storage__Base                                                import Perf_Report__Storage__Base
from phase_e.report.schemas.Schema__Perf_Report                                                       import Schema__Perf_Report


class Perf_Report__Storage__File_System(Perf_Report__Storage__Base):  # File system storage
    storage_path : str                                            # Base path for reports

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.storage_path:
            folder_create(self.storage_path)                      # Ensure folder exists

    # ═══════════════════════════════════════════════════════════════════════════
    # Storage Implementation
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def save_content(self                                     ,   # Save to file
                     key         : str                        ,
                     content     : str                        ,
                     format_type : str
                ) -> bool:
        file_path = self.build_file_path(key, format_type)
        file_create(file_path, content)
        return True

    @type_safe
    def load(self, key: str) -> Schema__Perf_Report:              # Load from JSON file
        file_path = self.build_file_path(key, 'json')

        if file_exists(file_path) is False:
            return None

        content = file_contents(file_path)
        if content is None:
            return None

        data = json_loads(content)
        if data is None:
            return None

        return Schema__Perf_Report.from_json(data)

    @type_safe
    def list_reports(self) -> List[str]:                          # List all report keys
        if self.storage_path is None:
            return []

        files = folder_files(self.storage_path, '*.json')
        keys  = []

        for file_path in files:
            # Extract key from filename (remove .json extension)
            filename = file_path.split('/')[-1]
            if filename.endswith('.json'):
                key = filename[:-5]                               # Remove .json
                keys.append(key)

        return sorted(keys)

    @type_safe
    def exists(self, key: str) -> bool:                           # Check if report exists
        file_path = self.build_file_path(key, 'json')
        return file_exists(file_path)

    # ═══════════════════════════════════════════════════════════════════════════
    # Helpers
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def build_file_path(self                                  ,   # Construct file path
                        key         : str                     ,
                        format_type : str
                   ) -> str:
        filename = f'{key}.{format_type}'
        return path_combine(self.storage_path, filename)
