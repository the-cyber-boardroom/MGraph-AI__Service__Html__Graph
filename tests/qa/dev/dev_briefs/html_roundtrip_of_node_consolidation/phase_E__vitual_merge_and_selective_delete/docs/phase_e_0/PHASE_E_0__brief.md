# Phase E: Virtual Merge and Selective Delete

**Status**: 📋 Planning  
**Depends On**: Phase A ✅, Phase B ✅

---

## Objective

> Extract text content from HTML, virtually compute merged text per parent element, make keep/discard decisions via a pluggable engine, then delete unwanted parent nodes from the original graph and rebuild clean HTML.

**Key Insight**: We do a **read-only analysis pass** to compute what merged text would be, make decisions on that virtual result, then **surgically delete** from the original unmodified graph. No actual merge transformation needed.

---

## The Problem

When processing HTML for content extraction (e.g., for LLM context), we need to:
1. Identify meaningful text blocks (merged from inline elements)
2. Decide which blocks to keep (eventually via ML/AI)
3. Remove unwanted content while preserving HTML structure

Previous approaches (Phase D) transformed the graph in-place. This phase takes a different approach: **analyze virtually, delete surgically**.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE E: VIRTUAL MERGE + SELECTIVE DELETE                 │
└─────────────────────────────────────────────────────────────────────────────┘

HTML String
    │
    ▼ (Phase A + B)
Html__To__Html_Dict__With__Node_Ids
    │
    ▼
Html__To__Html_MGraph__Document__Node_Id_Reuse
    │
    ▼
Html_MGraph__Document (with node_ids preserved)
    │
    │
    ├──────────────────────────────────────────────────────────────────┐
    │                                                                  │
    ▼                                                                  │
┌─────────────────────────────────────────┐                           │
│  STEP 1: Extract Text Nodes             │                           │
│                                         │                           │
│  { node_id: { text, parent_id } }       │                           │
└─────────────────────────────────────────┘                           │
    │                                                                  │
    ▼                                                                  │
┌─────────────────────────────────────────┐                           │
│  STEP 2: Virtual Merge (Read-Only)      │                           │
│                                         │                           │
│  { parent_id: {                         │                           │
│      merged_text: "Hello World!",       │                           │
│      source_node_ids: [n1, n2, n3]      │                           │
│  }}                                     │                           │
└─────────────────────────────────────────┘                           │
    │                                                                  │
    ▼                                                                  │
┌─────────────────────────────────────────┐                           │
│  STEP 3: Decision Engine                │                           │
│  (Pluggable: Hash-based / ML / AI)      │                           │
│                                         │                           │
│  { parent_id: keep=True/False }         │                           │
└─────────────────────────────────────────┘                           │
    │                                                                  │
    ▼                                                                  │
┌─────────────────────────────────────────┐                           │
│  STEP 4: Delete Unwanted Parents        │◄──────────────────────────┘
│  (From ORIGINAL graph)                  │
│                                         │
│  mgraph.edit().delete_node(parent_id)   │
└─────────────────────────────────────────┘
    │
    ▼
Html_MGraph__Document (modified - unwanted nodes removed)
    │
    ▼ (Existing converters)
Html_MGraph__Document__To__Html
    │
    ▼
Clean HTML String
```

---

## Data Structures

### Step 1: Text Node Extraction

```python
# Input: body_graph from Html_MGraph__Document
# Output: Dict mapping node_id → text info

text_nodes = {
    'n001': { 'text': 'Hello ',  'parent_id': 'p001' },
    'n002': { 'text': 'World',   'parent_id': 'p002' },  # inside <b>
    'n003': { 'text': '!',       'parent_id': 'p001' },
}
```

### Step 2: Virtual Merge Result

```python
# Group by ultimate block-level parent, merge in order
# Output: Dict mapping parent_id → merged info

virtual_merged = {
    'p001': {                                    # <div> parent
        'merged_text'    : 'Hello World!',
        'source_node_ids': ['n001', 'n002', 'n003'],
        'source_parents' : ['p001', 'p002', 'p001'],  # For traceability
    },
    'p003': {                                    # <nav> parent
        'merged_text'    : 'Home | About | Contact',
        'source_node_ids': ['n010', 'n011', 'n012'],
        'source_parents' : ['p003', 'p003', 'p003'],
    },
}
```

### Step 3: Decision Result

```python
# Output: Dict mapping parent_id → decision

decisions = {
    'p001': { 'keep': True,  'score': 0.85, 'reason': 'content' },
    'p003': { 'keep': False, 'score': 0.23, 'reason': 'navigation' },
}
```

---

## Class Design

### Core Classes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLASS HIERARCHY                                    │
└─────────────────────────────────────────────────────────────────────────────┘

Phase_E__Text_Extractor                    Extract text nodes from body_graph
    │
    └── extract(document) → Dict[node_id, TextNodeInfo]

Phase_E__Virtual_Merger                    Compute merged text per parent
    │
    └── merge(text_nodes) → Dict[parent_id, MergedTextInfo]

Phase_E__Decision_Engine__Base             Abstract base for keep/discard decisions
    │
    ├── should_keep(merged_text, parent_id) → bool
    └── classify(merged_text, parent_id) → DecisionResult

Phase_E__Decision_Engine__Hash_Based       Deterministic hash-based (for testing)
    │
    └── Inherits Phase_E__Decision_Engine__Base

Phase_E__Node_Deleter                      Delete parent nodes from graph
    │
    └── delete(document, parent_ids) → int  # Returns count deleted

Phase_E__Pipeline                          Orchestrates full workflow
    │
    ├── process(html) → str
    └── process_document(document) → Html_MGraph__Document
```

### Type Definitions

```python
from typing import Dict, List, TypedDict
from osbot_utils.type_safe.Type_Safe import Type_Safe

class TextNodeInfo(TypedDict):
    text      : str
    parent_id : str

class MergedTextInfo(TypedDict):
    merged_text     : str
    source_node_ids : List[str]
    source_parents  : List[str]

class DecisionResult(TypedDict):
    keep   : bool
    score  : float
    reason : str
```

---

## Implementation

### Phase_E__Text_Extractor

```python
class Phase_E__Text_Extractor(Type_Safe):
    """Extract all text nodes from body_graph with their parent_id."""
    
    def extract(self, document: Html_MGraph__Document) -> Dict[str, TextNodeInfo]:
        """Extract text nodes indexed by node_id.
        
        Returns:
            { node_id: { text, parent_id } }
        """
        text_nodes  = {}
        body_graph  = document.body_graph
        
        for domain_node in body_graph.mgraph.data().nodes():
            node_path = domain_node.node.data.node_path
            
            if str(node_path) != 'text':                    # Skip non-text nodes
                continue
            
            node_id   = str(domain_node.node.data.node_id)
            text      = self._get_text_value(domain_node)
            parent_id = self._get_parent_id(body_graph, node_id)
            
            if text.strip():                                # Only non-empty text
                text_nodes[node_id] = {
                    'text'     : text,
                    'parent_id': parent_id,
                }
        
        return text_nodes
    
    def _get_text_value(self, domain_node) -> str:
        """Extract text value from node_data."""
        node_data = domain_node.node.data.node_data
        if node_data and hasattr(node_data, 'value'):
            return str(node_data.value) if node_data.value else ''
        return ''
    
    def _get_parent_id(self, body_graph, node_id: str) -> str:
        """Find parent node_id via incoming edge."""
        mgraph = body_graph.mgraph
        index  = mgraph.index()
        
        incoming_edges = index.get_node_id_incoming_edges(node_id)
        
        for edge_id in incoming_edges:
            parent_id = index.edges_index.get_edge_from_node(edge_id)
            if parent_id:
                return str(parent_id)
        
        return ''
```

### Phase_E__Virtual_Merger

```python
class Phase_E__Virtual_Merger(Type_Safe):
    """Compute merged text per parent without modifying the graph."""
    
    def merge(self, 
              text_nodes: Dict[str, TextNodeInfo],
              document: Html_MGraph__Document
             ) -> Dict[str, MergedTextInfo]:
        """Group text nodes by block-level parent and merge.
        
        Args:
            text_nodes: Output from Phase_E__Text_Extractor
            document: For traversing to find block-level parents
            
        Returns:
            { parent_id: { merged_text, source_node_ids, source_parents } }
        """
        # Group by parent
        by_parent = {}  # parent_id → list of (node_id, text, position)
        
        for node_id, info in text_nodes.items():
            parent_id = info['parent_id']
            position  = self._get_position(document, node_id)
            
            if parent_id not in by_parent:
                by_parent[parent_id] = []
            
            by_parent[parent_id].append({
                'node_id' : node_id,
                'text'    : info['text'],
                'position': position,
            })
        
        # Merge each parent's text children
        merged = {}
        
        for parent_id, children in by_parent.items():
            # Sort by position for correct order
            sorted_children = sorted(children, key=lambda x: x['position'])
            
            merged[parent_id] = {
                'merged_text'    : ''.join(c['text'] for c in sorted_children),
                'source_node_ids': [c['node_id'] for c in sorted_children],
                'source_parents' : [parent_id] * len(sorted_children),
            }
        
        return merged
    
    def _get_position(self, document: Html_MGraph__Document, node_id: str) -> int:
        """Get position from edge_path."""
        body_graph = document.body_graph
        mgraph     = body_graph.mgraph
        index      = mgraph.index()
        
        incoming_edges = index.get_node_id_incoming_edges(node_id)
        
        for edge_id in incoming_edges:
            edge_data = mgraph.data().edge(edge_id)
            if edge_data and hasattr(edge_data, 'edge_path'):
                try:
                    return int(str(edge_data.edge_path))
                except (ValueError, TypeError):
                    pass
        
        return 0
```

### Phase_E__Decision_Engine__Base

```python
from abc import abstractmethod

class Phase_E__Decision_Engine__Base(Type_Safe):
    """Abstract base class for content keep/discard decisions.
    
    Subclasses implement the actual decision logic:
    - Hash-based (deterministic, for testing)
    - ML-based (trained classifier)
    - LLM-based (prompt-based classification)
    """
    
    @abstractmethod
    def should_keep(self, merged_text: str, parent_id: str) -> bool:
        """Simple keep/discard decision.
        
        Args:
            merged_text: The merged text content
            parent_id: The parent element's node_id
            
        Returns:
            True to keep, False to discard
        """
        raise NotImplementedError
    
    @abstractmethod
    def classify(self, merged_text: str, parent_id: str) -> DecisionResult:
        """Detailed classification with score and reason.
        
        Args:
            merged_text: The merged text content
            parent_id: The parent element's node_id
            
        Returns:
            DecisionResult with keep, score, and reason
        """
        raise NotImplementedError
    
    def classify_all(self, 
                     merged_texts: Dict[str, MergedTextInfo]
                    ) -> Dict[str, DecisionResult]:
        """Classify all merged texts.
        
        Args:
            merged_texts: Output from Phase_E__Virtual_Merger
            
        Returns:
            { parent_id: DecisionResult }
        """
        decisions = {}
        
        for parent_id, info in merged_texts.items():
            decisions[parent_id] = self.classify(info['merged_text'], parent_id)
        
        return decisions
```

### Phase_E__Decision_Engine__Hash_Based

```python
from hashlib import md5

class Phase_E__Decision_Engine__Hash_Based(Phase_E__Decision_Engine__Base):
    """Deterministic hash-based decision engine for testing.
    
    Uses MD5 hash of text to generate a deterministic score.
    Same text always produces same decision.
    
    Similar pattern to Semantic_Text__Engine__Hash_Based.
    """
    
    threshold: float = 0.5  # Score above this → keep
    
    def should_keep(self, merged_text: str, parent_id: str) -> bool:
        """Hash-based keep decision."""
        result = self.classify(merged_text, parent_id)
        return result['keep']
    
    def classify(self, merged_text: str, parent_id: str) -> DecisionResult:
        """Generate deterministic classification from hash."""
        score = self._hash_score(merged_text)
        keep  = score >= self.threshold
        
        return {
            'keep'  : keep,
            'score' : score,
            'reason': 'hash_above_threshold' if keep else 'hash_below_threshold',
        }
    
    def _hash_score(self, text: str) -> float:
        """Generate deterministic score from text hash.
        
        Same algorithm as Semantic_Text__Engine__Hash_Based.
        """
        full_hash = md5(text.encode()).hexdigest()
        hash_int  = int(full_hash[:16], 16)
        score     = (hash_int % 10000) / 10000.0
        
        return score
```

### Phase_E__Node_Deleter

```python
class Phase_E__Node_Deleter(Type_Safe):
    """Delete parent nodes from body_graph."""
    
    def delete(self, 
               document: Html_MGraph__Document, 
               parent_ids: List[str]
              ) -> int:
        """Delete parent nodes and their subtrees.
        
        Args:
            document: The Html_MGraph__Document to modify
            parent_ids: List of parent node_ids to delete
            
        Returns:
            Number of nodes deleted
        """
        deleted_count = 0
        body_graph    = document.body_graph.mgraph
        
        for parent_id in parent_ids:
            try:
                body_graph.edit().delete_node(parent_id)
                deleted_count += 1
            except Exception:
                pass  # Node might already be deleted (nested)
        
        return deleted_count
```

### Phase_E__Pipeline

```python
class Phase_E__Pipeline(Type_Safe):
    """Orchestrates the full Phase E workflow.
    
    Usage:
        # With default hash-based engine
        pipeline = Phase_E__Pipeline()
        clean_html = pipeline.process(html)
        
        # With custom engine
        pipeline = Phase_E__Pipeline(
            decision_engine=My_Custom_Engine(threshold=0.7)
        )
        clean_html = pipeline.process(html)
    """
    
    decision_engine: Phase_E__Decision_Engine__Base = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.decision_engine is None:
            self.decision_engine = Phase_E__Decision_Engine__Hash_Based()
    
    def process(self, html: str) -> str:
        """Full workflow: HTML → process → clean HTML."""
        document   = self._html_to_document(html)
        document   = self.process_document(document)
        clean_html = self._document_to_html(document)
        
        return clean_html
    
    def process_document(self, 
                         document: Html_MGraph__Document
                        ) -> Html_MGraph__Document:
        """Process document in-place."""
        
        # Step 1: Extract text nodes
        extractor  = Phase_E__Text_Extractor()
        text_nodes = extractor.extract(document)
        
        # Step 2: Virtual merge
        merger       = Phase_E__Virtual_Merger()
        merged_texts = merger.merge(text_nodes, document)
        
        # Step 3: Decision
        decisions = self.decision_engine.classify_all(merged_texts)
        
        # Step 4: Collect parents to delete
        parents_to_delete = [
            parent_id 
            for parent_id, result in decisions.items() 
            if not result['keep']
        ]
        
        # Step 5: Delete
        deleter = Phase_E__Node_Deleter()
        deleter.delete(document, parents_to_delete)
        
        return document
    
    def _html_to_document(self, html: str) -> Html_MGraph__Document:
        """Convert HTML to document using Phase A + B."""
        from Html__To__Html_Dict__With__Node_Ids import Html__To__Html_Dict__With__Node_Ids
        from Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse
        
        html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()
        document  = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)
        
        return document
    
    def _document_to_html(self, document: Html_MGraph__Document) -> str:
        """Convert document back to HTML."""
        from Html_MGraph__Document__To__Html import Html_MGraph__Document__To__Html
        
        return Html_MGraph__Document__To__Html().convert(document)
```

---

## Files to Create

| File | Purpose |
|------|---------|
| **Documentation** | |
| `PHASE_E__Virtual_Merge_And_Selective_Delete__Brief.md` | This document |
| **Implementation** | |
| `Phase_E__Text_Extractor.py` | Extract text nodes with parent_id |
| `Phase_E__Virtual_Merger.py` | Compute merged text per parent |
| `Phase_E__Decision_Engine__Base.py` | Abstract base for decisions |
| `Phase_E__Decision_Engine__Hash_Based.py` | Hash-based implementation |
| `Phase_E__Node_Deleter.py` | Delete parent nodes from graph |
| `Phase_E__Pipeline.py` | Orchestrates full workflow |
| **Tests** | |
| `test_Phase_E__Text_Extractor.py` | Unit tests |
| `test_Phase_E__Virtual_Merger.py` | Unit tests |
| `test_Phase_E__Decision_Engine__Hash_Based.py` | Unit tests |
| `test_Phase_E__Node_Deleter.py` | Unit tests |
| `test_Phase_E__Pipeline.py` | Integration tests |

### Suggested File Location

```
mgraph_ai_service_html_graph/
└── service/
    └── html_mgraph/
        └── phase_e/                              # NEW FOLDER
            ├── __init__.py
            ├── Phase_E__Text_Extractor.py
            ├── Phase_E__Virtual_Merger.py
            ├── Phase_E__Decision_Engine__Base.py
            ├── Phase_E__Decision_Engine__Hash_Based.py
            ├── Phase_E__Node_Deleter.py
            └── Phase_E__Pipeline.py
```

---

## Test Cases

### Unit Tests

| Test | Description |
|------|-------------|
| `test_extractor__simple_html` | Extract from `<div>Hello</div>` |
| `test_extractor__nested_inline` | Extract from `<div>Hello <b>World</b>!</div>` |
| `test_extractor__multiple_parents` | Multiple block elements |
| `test_extractor__empty_text_ignored` | Whitespace-only not extracted |
| `test_merger__single_parent` | Merge under one parent |
| `test_merger__preserves_order` | Text merged in correct order |
| `test_merger__multiple_parents` | Each parent gets own merge |
| `test_decision__hash_deterministic` | Same text → same result |
| `test_decision__threshold_boundary` | Score at threshold edge |
| `test_deleter__single_node` | Delete one parent |
| `test_deleter__multiple_nodes` | Delete multiple parents |
| `test_deleter__nested_safe` | Nested deletes don't error |

### Integration Tests

| Test | Description |
|------|-------------|
| `test_pipeline__simple_html` | Full workflow basic |
| `test_pipeline__keeps_high_score` | Content above threshold preserved |
| `test_pipeline__removes_low_score` | Content below threshold removed |
| `test_pipeline__preserves_structure` | Non-deleted structure intact |
| `test_pipeline__roundtrip_valid_html` | Output is valid HTML |

---

## Example Walkthrough

### Input HTML

```html
<html>
  <body>
    <div id="content">
      <p>Important article content here.</p>
    </div>
    <nav>
      <a href="/">Home</a> | <a href="/about">About</a>
    </nav>
  </body>
</html>
```

### Step 1: Extract Text Nodes

```python
{
    'n001': { 'text': 'Important article content here.', 'parent_id': 'p001' },
    'n002': { 'text': 'Home',                            'parent_id': 'a001' },
    'n003': { 'text': ' | ',                             'parent_id': 'nav1' },
    'n004': { 'text': 'About',                           'parent_id': 'a002' },
}
```

### Step 2: Virtual Merge

```python
{
    'p001': {
        'merged_text': 'Important article content here.',
        'source_node_ids': ['n001'],
        'source_parents': ['p001'],
    },
    'a001': {
        'merged_text': 'Home',
        'source_node_ids': ['n002'],
        'source_parents': ['a001'],
    },
    'nav1': {
        'merged_text': ' | ',
        'source_node_ids': ['n003'],
        'source_parents': ['nav1'],
    },
    'a002': {
        'merged_text': 'About',
        'source_node_ids': ['n004'],
        'source_parents': ['a002'],
    },
}
```

### Step 3: Decision (Hash-Based Example)

```python
{
    'p001': { 'keep': True,  'score': 0.72, 'reason': 'hash_above_threshold' },
    'a001': { 'keep': False, 'score': 0.31, 'reason': 'hash_below_threshold' },
    'nav1': { 'keep': False, 'score': 0.15, 'reason': 'hash_below_threshold' },
    'a002': { 'keep': False, 'score': 0.44, 'reason': 'hash_below_threshold' },
}
```

### Step 4: Delete

Delete nodes: `['a001', 'nav1', 'a002']`

### Step 5: Output HTML

```html
<html>
  <body>
    <div id="content">
      <p>Important article content here.</p>
    </div>
    <nav>
    </nav>
  </body>
</html>
```

(Note: `<nav>` is empty but still present because we only deleted its children's parents)

---

## Dependencies

- Phase A: `Html__To__Html_Dict__With__Node_Ids`
- Phase B: `Html__To__Html_MGraph__Document__Node_Id_Reuse`
- Existing: `Html_MGraph__Document__To__Html`
- Existing: `Html_MGraph__Document__To__Html_Dict`
- Core: `MGraph` from `mgraph_db`

---

## Success Criteria

1. ✅ Text extraction captures all text nodes with parent_id
2. ✅ Virtual merge computes correct merged text without graph modification
3. ✅ Decision engine is pluggable (base class + hash implementation)
4. ✅ Hash-based engine is deterministic (same input → same output)
5. ✅ Node deletion removes parent and subtree
6. ✅ Pipeline produces valid HTML
7. ✅ All tests pass

---

## Future Extensions

| Extension | Description |
|-----------|-------------|
| `Phase_E__Decision_Engine__ML_Based` | Trained classifier for content detection |
| `Phase_E__Decision_Engine__LLM_Based` | LLM prompt-based classification |
| Block-level parent resolution | Walk up tree to find block-level ancestor |
| Attribute-aware decisions | Use attrs_graph for class/id in decisions |
| Batch LLM classification | Classify multiple texts in single API call |

---

## Next Steps

1. Implement `Phase_E__Text_Extractor` with tests
2. Implement `Phase_E__Virtual_Merger` with tests
3. Implement decision engine base + hash-based with tests
4. Implement `Phase_E__Node_Deleter` with tests
5. Implement `Phase_E__Pipeline` with integration tests
6. Write `PHASE_E__debrief.md`
