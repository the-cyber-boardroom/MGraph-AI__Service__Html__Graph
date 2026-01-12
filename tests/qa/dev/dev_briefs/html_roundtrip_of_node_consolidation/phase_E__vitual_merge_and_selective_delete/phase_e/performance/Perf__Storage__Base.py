# note: this was refactored to phase_e/storage/base/Perf__Storage__Base

# # ═══════════════════════════════════════════════════════════════════════════════
# # Perf__Storage__Base - Abstract base for benchmark result storage
# # Part of Phase E_1: Performance Analysis
# #
# # Designed for future replacement with web service / caching solution
# # ═══════════════════════════════════════════════════════════════════════════════
#
# from abc                                                                        import abstractmethod
# from typing                                                                     import Dict, List, Optional
# from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
# from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str
#
#
# class Perf__Storage__Base(Type_Safe):                                           # Abstract base for storage
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Abstract Methods - Must be implemented by subclasses
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     @abstractmethod
#     def save(self                  ,                                            # Save data with key
#              key  : str            ,                                            # Unique identifier
#              data : dict           ) -> bool:                                   # Data to store
#         pass
#
#     @abstractmethod
#     def load(self                  ,                                            # Load data by key
#              key : str             ) -> Optional[dict]:                         # Returns None if not found
#         pass
#
#     @abstractmethod
#     def list_keys(self             ,                                            # List all stored keys
#                   prefix: str = '' ) -> List[str]:                              # Optional prefix filter
#         pass
#
#     @abstractmethod
#     def exists(self                ,                                            # Check if key exists
#                key : str           ) -> bool:
#         pass
#
#     @abstractmethod
#     def delete(self                ,                                            # Delete data by key
#                key : str           ) -> bool:
#         pass
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Convenience Methods - Built on abstract methods
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     def save_if_not_exists(self        ,                                        # Save only if key doesn't exist
#                            key  : str  ,
#                            data : dict ) -> bool:
#         if self.exists(key):
#             return False
#         return self.save(key, data)
#
#     def load_or_default(self               ,                                    # Load with default value
#                         key     : str      ,
#                         default : dict = None) -> dict:
#         result = self.load(key)
#         if result is None:
#             return default or {}
#         return result
#
#     def load_all(self, prefix: str = '') -> Dict[str, dict]:                    # Load all matching keys
#         results = {}
#         for key in self.list_keys(prefix):
#             data = self.load(key)
#             if data is not None:
#                 results[key] = data
#         return results