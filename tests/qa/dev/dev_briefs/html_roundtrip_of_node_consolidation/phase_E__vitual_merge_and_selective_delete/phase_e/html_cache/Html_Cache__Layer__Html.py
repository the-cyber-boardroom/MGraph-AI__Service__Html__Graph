from typing                                                                       import Optional

from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type import Enum__Cache__Data_Type

from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                import Cache_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id   import Safe_Str__Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                    import type_safe
from phase_e.html_cache.Html_Cache__Layer__Base                                   import Html_Cache__Layer__Base
from phase_e.html_cache.schemas.Schema__Html_Cache                                import Schema__Html_Cache__Metadata__L1


class Html_Cache__Layer__Html(Html_Cache__Layer__Base):                 # L1: Raw HTML caching
    layer_name: Safe_Str__Id = 'L1'

    @type_safe
    def key_data(self) -> Safe_Str__File__Path:                         # Override to use .html extension
        return f"{self.layer_name}/raw-html"

    def save(self,                                                      # Save raw HTML with metadata
             cache_id : Cache_Id,
             html     : str,
             source   : str = 'unknown'
        ) -> bool:
        # Save HTML string
        save_ok = self.storage.save_string(cache_id = cache_id,
                                           key      = self.key_data(),
                                           content  = html)

        if save_ok:
            # Save metadata
            metadata = Schema__Html_Cache__Metadata__L1(source       = source,
                                                        content_hash = self.content_hash(html),
                                                        size_bytes   = len(html.encode('utf-8')))
            self.save_metadata(cache_id = cache_id,
                               metadata = metadata.json())

        return save_ok

    def load(self, cache_id: Cache_Id) -> str:                          # Load raw HTML
        html = self.storage.load_string(cache_id = cache_id,
                                        key      = self.key_data())
        if html is not None:
            self.stats.l1_hits += 1
        else:
            self.stats.l1_misses += 1
        return html

    def get_content_hash(self, cache_id: Cache_Id) -> str:              # Get content hash without loading full HTML
        metadata = self.load_metadata(cache_id=cache_id)
        if metadata:
            return metadata.get('content_hash')
        return None

    def delete(self, cache_id: Cache_Id) -> bool:                       # Delete HTML data and metadata
        return self.storage.file_delete(cache_id  = cache_id                     ,
                                        data_type = Enum__Cache__Data_Type.STRING,
                                        path      = self.data_file()             ,
                                        key_data  = self.key_data()              )