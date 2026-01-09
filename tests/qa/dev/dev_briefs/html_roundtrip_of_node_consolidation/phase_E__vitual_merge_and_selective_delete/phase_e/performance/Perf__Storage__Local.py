# ═══════════════════════════════════════════════════════════════════════════════
# Perf__Storage__Local - Local disk storage for benchmark results
# Part of Phase E_1: Performance Analysis
#
# Stores results as JSON files in a local directory
# Can be replaced with Perf__Storage__Web_Service in future
# ═══════════════════════════════════════════════════════════════════════════════

from datetime                                                                   import datetime
from typing                                                                     import List, Optional
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from osbot_utils.utils.Files import file_exists, file_delete, folder_create, folder_exists, files_list, path_combine, file_save
from osbot_utils.utils.Json                                                     import json_load_file, json_save_file_pretty
from phase_e.performance.Perf__Storage__Base                                    import Perf__Storage__Base


class Perf__Storage__Local(Perf__Storage__Base):                                # Local disk storage

    storage_path : str = './perf_results'                                       # Default storage directory

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ensure_storage_dir()

    # ═══════════════════════════════════════════════════════════════════════════
    # Abstract Method Implementations
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def save(self                  ,                                            # Save data to JSON file
             key  : str            ,
             data : dict           ) -> bool:
        file_path = self.key_to_path(key)
        result    = json_save_file_pretty(data, file_path)

        return result is not None

    @type_safe
    def load(self                  ,                                            # Load data from JSON file
             key : str             ) -> Optional[dict]:
        file_path = self.key_to_path(key)

        if not file_exists(file_path):
            return None

        data = json_load_file(file_path)

        return data if data else None

    @type_safe
    def list_keys(self             ,                                            # List all stored keys
                  prefix: str = '' ) -> List[str]:
        if not folder_exists(self.storage_path):
            return []

        all_files = files_list(self.storage_path, pattern='*.json')
        keys      = [self.path_to_key(f) for f in all_files]

        if prefix:
            keys = [k for k in keys if k.startswith(prefix)]

        return sorted(keys)

    @type_safe
    def exists(self                ,                                            # Check if key exists
               key : str           ) -> bool:
        return file_exists(self.key_to_path(key))

    @type_safe
    def delete(self                ,                                            # Delete data by key
               key : str           ) -> bool:
        return file_delete(self.key_to_path(key))

    # ═══════════════════════════════════════════════════════════════════════════
    # Key Generation Helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_timestamped_key(self               ,                           # Generate key with timestamp
                                 prefix : str = ''  ) -> str:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        if prefix:
            return f"{prefix}_{timestamp}"

        return timestamp

    def generate_session_key(self                   ,                           # Generate session key
                             session_name : str = 'benchmark') -> str:
        return self.generate_timestamped_key(session_name)

    # ═══════════════════════════════════════════════════════════════════════════
    # Path Conversion
    # ═══════════════════════════════════════════════════════════════════════════

    def key_to_path(self, key: str, extension='json') -> str:                                     # Convert key to file path
        safe_key = key.replace('/', '_').replace('\\', '_')
        return path_combine(self.storage_path, f"{safe_key}.{extension}")

    def path_to_key(self, file_path: str) -> str:                               # Convert file path to key
        from osbot_utils.utils.Files import file_name_without_extension
        return file_name_without_extension(file_path)

    # ═══════════════════════════════════════════════════════════════════════════
    # Directory Management
    # ═══════════════════════════════════════════════════════════════════════════

    def ensure_storage_dir(self) -> None:                                       # Create storage directory
        folder_create(self.storage_path)

    def clear_all(self) -> int:                                                 # Delete all stored data
        deleted = 0
        for key in self.list_keys():
            if self.delete(key):
                deleted += 1
        return deleted

    def get_storage_info(self) -> dict:                                         # Get storage statistics
        from osbot_utils.utils.Files import file_size

        keys       = self.list_keys()
        total_size = 0

        for key in keys:
            file_path = self.key_to_path(key)
            if file_exists(file_path):
                total_size += file_size(file_path)

        return {'path'       : str(self.storage_path),
                'key_count'  : len(keys)             ,
                'total_bytes': total_size            }

    # ═══════════════════════════════════════════════════════════════════════════
    # Schema Serialization Helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def save_schema(self               ,                                        # Save Type_Safe schema
                    key    : str       ,
                    schema             ) -> bool:
        return self.save(key, schema.json())

    def save_analysis(self                      ,                               # Save analysis with auto-key
                      analysis                  ,
                      prefix : str = 'analysis' ) -> str:
        key = self.generate_timestamped_key(prefix)
        self.save_schema(key, analysis)
        return key

    @type_safe
    def save_report(self                  ,                                            # Save data to JSON file
             key  : str            ,
             report : str           ) -> bool:
        file_path = self.key_to_path(key, extension='txt')
        result    = file_save(report, file_path)

        return result is not None