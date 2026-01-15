# ═══════════════════════════════════════════════════════════════════════════════
# Html_Cache__Document - Manages cached HTML document state
# The root document serves as the state manager for all transformations
# ═══════════════════════════════════════════════════════════════════════════════
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.safe_str.Safe_Str__LETS__Name      import Safe_Str__LETS__Name
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Status       import Schema__LETS__Status
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now                import Timestamp_Now
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                  import type_safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id                 import Safe_Str__Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace          import Safe_Str__Namespace
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Json__Field_Path   import Safe_Str__Json__Field_Path
from mgraph_ai_service_html_graph.service.cache_storage.safe_str.Safe_Str__Cache_Key            import Safe_Str__Cache_Key
from mgraph_ai_service_html_graph.service.cache_storage.safe_str.Safe_Str__Data_File_Id         import Safe_Str__Data_File_Id
from mgraph_ai_service_html_graph.service.cache_storage.safe_str.Safe_Str__Layer_Name           import Safe_Str__Layer_Name
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                      import Html_Cache__Client
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Layer                       import Html_Cache__Layer
from mgraph_ai_service_html_graph.service.cache_storage.schemas.Schema__Html_Cache__Root        import Schema__Html_Cache__Root
from mgraph_ai_service_html_graph.service.cache_storage.schemas.Schema__Html_Cache__Entry       import Schema__Html_Cache__Entry


class Html_Cache__Document(Type_Safe):                                           # Cached document manager
    client     : Html_Cache__Client                                              # Cache service client
    namespace  : Safe_Str__Namespace                                             # Cache namespace
    cache_key  : Safe_Str__Cache_Key                                             # Semantic path
    file_id    : Safe_Str__Data_File_Id = 'html-entry'                           # Root document name
    cache_id   : Safe_Str__Id           = None                                   # Resolved cache ID
    root       : Schema__Html_Cache__Root = None                                 # Loaded root document

    # ═══════════════════════════════════════════════════════════════════════════
    # Cache ID Resolution
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def ensure_cache_id(self) -> Safe_Str__Id:                                   # Get or create cache_id
        if self.cache_id:
            return self.cache_id

        # Try to find existing entry by cache_key
        self.cache_id = self.client.cache_id__from_key(namespace = self.namespace,
                                                       cache_key = self.cache_key)
        if self.cache_id is None:
            self.cache_id = self.create_entry()

        return self.cache_id

    @type_safe
    def create_entry(self) -> Safe_Str__Id:                                      # Create new cache entry
        entry    = Schema__Html_Cache__Entry(cache_key = self.cache_key)
        response = self.client.entry__store(namespace       = self.namespace                       ,
                                            cache_key       = self.cache_key                       ,
                                            file_id         = self.file_id                         ,
                                            json_field_path = Safe_Str__Json__Field_Path('cache_key'),
                                            entry           = entry                                )
        if response and response.cache_id:
            return response.cache_id
        return None

    # ═══════════════════════════════════════════════════════════════════════════
    # Root Document Management
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def load_root(self) -> Schema__Html_Cache__Root:                             # Load root from cache
        if self.root:
            return self.root

        cache_id = self.ensure_cache_id()
        if cache_id:
            data = self.client.entry__retrieve(namespace = self.namespace,
                                               cache_id  = cache_id      )
            if data:
                self.root = Schema__Html_Cache__Root.from_json(data)
                return self.root

        # Create new root document
        self.root = Schema__Html_Cache__Root(cache_key  = self.cache_key)
        return self.root

    @type_safe
    def save_root(self) -> bool:                                                 # Save root to cache
        if self.root is None:
            return False
        self.root.updated_at = Timestamp_Now()
        return self.client.entry__update(namespace = self.namespace        ,
                                         cache_id  = self.ensure_cache_id(),
                                         entry     = self.root             )

    # ═══════════════════════════════════════════════════════════════════════════
    # LETS Status Management
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def update_lets_status(self,                                                 # Update LETS status
                           status: Schema__LETS__Status
                      ) -> bool:
        root = self.load_root()
        root.transformations[status.name] = status
        return self.save_root()

    @type_safe
    def get_lets_status(self,                                                    # Get LETS status
                        name: Safe_Str__LETS__Name
                   ) -> Schema__LETS__Status:                                    # Returns None if not found
        root = self.load_root()
        return root.transformations.get(name)

    # ═══════════════════════════════════════════════════════════════════════════
    # Layer Access
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def layer(self,                                                              # Get layer accessor
              layer_name: Safe_Str__Layer_Name
         ) -> Html_Cache__Layer:
        return Html_Cache__Layer(document   = self      ,
                                 layer_name = layer_name)

    # ═══════════════════════════════════════════════════════════════════════════
    # Status Query
    # ═══════════════════════════════════════════════════════════════════════════

    def layer_status(self) -> dict:                                              # Check which layers cached
        root   = self.load_root()
        status = {}
        for name, lets_status in root.transformations.items():
            status[name] = lets_status.completed if lets_status else False
        return status

    def delete(self) -> bool:                                                    # Delete entire document
        cache_id = self.ensure_cache_id()
        if cache_id:
            return self.client.entry__delete(namespace = self.namespace,
                                             cache_id  = cache_id      )
        return False

    def exists(self) -> bool:                                                    # Check if document exists
        if self.cache_id:
            return self.client.entry__exists(namespace = self.namespace,
                                             cache_id  = self.cache_id )
        cache_id = self.client.cache_id__from_key(namespace = self.namespace,
                                                  cache_key = self.cache_key)
        return cache_id is not None
