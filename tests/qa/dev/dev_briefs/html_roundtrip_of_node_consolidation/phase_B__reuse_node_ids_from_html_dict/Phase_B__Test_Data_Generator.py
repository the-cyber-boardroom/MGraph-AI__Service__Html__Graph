# ═══════════════════════════════════════════════════════════════════════════════
# Phase_B__Test_Data_Generator - Generate test fixtures for Phase C
# Run this in Phase B context to create JSON files Phase C can consume
# ═══════════════════════════════════════════════════════════════════════════════

import json
from pathlib                                        import Path
from Html__To__Html_Dict__With__Node_Ids            import Html__To__Html_Dict__With__Node_Ids
from Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse
from osbot_utils.testing.Graph__Deterministic__Ids import graph_deterministic_ids

# ═══════════════════════════════════════════════════════════════════════════════
# Test HTML Samples
# ═══════════════════════════════════════════════════════════════════════════════

HTML_SAMPLES = {
    'simple': "<html><body><div>Hello <b>World</b>!</div></body></html>",

    'multiple_wrappers': "<html><body><p>Start <a>link</a> middle <b>bold</b> end</p></body></html>",

    'nested_structure': """\
<!DOCTYPE html>
<html>
    <body>
        <div>
            This is a <a href="">link</a> with some <b>bold</b> in the mix
        </div>
        <div>
            this is the <i>2nd div</i> in here
        </div>
    </body>
</html>
"""
}


def generate_test_fixture(html: str, name: str) -> dict:
    """Generate a complete test fixture from HTML.

    Returns dict containing:
    - html: Original HTML string
    - html_dict: Parsed dict with node_ids (Phase A output)
    - body_graph_json: Serialized body MGraph (Phase B output)
    """
    # Phase A: Parse to dict with node_ids
    html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()

    # Phase B: Convert to MGraph
    doc = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)

    # Serialize body graph
    #body_graph_json = doc.body_graph.to_json()
    #body_graph_json = doc.body_graph.mgraph.export().to__mgraph_json()
    body_graph_json = doc.body_graph.mgraph.json()


    return {
        'name'           : name,
        'html'           : html,
        'html_dict'      : html_dict,
        'body_graph_json': body_graph_json
    }


def generate_all_fixtures(output_dir: str = None) -> dict:
    """Generate fixtures for all HTML samples.

    Args:
        output_dir: If provided, write JSON files to this directory

    Returns:
        Dict of all fixtures keyed by name
    """
    fixtures = {}

    for name, html in HTML_SAMPLES.items():
        with graph_deterministic_ids():
            fixture = generate_test_fixture(html, name)
            fixtures[name] = fixture

            if output_dir:
                output_path = Path(output_dir) / f'fixture__{name}.json'
                with open(output_path, 'w') as f:
                    json.dump(fixture, f, indent=2, default=str)
                print(f"Generated: {output_path}")

    return fixtures



# ═══════════════════════════════════════════════════════════════════════════════
# Main - Run to generate fixtures
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':

    # Also generate JSON files for inspection
    generate_all_fixtures('.')