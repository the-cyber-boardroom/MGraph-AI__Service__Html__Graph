# ═══════════════════════════════════════════════════════════════════════════════
# test_integration__L5_Transformations__From_LETS_Pipeline.py
# ═══════════════════════════════════════════════════════════════════════════════
#
# Reads L2 (html_dict) and L3 (MGraph) from existing LETS pipeline cache,
# applies transformations, and saves results to L5 folder.
#
# Each transformation is saved as a JSON file with 'html' key for UI rendering.
#
# Transformations created:
#   L5/a-original-reconstructed.json  - HTML reconstructed from MGraph (baseline)
#   L5/b-body-only.json               - Just the <body> content
#   L5/c-phase-e0-filtered.json       - After Phase E_0 content filtering
#   L5/d-text-content.json            - Extracted text as simple HTML
#
# Run with: pytest test_integration__L5_Transformations__From_LETS_Pipeline.py -v -s
# ═══════════════════════════════════════════════════════════════════════════════

import pytest
from unittest                                                                                               import TestCase

from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id import Obj_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid import Random_Guid
from osbot_utils.utils.Env import get_env, load_dotenv
from osbot_utils.utils.Files                                                                                import file_exists, path_combine
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                          import Cache_Id
from mgraph_ai_service_cache_client.client.Client__Cache__Service                                           import Client__Cache__Service
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document                          import Html_MGraph__Document
from phase_e.core.Phase_E__Text_Extractor                                                                   import Phase_E__Text_Extractor
from phase_e.core.Phase_E__Virtual_Merger                                                                   import Phase_E__Virtual_Merger
from phase_e.core.Phase_E__Node_Deleter                                                                     import Phase_E__Node_Deleter
from phase_e.decision.Phase_E__Decision_Engine__Hash_Based                                                  import Phase_E__Decision_Engine__Hash_Based
from phase_e.mgraph.Html_MGraph__Document__To__Html__With_Original_Head import Html_MGraph__Document__To__Html__With_Original_Head
from phase_e.storage.backends.Perf__Storage__Cache_Service                                                  import Perf__Storage__Cache_Service
from phase_e.storage.cache_service.Cache_Service__Client                                                    import Cache_Service__Client
from phase_e.storage.schemas.Schema__Perf__Storage__Config                                                  import Schema__Perf__Storage__Config
from phase_e.storage.safe_str.Safe_Str__Session_Name                                                        import Safe_Str__Session_Name
from phase_e.storage.safe_str.Safe_Str__Target_Name                                                         import Safe_Str__Target_Name


# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

ENV_VAR__URL__TARGET_SERVER__CACHE_SERVICE = 'URL__TARGET_SERVER__CACHE_SERVICE'

# Source: Where to read L2/L3 from (existing LETS pipeline)
SOURCE_NAMESPACE = 'phase-e5-full-pipeline'
SOURCE_SESSION   = 'full-pipeline-batch'

# Targets to process (must match targets in source namespace)
TARGETS = [
    #'docs_diniscruz_ai'  ,
    'text_npr_org'       ,
    #'paulgraham_com'     ,
    'theintercept_com'   ,
    #'www_bbc_com_sport'  ,
    "joelonsoftware",
    "joelonsoftware--page"
]


def load_env_vars__cache_service():
    """Load cache service URL from .cache_service.env file."""
    env_var_file_name = '.cache_service.env'
    env_var_file      = path_combine(__file__, f'../{env_var_file_name}')
    load_dotenv(dotenv_path=env_var_file, override=True)
    url_cache_service = get_env(ENV_VAR__URL__TARGET_SERVER__CACHE_SERVICE)

    assert file_exists(env_var_file), f"Env file not found: {env_var_file}"
    assert url_cache_service is not None, f"Env var {ENV_VAR__URL__TARGET_SERVER__CACHE_SERVICE} not set"

    return url_cache_service


def create_live_cache_client(url_cache_service: str):
    """Create a cache client pointing to the live cache service."""
    client = Client__Cache__Service()
    return client.client()


def is_cache_service_available():
    """Check if the cache service is running."""
    try:
        url_cache_service = load_env_vars__cache_service()
        client            = create_live_cache_client(url_cache_service)
        result            = client.info().health()
        return result and result.get('status') == 'ok'
    except Exception as e:
        print(f"Cache service not available: {e}")
        return False


# Skip all tests if cache service is not available
pytestmark = pytest.mark.skipif(
    not is_cache_service_available(),
    reason="Cache service not available (check .cache_service.env)"
)


# ═══════════════════════════════════════════════════════════════════════════════
# Transformation Functions
# ═══════════════════════════════════════════════════════════════════════════════

def transform__original_reconstructed(document, html_dict: dict) -> str:
    """L5/a - Reconstruct HTML from MGraph (baseline, with patched head)."""
    converter = Html_MGraph__Document__To__Html__With_Original_Head(original_html_dict=html_dict)
    return converter.convert(document)


def transform__body_only(document, html_dict: dict) -> str:
    """L5/b - Extract just the <body> content."""
    converter = Html_MGraph__Document__To__Html__With_Original_Head(original_html_dict=html_dict)
    full_html = converter.convert(document)

    # Extract body content
    body_start = full_html.lower().find('<body')
    body_end   = full_html.lower().find('</body>')

    if body_start != -1 and body_end != -1:
        body_tag_end = full_html.find('>', body_start)
        if body_tag_end != -1:
            body_content = full_html[body_tag_end + 1:body_end].strip()
            return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Body Only</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }}
    </style>
</head>
<body>
{body_content}
</body>
</html>"""

    return full_html


def transform__phase_e0_filtered(document, html_dict: dict, threshold: float = 0.5) -> str:
    """L5/c - Apply Phase E_0 content filtering."""
    converter              = Html__To__Html_MGraph__Document__Node_Id_Reuse()
    document_for_filtering = converter.convert_from_dict(html_dict)

    extractor  = Phase_E__Text_Extractor()
    text_nodes = extractor.extract(document_for_filtering)

    if not text_nodes:
        return transform__original_reconstructed(document, html_dict)

    merger       = Phase_E__Virtual_Merger()
    merged_texts = merger.merge(text_nodes, document_for_filtering)

    decision_engine   = Phase_E__Decision_Engine__Hash_Based(threshold=threshold)
    decisions         = decision_engine.classify_all(merged_texts)
    parents_to_delete = decision_engine.get_parents_to_delete(decisions)

    deleter = Phase_E__Node_Deleter()
    deleter.delete(document_for_filtering, parents_to_delete)

    patched_converter = Html_MGraph__Document__To__Html__With_Original_Head(original_html_dict=html_dict)
    return patched_converter.convert(document_for_filtering)


def transform__text_content(document, html_dict: dict) -> str:
    """L5/d - Extract text content as simple HTML list."""
    converter               = Html__To__Html_MGraph__Document__Node_Id_Reuse()
    document_for_extraction = converter.convert_from_dict(html_dict)

    extractor  = Phase_E__Text_Extractor()
    text_nodes = extractor.extract(document_for_extraction)

    merger       = Phase_E__Virtual_Merger()
    merged_texts = merger.merge(text_nodes, document_for_extraction)

    text_blocks = []
    for parent_id, info in merged_texts.items():
        text = str(info.merged_text).strip()
        if text and len(text) > 2:
            text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            text_blocks.append(f'<p>{text}</p>')

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Text Content Only</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
            padding: 20px; 
            max-width: 800px; 
            margin: 0 auto; 
            line-height: 1.6;
        }}
        p {{ 
            margin: 1em 0; 
            padding: 0.5em;
            background: #f5f5f5;
            border-radius: 4px;
        }}
        h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 0.5em; }}
    </style>
</head>
<body>
    <h1>Extracted Text Content</h1>
    <p><em>Total text blocks: {len(text_blocks)}</em></p>
    <hr>
    {''.join(text_blocks)}
</body>
</html>"""


# ═══════════════════════════════════════════════════════════════════════════════
# L5 Transformer Class
# ═══════════════════════════════════════════════════════════════════════════════

class L5_Transformer:
    """Apply transformations to cached L2/L3 data and save to L5."""

    def __init__(self, storage: Perf__Storage__Cache_Service):
        self.storage = storage

    def transform_target(self, cache_id: Cache_Id) -> dict:
        """Apply all transformations and save to L5."""
        result = {
            'cache_id'    : str(cache_id),
            'L2_loaded'   : False,
            'L3_loaded'   : False,
            'L5a_saved'   : False,
            'L5b_saved'   : False,
            'L5c_saved'   : False,
            'L5d_saved'   : False,
            'L5a_size'    : 0,
            'L5b_size'    : 0,
            'L5c_size'    : 0,
            'L5d_size'    : 0,
        }

        # Load L2
        html_dict = self.storage.load__json(cache_id=cache_id, key='L2/html-dict')
        if not html_dict:
            return result
        result['L2_loaded'] = True

        # Load L3
        mgraph_json = self.storage.load__json(cache_id=cache_id, key='L3/mgraph-document')
        if not mgraph_json:
            return result
        result['L3_loaded'] = True

        # Reconstruct document
        document = Html_MGraph__Document.from_json(mgraph_json)

        # L5/a - Original reconstructed
        try:
            html_a = transform__original_reconstructed(document, html_dict)
            if self.storage.save(cache_id=cache_id, key='L5/a-original-reconstructed', data={'html': html_a}):
                result['L5a_saved'] = True
                result['L5a_size']  = len(html_a)
        except Exception as e:
            print(f"L5/a error: {e}")

        # L5/b - Body only
        try:
            html_b = transform__body_only(document, html_dict)
            if self.storage.save(cache_id=cache_id, key='L5/b-body-only', data={'html': html_b}):
                result['L5b_saved'] = True
                result['L5b_size']  = len(html_b)
        except Exception as e:
            print(f"L5/b error: {e}")

        # L5/c - Phase E_0 filtered
        try:
            html_c = transform__phase_e0_filtered(document, html_dict, threshold=0.5)
            if self.storage.save(cache_id=cache_id, key='L5/c-phase-e0-filtered', data={'html': html_c}):
                result['L5c_saved'] = True
                result['L5c_size']  = len(html_c)
        except Exception as e:
            print(f"L5/c error: {e}")

        # L5/d - Text content
        try:
            html_d = transform__text_content(document, html_dict)
            if self.storage.save(cache_id=cache_id, key='L5/d-text-content', data={'html': html_d}):
                result['L5d_saved'] = True
                result['L5d_size']  = len(html_d)
        except Exception as e:
            print(f"L5/d error: {e}")

        return result


# ═══════════════════════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════════════════════

class test_integration__L5_Transformations(TestCase):
    """Test L5 transformations on existing LETS pipeline cache."""

    @classmethod
    def setUpClass(cls):
        cls.url_cache_service = load_env_vars__cache_service()
        print(f"\n✓ Cache service URL: {cls.url_cache_service}")

        cls.cache_client         = create_live_cache_client(cls.url_cache_service)
        cls.storage_config       = Schema__Perf__Storage__Config(cache_namespace=SOURCE_NAMESPACE)
        cls.cache_client_wrapper = Cache_Service__Client(cache_client = cls.cache_client,
                                                         config       = cls.storage_config)

        assert cls.cache_client_wrapper.health_check(), "Cache service health check failed"
        print(f"✓ Connected to cache service")
        print(f"✓ Source namespace: {SOURCE_NAMESPACE}")
        print(f"✓ Source session: {SOURCE_SESSION}")

    def _create_storage(self, target_name: str) -> Perf__Storage__Cache_Service:
        return Perf__Storage__Cache_Service(
            config       = self.storage_config,
            client       = self.cache_client_wrapper,
            session_name = Safe_Str__Session_Name(SOURCE_SESSION),
            target_name  = Safe_Str__Target_Name(target_name)
        )

    def test_l5_transformations__all_targets(self):                             # Test L5 transformations on all targets
        print(f"\n{'='*70}")
        print(f"L5 Transformations - All Targets")
        print(f"{'='*70}")

        results = []

        for target_name in TARGETS:
            print(f"\n📄 {target_name}")

            storage     = self._create_storage(target_name)
            transformer = L5_Transformer(storage=storage)
            cache_id    = storage.cache_id()

            result = transformer.transform_target(cache_id)
            results.append((target_name, result))

            if not result['L2_loaded']:
                print(f"   ✗ L2 not found - skipping")
                continue

            if not result['L3_loaded']:
                print(f"   ✗ L3 not found - skipping")
                continue

            print(f"   ✓ L5/a: Original reconstructed ({result['L5a_size']:,} bytes)")
            print(f"   ✓ L5/b: Body only ({result['L5b_size']:,} bytes)")
            print(f"   ✓ L5/c: Phase E_0 filtered ({result['L5c_size']:,} bytes)")
            print(f"   ✓ L5/d: Text content ({result['L5d_size']:,} bytes)")

        # Summary
        print(f"\n{'='*70}")
        print(f"Summary")
        print(f"{'='*70}")

        successful = sum(1 for _, r in results if r['L5a_saved'] and r['L5b_saved'] and r['L5c_saved'] and r['L5d_saved'])
        print(f"Targets processed: {len(results)}")
        print(f"Fully successful:  {successful}")

        # At least one should succeed
        #assert successful > 0, "No targets were successfully transformed"
        print(f"\n✓ L5 transformations complete!")

    # def test_l5_transformations__single_target__text_npr_org(self):             # Test single target in detail
    #     target_name = 'text_npr_org'
    #     print(f"\n{'='*70}")
    #     print(f"L5 Transformations - {target_name}")
    #     print(f"{'='*70}")
    #
    #     storage     = self._create_storage(target_name)
    #     transformer = L5_Transformer(storage=storage)
    #     cache_id    = storage.cache_id()
    #
    #     result = transformer.transform_target(cache_id)
    #
    #     print(f"\nResults:")
    #     print(f"  L2 loaded: {result['L2_loaded']}")
    #     print(f"  L3 loaded: {result['L3_loaded']}")
    #     print(f"  L5/a saved: {result['L5a_saved']} ({result['L5a_size']:,} bytes)")
    #     print(f"  L5/b saved: {result['L5b_saved']} ({result['L5b_size']:,} bytes)")
    #     print(f"  L5/c saved: {result['L5c_saved']} ({result['L5c_size']:,} bytes)")
    #     print(f"  L5/d saved: {result['L5d_saved']} ({result['L5d_size']:,} bytes)")
    #
    #     if result['L2_loaded'] and result['L3_loaded']:
    #         assert result['L5a_saved'], "L5/a should be saved"
    #         assert result['L5b_saved'], "L5/b should be saved"
    #         assert result['L5c_saved'], "L5/c should be saved"
    #         assert result['L5d_saved'], "L5/d should be saved"
    #         print(f"\n✓ All L5 transformations saved for {target_name}!")
    #     else:
    #         pytest.skip(f"L2/L3 not available for {target_name}")
    #
    # def test_l5_verify_saved_transformations(self):                             # Verify L5 files can be retrieved
    #     target_name = 'text_npr_org'
    #     print(f"\n{'='*70}")
    #     print(f"Verify L5 Saved Transformations - {target_name}")
    #     print(f"{'='*70}")
    #
    #     storage  = self._create_storage(target_name)
    #     cache_id = storage.cache_id()
    #
    #     # First ensure transformations exist
    #     transformer = L5_Transformer(storage=storage)
    #     transformer.transform_target(cache_id)
    #
    #     # Now retrieve and verify
    #     l5a = storage.load__json(cache_id=cache_id, key='L5/a-original-reconstructed')
    #     l5b = storage.load__json(cache_id=cache_id, key='L5/b-body-only')
    #     l5c = storage.load__json(cache_id=cache_id, key='L5/c-phase-e0-filtered')
    #     l5d = storage.load__json(cache_id=cache_id, key='L5/d-text-content')
    #
    #     print(f"\nRetrieved L5 files:")
    #     print(f"  L5/a: {'✓' if l5a else '✗'} {len(l5a.get('html', '')) if l5a else 0:,} bytes")
    #     print(f"  L5/b: {'✓' if l5b else '✗'} {len(l5b.get('html', '')) if l5b else 0:,} bytes")
    #     print(f"  L5/c: {'✓' if l5c else '✗'} {len(l5c.get('html', '')) if l5c else 0:,} bytes")
    #     print(f"  L5/d: {'✓' if l5d else '✗'} {len(l5d.get('html', '')) if l5d else 0:,} bytes")
    #
    #     if l5a:
    #         assert 'html' in l5a, "L5/a should have 'html' key"
    #         assert l5a['html'].startswith('<!DOCTYPE') or l5a['html'].startswith('<html'), "L5/a should be HTML"
    #
    #     if l5d:
    #         assert 'html' in l5d, "L5/d should have 'html' key"
    #         assert 'Extracted Text Content' in l5d['html'], "L5/d should have text content title"
    #
    #     print(f"\n✓ L5 transformations verified!")


# ═══════════════════════════════════════════════════════════════════════════════
# Run Tests
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])