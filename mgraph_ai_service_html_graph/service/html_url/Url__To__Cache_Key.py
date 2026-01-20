# ═══════════════════════════════════════════════════════════════════════════════
# Url__To__Cache_Key - Converts URLs to hierarchical cache keys
# ═══════════════════════════════════════════════════════════════════════════════

import re
from urllib.parse                                                                               import urlparse, parse_qs, urlencode
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__Cache_Key     import Safe_Str__Cache__File__Cache_Key
from mgraph_ai_service_html_graph.schemas.flet.url.Schema__Url__Cache_Key__Config               import Schema__Url__Cache_Key__Config
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                        import Safe_Str__Url
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                  import type_safe
from osbot_utils.helpers.cache.Cache__Hash__Generator                                           import Cache__Hash__Generator



class Url__To__Cache_Key(Type_Safe):
    config         : Schema__Url__Cache_Key__Config                             # Config (auto-created with defaults)
    hash_generator : Cache__Hash__Generator                                     # Hash generator (auto-created)

    @type_safe
    def cache_key(self, url: Safe_Str__Url) -> Safe_Str__Cache__File__Cache_Key:
        parsed    = urlparse(url)
        domain    = parsed.netloc
        path      = self.sanitize_path(parsed.path)
        cache_key = f"{domain}/{path}"

        if self.config.include_query_params and parsed.query:
            query_part = self.process_query(parsed.query)
            if query_part:
                cache_key = f"{cache_key}/{query_part}"

        return cache_key

    def sanitize_path(self, path: str) -> str:
        path = path.strip('/')
        if not path:
            return 'index'
        sanitized = re.sub(r'[^a-zA-Z0-9\-_/.]', '-', path)                     # Allow dots for file extensions
        sanitized = re.sub(r'-+', '-', sanitized)                               # Collapse consecutive hyphens
        sanitized = re.sub(r'-*/-*', '/', sanitized)                            # Clean hyphens around slashes
        return sanitized.strip('-')

    def process_query(self, query: str) -> str:
        params = parse_qs(query, keep_blank_values=True)

        if self.config.include_params:                                          # Whitelist mode
            params = {k: v for k, v in params.items() if k in self.config.include_params}
        elif self.config.exclude_params:                                        # Blacklist mode
            params = {k: v for k, v in params.items() if k not in self.config.exclude_params}

        if not params:
            return ''

        if self.config.sort_query_params:
            params = dict(sorted(params.items()))

        flat_params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
        query_str   = urlencode(flat_params, doseq=True)

        if self.config.query_params_as_hash:
            query_hash = self.hash_generator.from_string(query_str)
            return f"q-{query_hash[:self.config.hash_length]}"
        else:
            return self.sanitize_path(query_str)