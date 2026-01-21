# ═══════════════════════════════════════════════════════════════════════════════
# Html_Cache__Storage_Factory - Factory for creating per-layer storage instances
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id    import Safe_Str__Id
from phase_e.storage.backends.Perf__Storage__Cache_Service                         import Perf__Storage__Cache_Service
from phase_e.storage.cache_service.Cache_Service__Client                           import Cache_Service__Client
from phase_e.storage.schemas.Schema__Perf__Storage__Config                         import Schema__Perf__Storage__Config
from phase_e.storage.safe_str.Safe_Str__Session_Name                               import Safe_Str__Session_Name
from phase_e.storage.safe_str.Safe_Str__Target_Name                                import Safe_Str__Target_Name
from phase_e.storage.safe_str.Safe_Str__Data_File_Id                               import Safe_Str__Data_File_Id


# Layer to file_id mapping
LAYER_FILE_IDS = {
    'L0': 'L0-url-metadata',
    'L1': 'L1-raw-html',
    'L2': 'L2-html-dict',
    'L3': 'L3-mgraph-document',
}


class Html_Cache__Storage_Factory(Type_Safe):
    """Factory for creating per-layer storage instances."""
    
    config       : Schema__Perf__Storage__Config                    # Storage configuration
    cache_client : Cache_Service__Client                            # Cache service client
    session_name : Safe_Str__Session_Name                           # Current session

    # ═══════════════════════════════════════════════════════════════════════════
    # Public Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def create_for_layer(self                                  , 
                         layer_name  : Safe_Str__Id            ,
                         target_name : Safe_Str__Target_Name   ) -> Perf__Storage__Cache_Service:
        """Create storage instance for specific layer and target."""
        file_id = self._layer_to_file_id(layer_name)
        
        return Perf__Storage__Cache_Service(
            config       = self.config,
            client       = self.cache_client,
            session_name = self.session_name,
            target_name  = target_name
        )

    def create_all_layers(self                                ,
                          target_name : Safe_Str__Target_Name ) -> dict:
        """Create storage instances for all layers."""
        return {
            'L0': self.create_for_layer(Safe_Str__Id('L0'), target_name),
            'L1': self.create_for_layer(Safe_Str__Id('L1'), target_name),
            'L2': self.create_for_layer(Safe_Str__Id('L2'), target_name),
            'L3': self.create_for_layer(Safe_Str__Id('L3'), target_name),
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # Private Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _layer_to_file_id(self, layer_name: Safe_Str__Id) -> Safe_Str__Data_File_Id:
        """Convert layer name to file_id."""
        file_id = LAYER_FILE_IDS.get(str(layer_name), f'{layer_name}-data')
        return Safe_Str__Data_File_Id(file_id)
