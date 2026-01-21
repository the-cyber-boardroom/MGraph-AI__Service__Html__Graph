from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                      import Cache_Id
from phase_e.html_cache.Html_Cache__Layer__Html                                         import Html_Cache__Layer__Html
from phase_e.html_cache.Html_Cache__Layer__Html__Dict                                   import Html_Cache__Layer__Html__Dict
from phase_e.html_cache.Html_Cache__Layer__MGraph                                       import Html_Cache__Layer__MGraph
from phase_e.html_cache.schemas.Schema__Html_Cache                                      import Schema__Html_Cache__Config, Schema__Html_Cache__Stats
from phase_e.storage.base.Perf__Storage__Base                                           import Perf__Storage__Base
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document      import Html_MGraph__Document


class Html_Cache__Manager(Type_Safe):                                   # Orchestrates all cache layers
    storage      : Perf__Storage__Base                                  # Injected storage backend
    config       : Schema__Html_Cache__Config                           # Configuration options
    stats        : Schema__Html_Cache__Stats                            # Hit/miss tracking

    # Layers (created on setup)
    layer_html   : Html_Cache__Layer__Html          = None
    layer_dict   : Html_Cache__Layer__Html__Dict    = None
    layer_mgraph : Html_Cache__Layer__MGraph        = None

    # Current target
    current_target: str = ''

    def setup(self) -> 'Html_Cache__Manager':                           # Initialize layers with manager reference
        if self.config is None:
            self.config = Schema__Html_Cache__Config()
        if self.stats is None:
            self.stats = Schema__Html_Cache__Stats()

        self.layer_html   = Html_Cache__Layer__Html         (storage=self.storage, stats=self.stats, config=self.config)
        self.layer_dict   = Html_Cache__Layer__Html__Dict   (storage=self.storage, stats=self.stats, config=self.config)
        self.layer_mgraph = Html_Cache__Layer__MGraph       (storage=self.storage, stats=self.stats, config=self.config)
        return self

    def set_target(self, target_name: str) -> 'Html_Cache__Manager':    # Set current target for all operations
        self.current_target = target_name
        self.storage.set_context(self.config.session_name, target_name)
        return self

    def get_cache_id(self) -> Cache_Id:                                 # Get or create cache_id for current target
        return self.storage.create_file__perf_entry()

    # ═══════════════════════════════════════════════════════════════════════════
    # High-level Operations
    # ═══════════════════════════════════════════════════════════════════════════

    def cache_html(self, target: str, html: str, source: str = 'unknown') -> bool:
        """Cache raw HTML for a target."""
        self.set_target(target)
        cache_id = self.get_cache_id()
        return self.layer_html.save(cache_id = cache_id,
                                    html     = html,
                                    source   = source)

    def get_html(self, target: str) -> str:                             # Get cached HTML for target
        self.set_target(target)
        cache_id = self.storage.cache_id()
        if not cache_id:
            self.stats.l1_misses += 1
            return None
        return self.layer_html.load(cache_id=cache_id)

    def get_dict(self, target: str, build_if_missing: bool = None) -> dict:
        """Get cached dict, optionally building from HTML if missing."""
        self.set_target(target)
        cache_id = self.storage.cache_id()

        if cache_id:
            # Check L2 cache
            html_dict = self.layer_dict.load(cache_id=cache_id)
            if html_dict is not None:
                return html_dict

        # Build from L1 if configured
        if build_if_missing is None:
            build_if_missing = self.config.auto_build_on_miss

        if build_if_missing:
            return self.build_dict_from_html(target)

        return None

    def get_mgraph(self, target: str, build_if_missing: bool = None) -> Html_MGraph__Document:
        """Get cached MGraph, optionally building from lower layers if missing."""
        self.set_target(target)
        cache_id = self.storage.cache_id()

        if cache_id:
            # Check L3 cache
            document = self.layer_mgraph.load(cache_id=cache_id)
            if document is not None:
                return document

        # Build from L2 if configured
        if build_if_missing is None:
            build_if_missing = self.config.auto_build_on_miss

        if build_if_missing:
            return self.build_mgraph_from_dict(target)

        return None

    # ═══════════════════════════════════════════════════════════════════════════
    # Build Operations (Cascade)
    # ═══════════════════════════════════════════════════════════════════════════

    def build_dict_from_html(self, target: str) -> dict:                # Build L2 from L1
        self.set_target(target)
        cache_id = self.storage.cache_id()
        if not cache_id:
            return None

        # Get HTML from L1
        html = self.layer_html.load(cache_id=cache_id)
        if html is None:
            return None

        # Parse to dict
        html_dict = self.layer_dict.build_from_html(html)
        if html_dict is None:
            return None

        # Cache the dict
        self.layer_dict.save(cache_id  = cache_id,
                             html_dict = html_dict)
        return html_dict

    def build_mgraph_from_dict(self, target: str) -> Html_MGraph__Document:
        """Build L3 from L2, cascading to L1 if needed."""
        self.set_target(target)

        # Get dict from L2 (which may build from L1)
        html_dict = self.get_dict(target, build_if_missing=True)
        if html_dict is None:
            return None

        # Build MGraph
        document = self.layer_mgraph.build_from_dict(html_dict)
        if document is None:
            return None

        # Cache the document
        cache_id = self.storage.cache_id()
        self.layer_mgraph.save(cache_id = cache_id,
                               document = document)
        return document

    def build_full_pipeline(self, target: str, html: str, source: str = 'unknown') -> Html_MGraph__Document:
        """Cache HTML and build full pipeline to MGraph."""
        # Cache the HTML
        if not self.cache_html(target, html, source=source):
            return None

        # Build dict from HTML
        html_dict = self.build_dict_from_html(target)
        if html_dict is None:
            return None

        # Build MGraph from dict (already cached by build_dict_from_html)
        self.set_target(target)  # Ensure target is set
        document = self.layer_mgraph.build_from_dict(html_dict)
        if document is None:
            return None

        # Cache the document
        cache_id = self.storage.cache_id()
        self.layer_mgraph.save(cache_id = cache_id,
                               document = document)
        return document

    # ═══════════════════════════════════════════════════════════════════════════
    # Cache Status Operations
    # ═══════════════════════════════════════════════════════════════════════════

    def has_html(self, target: str) -> bool:                            # Check if L1 exists for target
        self.set_target(target)
        return self.layer_html.exists()

    def has_dict(self, target: str) -> bool:                            # Check if L2 exists for target
        self.set_target(target)
        return self.layer_dict.exists()

    def has_mgraph(self, target: str) -> bool:                          # Check if L3 exists for target
        self.set_target(target)
        return self.layer_mgraph.exists()

    def cache_status(self, target: str) -> dict:                        # Get cache status for all layers
        self.set_target(target)
        return {
            'target' : target,
            'L1'     : self.layer_html.exists(),
            'L2'     : self.layer_dict.exists(),
            'L3'     : self.layer_mgraph.exists()
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # Delete Operations
    # ═══════════════════════════════════════════════════════════════════════════

    def delete_target(self, target: str) -> dict:                       # Delete all cached data for target
        self.set_target(target)
        cache_id = self.storage.cache_id()
        if not cache_id:
            return {'target': target, 'L1': False, 'L2': False, 'L3': False}
        return {
            'target' : target,
            'L1'     : self.layer_html.delete  (cache_id=cache_id),
            'L2'     : self.layer_dict.delete  (cache_id=cache_id),
            'L3'     : self.layer_mgraph.delete(cache_id=cache_id)
        }

    def delete_layer(self, target: str, layer: str) -> bool:            # Delete specific layer for target
        self.set_target(target)
        cache_id = self.storage.cache_id()
        if not cache_id:
            return False
        if layer == 'L1':
            return self.layer_html.delete(cache_id=cache_id)
        elif layer == 'L2':
            return self.layer_dict.delete(cache_id=cache_id)
        elif layer == 'L3':
            return self.layer_mgraph.delete(cache_id=cache_id)
        return False

    # ═══════════════════════════════════════════════════════════════════════════
    # Content Hash Operations
    # ═══════════════════════════════════════════════════════════════════════════

    def get_content_hash(self, target: str, layer: str) -> str:
        """Get content hash for a specific layer."""
        self.set_target(target)
        cache_id = self.storage.cache_id()
        if not cache_id:
            return None
        if layer == 'L1':
            return self.layer_html.get_content_hash(cache_id=cache_id)
        elif layer == 'L2':
            return self.layer_dict.get_content_hash(cache_id=cache_id)
        elif layer == 'L3':
            return self.layer_mgraph.get_content_hash(cache_id=cache_id)
        return None

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Operations
    # ═══════════════════════════════════════════════════════════════════════════

    def reset_stats(self):                                              # Reset all statistics
        self.stats.reset()

    def get_stats(self) -> dict:                                        # Get current statistics
        return self.stats.json()