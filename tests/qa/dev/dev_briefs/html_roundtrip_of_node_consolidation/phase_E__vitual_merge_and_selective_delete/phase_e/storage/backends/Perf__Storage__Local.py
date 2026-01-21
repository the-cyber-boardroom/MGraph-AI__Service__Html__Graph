# ═══════════════════════════════════════════════════════════════════════════════
# Perf__Storage__Local - Local disk storage backend
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import Optional, List
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path
from osbot_utils.utils.Files                                                    import file_exists, folder_create, folder_exists, files_list
from osbot_utils.utils.Json                                                     import json_load_file, json_save_file_pretty
from phase_e.storage.base.Perf__Storage__Base                                   import Perf__Storage__Base
from phase_e.storage.safe_str.Safe_Str__Session_Name                            import Safe_Str__Session_Name
from phase_e.storage.safe_str.Safe_Str__Target_Name                             import Safe_Str__Target_Name


class Perf__Storage__Local(Perf__Storage__Base):                                # Local disk storage backend
    storage_path : Safe_Str__File__Path = './perf_results'                      # Root storage directory
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Path Helpers
    # ═══════════════════════════════════════════════════════════════════════════
    
    def context_path(self) -> str:                                              # Get context directory path
        return f"{self.storage_path}/sessions/{self.session_name}/targets/{self.target_name}"
    
    def full_path(self, key: str) -> str:                                       # Get full file path for key
        return f"{self.context_path()}/{key}"
    
    def ensure_directory(self, path: str) -> None:                              # Ensure parent directory exists
        import os
        dir_path = os.path.dirname(path)
        if dir_path and not folder_exists(dir_path):
            folder_create(dir_path)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Abstract Method Implementations
    # ═══════════════════════════════════════════════════════════════════════════
    
    @type_safe
    def save(self                  ,                                            # Save JSON data
             key  : str            ,                                            # Data key
             data : dict           ) -> bool:                                   # Data to store
        path = self.full_path(key)
        self.ensure_directory(path)
        json_save_file_pretty(data, path)
        return True
    
    @type_safe
    def save_string(self                  ,                                     # Save string content
                    key     : str         ,                                     # Data key
                    content : str         ) -> bool:                            # String content
        path = self.full_path(key)
        self.ensure_directory(path)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    @type_safe
    def load(self             ,                                                 # Load JSON data
             key : str        ) -> Optional[dict]:                              # Returns None if not found
        path = self.full_path(key)
        if file_exists(path) is False:
            return None
        return json_load_file(path)
    
    @type_safe
    def load_string(self             ,                                          # Load string content
                    key : str        ) -> Optional[str]:                        # Returns None if not found
        path = self.full_path(key)
        if file_exists(path) is False:
            return None
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @type_safe
    def exists(self             ,                                               # Check if key exists
               key : str        ) -> bool:
        return file_exists(self.full_path(key))
    
    @type_safe
    def delete(self             ,                                               # Delete data by key
               key : str        ) -> bool:
        import os
        path = self.full_path(key)
        if file_exists(path):
            os.remove(path)
            return True
        return False
    
    @type_safe
    def list_keys(self                  ,                                       # List stored keys
                  prefix : str = ''     ) -> List[str]:                         # Optional prefix filter
        import os
        context_dir = self.context_path()
        if not folder_exists(context_dir):
            return []
        
        keys = []
        for root, dirs, files in os.walk(context_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path  = os.path.relpath(full_path, context_dir)
                if prefix and not rel_path.startswith(prefix):
                    continue
                keys.append(rel_path)
        
        return sorted(keys)
