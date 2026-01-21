import json

from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type import Enum__Cache__Data_Type

from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document                              import Html_MGraph__Document
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                               import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                              import Cache_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id                                 import Safe_Str__Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                  import type_safe
from phase_e.html_cache.Html_Cache__Layer__Base                                                                 import Html_Cache__Layer__Base
from phase_e.html_cache.schemas.Schema__Html_Cache                                                              import Schema__Html_Cache__Metadata__L3


class Html_Cache__Layer__MGraph(Html_Cache__Layer__Base):               # L3: MGraph document caching
    layer_name: Safe_Str__Id = 'L3'

    def data_file(self) -> Safe_Str__File__Path:
        return self.storage.data_file(data_type = Enum__Cache__Data_Type.JSON,
                                      key_data  = self.key_data())

    @type_safe
    def key_data(self) -> Safe_Str__File__Path:                         # Key for document data
        return f"{self.layer_name}/mgraph-document"

    def save(self,                                                      # Save MGraph document using .json() serialization
             cache_id : Cache_Id,
             document : Html_MGraph__Document
        ) -> bool:
        doc_json = document.json()
        save_ok  = self.storage.save(cache_id = cache_id,
                                     key      = self.key_data(),
                                     data     = doc_json)

        if save_ok:
            # Calculate hash and stats
            doc_str    = json.dumps(doc_json, sort_keys=True)
            node_count = 0
            edge_count = 0

            # Try to get stats from document

            if hasattr(document, 'body_graph') and document.body_graph:
                body_stats = document.body_graph.stats()
                if body_stats:
                    node_count += body_stats.total_nodes
                    edge_count += body_stats.total_edges

            metadata = Schema__Html_Cache__Metadata__L3(content_hash = self.content_hash(doc_str),
                                                        node_count   = node_count,
                                                        edge_count   = edge_count)
            self.save_metadata(cache_id = cache_id,
                               metadata = metadata.json())

        return save_ok


    def load(self, cache_id: Cache_Id) -> Html_MGraph__Document:        # Load MGraph document using .from_json() deserialization
        doc_json = self.storage.load__json(cache_id = cache_id,
                                           key      = self.key_data())
        if doc_json is not None:
            document = Html_MGraph__Document.from_json(doc_json)
            self.stats.l3_hits += 1
            return document
        else:
            self.stats.l3_misses += 1
            return None

    def build_from_dict(self, html_dict: dict) -> Html_MGraph__Document:  # Create MGraph from dict
        converter = Html__To__Html_MGraph__Document__Node_Id_Reuse()
        document  = converter.convert_from_dict(html_dict)
        self.stats.l3_builds += 1
        return document

    def get_content_hash(self, cache_id: Cache_Id) -> str:              # Get content hash without loading full document
        metadata = self.load_metadata(cache_id=cache_id)
        if metadata:
            return metadata.get('content_hash')
        return None

    def delete(self, cache_id: Cache_Id) -> bool:                       # Delete MGraph data and metadata
        return self.storage.file_delete(cache_id  = cache_id                   ,
                                        data_type = Enum__Cache__Data_Type.JSON,
                                        path      = self.data_file()           ,
                                        key_data  = self.key_data()            )