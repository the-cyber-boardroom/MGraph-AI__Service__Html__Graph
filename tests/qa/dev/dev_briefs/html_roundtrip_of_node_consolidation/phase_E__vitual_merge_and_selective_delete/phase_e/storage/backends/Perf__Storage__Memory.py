# ═══════════════════════════════════════════════════════════════════════════════
# Perf__Storage__Memory - In-memory storage backend for testing
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import Optional, List
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from phase_e.storage.base.Perf__Storage__Base                                   import Perf__Storage__Base
from phase_e.storage.safe_str.Safe_Str__Session_Name                            import Safe_Str__Session_Name
from phase_e.storage.safe_str.Safe_Str__Target_Name                             import Safe_Str__Target_Name


class Perf__Storage__Memory(Perf__Storage__Base):                               # In-memory storage backend
    data : dict                                                                 # Storage dict (auto-init {})
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Path Helpers
    # ═══════════════════════════════════════════════════════════════════════════
    
    def context_key(self) -> str:                                               # Generate context prefix
        return f"{self.session_name}/{self.target_name}"
    
    def full_key(self, key: str) -> str:                                        # Generate full storage key
        return f"{self.context_key()}/{key}"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Abstract Method Implementations
    # ═══════════════════════════════════════════════════════════════════════════
    
    @type_safe
    def save(self                  ,                                            # Save JSON data
             key  : str            ,                                            # Data key
             data : dict           ) -> bool:                                   # Data to store
        full_key            = self.full_key(key)
        self.data[full_key] = data
        return True
    
    @type_safe
    def save_string(self                  ,                                     # Save string content
                    key     : str         ,                                     # Data key
                    content : str         ) -> bool:                            # String content
        full_key            = self.full_key(key)
        self.data[full_key] = content
        return True
    
    @type_safe
    def load(self             ,                                                 # Load JSON data
             key : str        ) -> Optional[dict]:                              # Returns None if not found
        full_key = self.full_key(key)
        return self.data.get(full_key)
    
    @type_safe
    def load_string(self             ,                                          # Load string content
                    key : str        ) -> Optional[str]:                        # Returns None if not found
        full_key = self.full_key(key)
        return self.data.get(full_key)
    
    @type_safe
    def exists(self             ,                                               # Check if key exists
               key : str        ) -> bool:
        full_key = self.full_key(key)
        return full_key in self.data
    
    @type_safe
    def delete(self             ,                                               # Delete data by key
               key : str        ) -> bool:
        full_key = self.full_key(key)
        if full_key in self.data:
            del self.data[full_key]
            return True
        return False
    
    @type_safe
    def list_keys(self                  ,                                       # List stored keys
                  prefix : str = ''     ) -> List[str]:                         # Optional prefix filter
        context = self.context_key()
        keys    = [k.replace(f"{context}/", '') 
                   for k in self.data.keys() 
                   if k.startswith(context)]
        if prefix:
            keys = [k for k in keys if k.startswith(prefix)]
        return sorted(keys)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Memory-Specific Methods
    # ═══════════════════════════════════════════════════════════════════════════
    
    def clear(self) -> None:                                                    # Clear all stored data
        self.data.clear()
    
    def clear_context(self) -> None:                                            # Clear current context data
        context = self.context_key()
        keys_to_delete = [k for k in self.data.keys() if k.startswith(context)]
        for key in keys_to_delete:
            del self.data[key]
