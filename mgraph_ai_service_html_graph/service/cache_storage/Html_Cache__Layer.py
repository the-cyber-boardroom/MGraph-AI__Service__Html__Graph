# ═══════════════════════════════════════════════════════════════════════════════
# Html_Cache__Layer - Provides access to a single transformation layer
# Each layer stores the output of one LETS transformation
# ═══════════════════════════════════════════════════════════════════════════════

from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type           import Enum__Cache__Data_Type
from osbot_utils.type_safe.Type_Safe                                                     import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                           import type_safe
from mgraph_ai_service_html_graph.service.cache_storage.safe_str.Safe_Str__Layer_Name    import Safe_Str__Layer_Name
from mgraph_ai_service_html_graph.service.cache_storage.safe_str.Safe_Str__Data_File_Id  import Safe_Str__Data_File_Id

# todo: refactor the logic of having the document object here (which should be Html_Cache__Document,
#         but we can't add it as the type due to circular refs
#         this is why we have a warning below on methods like self.document.client
class Html_Cache__Layer(Type_Safe):                                              # Single layer accessor
    document   : Type_Safe                                                       # Html_Cache__Document (forward ref)
    layer_name : Safe_Str__Layer_Name                                            # Layer identifier

    # ═══════════════════════════════════════════════════════════════════════════
    # JSON Operations
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def save_json(self,                                                          # Save JSON to layer
                  file_id : Safe_Str__Data_File_Id,                              # File identifier
                  data    : dict                                                 # JSON data
             ) -> bool:
        result = self.document.client.data__store_json(namespace    = self.document.namespace        ,
                                                       cache_id     = self.document.ensure_cache_id(),
                                                       data_key     = self.layer_name                ,
                                                       data_file_id = file_id                        ,
                                                       data         = data                           )
        return result is not None

    @type_safe
    def load_json(self,                                                          # Load JSON from layer
                  file_id: Safe_Str__Data_File_Id
             ) -> dict:                                                          # Returns None if not found
        return self.document.client.data__retrieve_json(namespace    = self.document.namespace        ,
                                                        cache_id     = self.document.ensure_cache_id(),
                                                        data_key     = self.layer_name                ,
                                                        data_file_id = file_id                        )

    @type_safe
    def update_json(self,                                                        # Update JSON in layer
                    file_id : Safe_Str__Data_File_Id,                            # File identifier
                    data    : dict                                               # New JSON data
               ) -> bool:
        return self.document.client.data__update_json(namespace    = self.document.namespace        ,
                                                      cache_id     = self.document.ensure_cache_id(),
                                                      data_key     = self.layer_name                ,
                                                      data_file_id = file_id                        ,
                                                      data         = data                           )

    # ═══════════════════════════════════════════════════════════════════════════
    # String Operations
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def save_string(self,                                                        # Save string to layer
                    file_id : Safe_Str__Data_File_Id,                            # File identifier
                    content : str                                                # String content
               ) -> bool:
        result = self.document.client.data__store_string(namespace    = self.document.namespace        ,
                                                         cache_id     = self.document.ensure_cache_id(),
                                                         data_key     = self.layer_name                ,
                                                         data_file_id = file_id                        ,
                                                         content      = content                        )
        return result is not None

    @type_safe
    def load_string(self,                                                        # Load string from layer
                    file_id: Safe_Str__Data_File_Id
               ) -> str:                                                         # Returns None if not found
        return self.document.client.data__retrieve_string(namespace    = self.document.namespace        ,
                                                          cache_id     = self.document.ensure_cache_id(),
                                                          data_key     = self.layer_name                ,
                                                          data_file_id = file_id                        )

    @type_safe
    def update_string(self,                                                      # Update string in layer
                      file_id : Safe_Str__Data_File_Id,                          # File identifier
                      content : str                                              # New string content
                 ) -> bool:
        return self.document.client.data__update_string(namespace    = self.document.namespace        ,
                                                        cache_id     = self.document.ensure_cache_id(),
                                                        data_key     = self.layer_name                ,
                                                        data_file_id = file_id                        ,
                                                        content      = content                        )

    # ═══════════════════════════════════════════════════════════════════════════
    # Existence / Deletion / Listing
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def exists(self,                                                             # Check if file exists
               file_id   : Safe_Str__Data_File_Id,
               data_type : Enum__Cache__Data_Type = Enum__Cache__Data_Type.STRING
          ) -> bool:
        return self.document.client.data__exists(namespace    = self.document.namespace        ,
                                                 cache_id     = self.document.ensure_cache_id(),
                                                 data_key     = self.layer_name                ,
                                                 data_file_id = file_id                        ,
                                                 data_type    = data_type                      )

    @type_safe
    def delete(self,                                                             # Delete file from layer
               file_id   : Safe_Str__Data_File_Id,
               data_type : Enum__Cache__Data_Type = Enum__Cache__Data_Type.STRING
          ) -> bool:
        return self.document.client.data__delete(namespace    = self.document.namespace        ,
                                                 cache_id     = self.document.ensure_cache_id(),
                                                 data_key     = self.layer_name                ,
                                                 data_file_id = file_id                        ,
                                                 data_type    = data_type                      )

    def list_files(self, recursive: bool = True):                                # List all files in layer
        return self.document.client.data__list(namespace = self.document.namespace        ,
                                               cache_id  = self.document.ensure_cache_id(),
                                               data_key  = self.layer_name                ,
                                               recursive = recursive                      )
