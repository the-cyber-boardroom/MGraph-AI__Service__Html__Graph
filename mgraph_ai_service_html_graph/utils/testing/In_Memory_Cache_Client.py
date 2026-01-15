# ═══════════════════════════════════════════════════════════════════════════════
# In-Memory Cache Client for Tests
# Provides real behavior without external dependencies
# ═══════════════════════════════════════════════════════════════════════════════

import uuid
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id import Cache_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid import Random_Guid
from osbot_utils.type_safe.type_safe_core.decorators.type_safe import type_safe

# todo: see if we really need this
class In_Memory_Cache_Client(Type_Safe):                                         # In-memory cache for tests
    storage : dict                                                               # In-memory storage

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = {}

    def file__refs__by_json_value(self                     ,                     # Find by field value
                                  namespace       : str    ,
                                  json_field_path : str    ,
                                  json_value      : str    ):
        key = f"refs:{namespace}:{json_field_path}:{json_value}"
        return self.storage.get(key)

    @type_safe
    def file__create(self                         ,                              # Create new entry
                     namespace       : str        ,
                     cache_key       : str        ,
                     file_id         : str        ,
                     json_field_path : str        ,
                     data            : dict
                ) -> Cache_Id:
        cache_id = Random_Guid()

        # Store entry
        entry_key = f"{namespace}:{cache_id}"
        self.storage[entry_key] = data

        # Store refs for lookup
        ref_key = f"refs:{namespace}:{json_field_path}:{cache_key}"
        result  = type('CacheResult', (), {'cache_id': cache_id})()
        self.storage[ref_key] = result

        return result

    def file__contents__json(self, namespace: str, cache_id: str):               # Get entry JSON
        entry_key = f"{namespace}:{cache_id}"
        return self.storage.get(entry_key)

    def file__update(self, namespace: str, cache_id: str, data: dict):           # Update entry
        entry_key = f"{namespace}:{cache_id}"
        self.storage[entry_key] = data
        return True

    def file__add_data__json(self                       ,                        # Add child JSON
                             namespace    : str         ,
                             cache_id     : str         ,
                             data_key     : str         ,
                             data_file_id : str         ,
                             data         : dict        ):
        child_key = f"{namespace}:{cache_id}:json:{data_key}:{data_file_id}"
        self.storage[child_key] = data
        return True

    def file__data__json(self                       ,                            # Get child JSON
                         namespace    : str         ,
                         cache_id     : str         ,
                         data_key     : str         ,
                         data_file_id : str         ):
        child_key = f"{namespace}:{cache_id}:json:{data_key}:{data_file_id}"
        return self.storage.get(child_key)

    def file__add_data__string(self                       ,                      # Add child string
                               namespace    : str         ,
                               cache_id     : str         ,
                               data_key     : str         ,
                               data_file_id : str         ,
                               content      : str         ):
        child_key = f"{namespace}:{cache_id}:string:{data_key}:{data_file_id}"
        self.storage[child_key] = content
        return True

    def file__data__string(self                       ,                          # Get child string
                           namespace    : str         ,
                           cache_id     : str         ,
                           data_key     : str         ,
                           data_file_id : str         ):
        child_key = f"{namespace}:{cache_id}:string:{data_key}:{data_file_id}"
        return self.storage.get(child_key)

    def file__data__exists(self                       ,                          # Check child exists
                           namespace    : str         ,
                           cache_id     : str         ,
                           data_key     : str         ,
                           data_file_id : str         ):
        json_key   = f"{namespace}:{cache_id}:json:{data_key}:{data_file_id}"
        string_key = f"{namespace}:{cache_id}:string:{data_key}:{data_file_id}"
        return json_key in self.storage or string_key in self.storage

    def file__data__delete(self                       ,                          # Delete child
                           namespace    : str         ,
                           cache_id     : str         ,
                           data_key     : str         ,
                           data_file_id : str         ):
        json_key   = f"{namespace}:{cache_id}:json:{data_key}:{data_file_id}"
        string_key = f"{namespace}:{cache_id}:string:{data_key}:{data_file_id}"
        deleted    = False
        if json_key in self.storage:
            del self.storage[json_key]
            deleted = True
        if string_key in self.storage:
            del self.storage[string_key]
            deleted = True
        return deleted

    def clear(self):                                                             # Clear all storage
        self.storage.clear()

    def storage_size(self) -> int:                                               # Get storage entry count
        return len(self.storage)


@type_safe
def create_in_memory_cache_client() -> In_Memory_Cache_Client:                   # Factory for test cache
    return In_Memory_Cache_Client()
