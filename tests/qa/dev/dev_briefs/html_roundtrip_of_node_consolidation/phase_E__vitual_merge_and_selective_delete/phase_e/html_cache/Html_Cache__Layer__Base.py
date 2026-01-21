import hashlib
import time

from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type import Enum__Cache__Data_Type

from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                import Cache_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id   import Safe_Str__Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                    import type_safe
from phase_e.html_cache.schemas.Schema__Html_Cache                                import Schema__Html_Cache__Config, Schema__Html_Cache__Stats
from phase_e.storage.base.Perf__Storage__Base                                     import Perf__Storage__Base


class Html_Cache__Layer__Base(Type_Safe):                       # Base class for all cache layers
    storage      : Perf__Storage__Base
    config       : Schema__Html_Cache__Config                   # Configuration options
    stats        : Schema__Html_Cache__Stats                    # Hit/miss tracking
    layer_name   : Safe_Str__Id                                 # Layer identifier: 'L1', 'L2', 'L3'

    def cache_id(self) -> Cache_Id:                               # Get cache_id from storage
        return self.storage.cache_id()

    def cache_hash(self):
        return self.storage.cache_hash()

    def cache_key(self):
        return self.storage.cache_key()

    def data_folder(self):
        return self.storage.data_folder()

    def data_file(self) -> Safe_Str__File__Path:
        return self.storage.data_file(data_type = Enum__Cache__Data_Type.STRING,
                                      key_data  = self.key_data())

    def file_folder(self):
        return self.storage.file_folder()

    def timestamp(self) -> float:                                  # Get current timestamp
        return time.time()

    @type_safe
    def key_data(self) -> Safe_Str__File__Path:                 # Key for main data file (override in subclass)
        return f"{self.layer_name}/data"

    @type_safe
    def key_metadata(self) -> Safe_Str__File__Path:             # Key for metadata file
        return f"{self.layer_name}/metadata"

    def exists(self) -> bool:                                   # Check if layer data exists for current target
        return self.storage.file_exist(path=self.data_file())

    def content_hash(self, content: str) -> str:                # Generate hash for content-addressable lookup
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

    def save_metadata(self, cache_id: Cache_Id, metadata: dict) -> bool:    # Save metadata for this layer
        return self.storage.save(cache_id = cache_id,
                                 key      = self.key_metadata(),
                                 data     = metadata)

    def load_metadata(self, cache_id: Cache_Id) -> dict:                    # Load metadata for this layer
        return self.storage.load__json(cache_id = cache_id,
                                       key      = self.key_metadata())

    def delete(self, cache_id: Cache_Id) -> bool:               # Delete layer data (override in subclass)
        raise NotImplementedError