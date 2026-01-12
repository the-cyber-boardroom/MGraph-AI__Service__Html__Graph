from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type                       import Enum__Cache__Data_Type
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids import Html__To__Html_Dict__With__Node_Ids
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                    import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                   import Cache_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id                      import Safe_Str__Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                       import type_safe
from phase_e.html_cache.Html_Cache__Layer__Base                                                      import Html_Cache__Layer__Base


class Html_Cache__Layer__Html__Dict(Html_Cache__Layer__Base):                 # L2: Parsed HTML dict caching
    layer_name : Safe_Str__Id = 'L2'

    def delete(self, cache_id: Cache_Id) -> bool:
        return self.storage.file_delete(cache_id  = cache_id                   ,
                                        data_type = Enum__Cache__Data_Type.JSON,
                                        path      = self.data_file()           ,
                                        key_data = self.key_data()             )

    def data_file(self) -> Safe_Str__File__Path:
        return self.storage.data_file(data_type = Enum__Cache__Data_Type.JSON,
                                      key_data  = self.key_data())

    def exists(self) -> bool:
        return self.storage.file_exist(path=self.data_file())

    @type_safe
    def key_data(self) -> Safe_Str__File__Path:                               # Key for dict data
        return f"{self.layer_name}/html-dict"

    @type_safe
    def save(self,                                                            # Save parsed HTML dict
             cache_id : Cache_Id,
             html_dict: dict
        ) -> bool:

        save_ok = self.storage.save(cache_id = cache_id       ,
                                    key      = self.key_data(),
                                    data     = html_dict      )
        return save_ok

    def load(self, cache_id: Cache_Id) -> dict:                               # Load parsed HTML dict
        html_dict = self.storage.load__json(cache_id = cache_id, key=self.key_data())
        if html_dict is not None:
            self.stats.l2_hits += 1
        else:
            self.stats.l2_misses += 1
        return html_dict

    def build_from_html(self, html: str) -> dict:                             # Parse HTML to dict using converter
        html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()
        self.stats.l2_builds += 1
        return html_dict

    def get_content_hash(self, cache_id: Cache_Id) -> str:                    # Get content hash from metadata
        metadata = self.load_metadata(cache_id=cache_id)
        if metadata:
            return metadata.get('content_hash')
        return None