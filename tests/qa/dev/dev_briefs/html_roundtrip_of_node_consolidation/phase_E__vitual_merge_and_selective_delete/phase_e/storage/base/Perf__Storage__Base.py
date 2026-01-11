# ═══════════════════════════════════════════════════════════════════════════════
# Perf__Storage__Base - Abstract base class for storage backends
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import Optional, List
from abc                                                                        import abstractmethod
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from phase_e.storage.safe_str.Safe_Str__Session_Name                            import Safe_Str__Session_Name
from phase_e.storage.safe_str.Safe_Str__Target_Name                             import Safe_Str__Target_Name


class Perf__Storage__Base(Type_Safe):                                           # Abstract storage backend
    session_name : Safe_Str__Session_Name                                       # Current session context
    target_name  : Safe_Str__Target_Name                                        # Current target context
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Context Management
    # ═══════════════════════════════════════════════════════════════════════════
    
    @type_safe
    def set_context(self                                    ,                   # Set session/target context
                    session_name : Safe_Str__Session_Name   ,                   # Session identifier
                    target_name  : Safe_Str__Target_Name    ) -> None:          # Target identifier
        self.session_name = session_name
        self.target_name  = target_name
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Abstract Methods - Must be implemented by subclasses
    # ═══════════════════════════════════════════════════════════════════════════
    
    @abstractmethod
    def save(self, key: str, data: dict) -> bool:                               # Save JSON data
        pass
    
    @abstractmethod
    def save_string(self, key: str, content: str) -> bool:                      # Save string content
        pass
    
    @abstractmethod
    def load(self, key: str) -> Optional[dict]:                                 # Load JSON data
        pass
    
    @abstractmethod
    def load_string(self, key: str) -> Optional[str]:                           # Load string content
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:                                         # Check if key exists
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:                                         # Delete data by key
        pass
    
    @abstractmethod
    def list_keys(self, prefix: str = '') -> List[str]:                         # List stored keys
        pass
