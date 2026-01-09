# Phased Development Methodology

## A Guide to Independent, Composable Development Phases

---

## Overview

This document captures a development methodology for building complex systems through independent, composable phases. Each phase produces testable artifacts that can be validated in isolation before integration.

**Core Principle**: Build systems as a pipeline of independent transformations, where each phase's output becomes the next phase's input, connected via serializable data formats.

---

## The Phase Structure

### Each Phase Contains

```
phase_X__descriptive_name/
├── PHASE_X__brief.md           # Requirements and design decisions
├── Implementation files         # The actual code
├── test_*.py                   # Tests for this phase
├── fixture__*.json             # Test data (often from previous phase)
├── PHASE_X__debrief.md         # Learnings and completion summary
└── *__Generator.py             # Tools to create fixtures for next phase
```

### The Phase Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PHASE LIFECYCLE                              │
└─────────────────────────────────────────────────────────────────────┘

1. BRIEF PHASE
   ├── Define inputs and outputs
   ├── Specify interfaces
   ├── Document design decisions
   └── Create: PHASE_X__brief.md

2. IMPLEMENT PHASE
   ├── Write core implementation
   ├── Use subclass pattern when extending existing code
   ├── Create helper utilities
   └── Create: Implementation files

3. TEST PHASE
   ├── Load fixtures from previous phase
   ├── Validate transformations
   ├── Test edge cases
   └── Create: test_*.py files

4. FIXTURE GENERATION
   ├── Create generator for next phase
   ├── Serialize outputs as JSON
   ├── Enable deterministic IDs for reproducibility
   └── Create: *__Generator.py, fixture__*.json

5. DEBRIEF PHASE
   ├── Document what was built
   ├── Capture bugs fixed and learnings
   ├── Record architectural decisions
   └── Create: PHASE_X__debrief.md
```

---

## Key Patterns

### 1. Phase Independence via JSON Fixtures

**Problem**: Phases depend on each other's classes, creating import chains and tight coupling.

**Solution**: Serialize phase outputs to JSON. Next phase loads JSON, not classes.

```
Phase A                          Phase B
┌─────────────┐                 ┌─────────────┐
│ Process     │                 │ Load JSON   │
│ Transform   │ ──JSON file──►  │ Process     │
│ Serialize   │                 │ Transform   │
└─────────────┘                 └─────────────┘

# Phase A generates
fixture__example.json

# Phase B loads
fixture = load_fixture('example')
data = fixture['output_data']
```

**Benefits**:
- Test Phase B without Phase A classes installed
- Clear phase boundaries
- Reproducible test data
- Easy debugging (JSON is human-readable)

### 2. The Subclass Pattern

**Problem**: Need to add functionality without modifying production code.

**Solution**: Create subclass that overrides only what's needed.

```python
# Base class (UNCHANGED)
class Html_Use_Case__3:
    def transform(self, data):
        self.step_1()
        self.step_2()
        self.step_3()
        self.step_4()
    
    def step_1(self): ...
    def step_2(self): ...
    def step_3(self): ...
    def step_4(self): ...

# Subclass (NEW - adds tracking)
class Html_Use_Case__3__Source_Tracking(Html_Use_Case__3):
    def __init__(self):
        super().__init__()
        self.tracking_data = {}
    
    def step_1(self):          # Override with tracking
        # Track before
        result = super().step_1()
        # Track after
        return result
    
    # step_2, step_4 inherited unchanged
```

**Benefits**:
- Zero changes to production code
- Easy rollback (delete subclass files)
- Can use base class when feature not needed
- Clear separation of concerns

### 3. Deterministic IDs for Testing

**Problem**: Random UUIDs make tests non-reproducible and hard to debug.

**Solution**: Use deterministic ID generation in test fixtures.

```python
# Without deterministic IDs
node_ids = {'a7f3b2c1-...', 'e9d4f5a6-...', ...}  # Changes every run

# With deterministic IDs
with graph_deterministic_ids():
    fixture = generate_fixture(data)
# node_ids = {'f0000001', 'f0000002', 'f0000003', ...}  # Same every run
```

**Benefits**:
- Tests are reproducible
- Easy to write assertions on specific IDs
- Debugging is straightforward
- Can track ID relationships across phases

### 4. Fixture Generator Pattern

Each phase creates a generator for the next phase:

```python
# Phase_B__Test_Data_Generator.py

HTML_SAMPLES = {
    'simple': '<html>...</html>',
    'complex': '<html>...</html>',
}

def generate_fixture(html: str, name: str) -> dict:
    """Generate fixture for Phase C from HTML."""
    # Phase A processing
    phase_a_output = PhaseA(html).process()
    
    # Phase B processing  
    phase_b_output = PhaseB(phase_a_output).process()
    
    return {
        'name': name,
        'input': html,
        'phase_a_output': phase_a_output,
        'phase_b_output': phase_b_output.to_json()  # Serialize!
    }

def generate_all_fixtures(output_dir: str):
    """Generate all fixtures for next phase."""
    for name, html in HTML_SAMPLES.items():
        with deterministic_ids():
            fixture = generate_fixture(html, name)
        
        path = f'{output_dir}/fixture__{name}.json'
        with open(path, 'w') as f:
            json.dump(fixture, f, indent=2)
```

### 5. Fixture Loader Pattern

Each phase has a loader for its fixtures:

```python
# Phase_C__Test_Fixtures.py

FIXTURES_DIR = Path(__file__).parent
FIXTURE_NAMES = ['simple', 'complex', 'edge_case']

def _load_all_fixtures() -> dict:
    fixtures = {}
    for name in FIXTURE_NAMES:
        path = FIXTURES_DIR / f'fixture__{name}.json'
        if path.exists():
            with open(path) as f:
                fixtures[name] = json.load(f)
    return fixtures

FIXTURES = _load_all_fixtures()

def get_fixture(name: str) -> dict:
    return FIXTURES.get(name)

def list_fixtures() -> list:
    return list(FIXTURES.keys())

def print_fixtures_status():
    """Diagnostic: show which fixtures are loaded."""
    ...
```

### 6. Graceful Test Skipping

Tests skip gracefully when fixtures aren't available:

```python
class test_Phase_C(TestCase):
    
    def setUp(self):
        if len(FIXTURES) == 0:
            self.skipTest("No fixtures loaded - run Phase B generator first")
    
    def test_something(self):
        fixture = get_fixture('simple')
        # ... test code
```

---

## The Brief Document

### Structure

```markdown
# Phase X: [Descriptive Name]

**Status**: 🔄 In Progress | ✅ Complete
**Depends On**: Phase A ✅, Phase B ✅

---

## Objective

> One sentence describing what this phase achieves.

---

## The Problem

What problem does this phase solve? Include:
- Current state
- Desired state
- Why existing approaches don't work

---

## Implementation Approach

### Architecture

```
Diagram showing components and data flow
```

### Key Design Decisions

1. **Decision 1**: Rationale
2. **Decision 2**: Rationale

---

## Interfaces

### Input
- What this phase receives
- Format and structure

### Output
- What this phase produces
- Format and structure

---

## Files

| File | Purpose |
|------|---------|
| file1.py | Description |
| file2.py | Description |

---

## Test Plan

| Test | Description |
|------|-------------|
| test_1 | What it validates |
| test_2 | What it validates |
```

---

## The Debrief Document

### Structure

```markdown
# Phase X Debrief: [Descriptive Name]

**Date**: [Completion date]
**Status**: ✅ Complete
**Tests**: X/Y passing

---

## Executive Summary

Brief description of what was built and the key achievement.

---

## Architecture Decisions

Document the decisions made and why.

---

## Files Created

| File | Purpose |
|------|---------|
| ... | ... |

---

## Key Learnings & Bugs Fixed

### Bug 1: [Name]

**Problem**: What went wrong
**Symptom**: How it manifested
**Root Cause**: Why it happened
**Fix**: How it was resolved

---

## Test Coverage

Summary of tests and what they validate.

---

## Next Steps

What comes after this phase.
```

---

## JSON Serialization Guidelines

### DO serialize with full type information

```python
# Good - preserves type info for deserialization
data = obj.json()  # Full format

# Bad - loses type info
data = obj.to_json()  # Compressed format
```

### DO use standard reconstruction methods

```python
# Good
obj = MyClass.from_json(json_data)

# Bad - manual reconstruction
obj = MyClass()
for key, value in json_data['nodes'].items():
    obj.add_node(...)  # Fragile, may miss edge cases
```

### DO validate JSON format in tests

```python
def test_json_roundtrip(self):
    original = create_object()
    json_data = original.json()
    restored = MyClass.from_json(json_data)
    
    assert restored == original  # or equivalent validation
```

---

## Test Organization

### Unit Tests (per file)

```python
# test_MyClass.py
class test_MyClass(TestCase):
    
    def test_method_1__basic(self):
        ...
    
    def test_method_1__edge_case(self):
        ...
    
    def test_method_2__basic(self):
        ...
```

### Integration Tests (per phase)

```python
# test_Phase_C__Full_Pipeline_Integration.py
class test_Phase_C__Full_Pipeline_Integration(TestCase):
    
    def setUp(self):
        # Skip if fixtures not available
        if len(FIXTURES) == 0:
            self.skipTest("...")
    
    def test_1__first_stage(self):
        """Validate input processing."""
        ...
    
    def test_2__transformation(self):
        """Validate core transformation."""
        ...
    
    def test_3__output(self):
        """Validate output format."""
        ...
    
    def test_4__end_to_end(self):
        """Full pipeline validation."""
        ...
```

---

## Common Pitfalls

### 1. Importing Previous Phase Classes

**Wrong**:
```python
from Phase_A import PhaseAProcessor  # Creates dependency!
from Phase_B import PhaseBConverter
```

**Right**:
```python
from Phase_C__Test_Fixtures import get_fixture  # Load JSON instead
```

### 2. Non-Deterministic Test Data

**Wrong**:
```python
def test_something(self):
    data = generate_random_data()  # Different every run
    assert process(data) == expected  # May fail randomly
```

**Right**:
```python
def test_something(self):
    fixture = get_fixture('known_case')  # Same every run
    assert process(fixture) == expected
```

### 3. Modifying Core Classes

**Wrong**:
```python
# In production code
class CoreProcessor:
    def process(self):
        # Added tracking here for Phase C
        self.track()  # Pollutes core with phase-specific code
```

**Right**:
```python
# In Phase C
class CoreProcessor__WithTracking(CoreProcessor):
    def process(self):
        self.track()
        return super().process()
```

### 4. Compressed JSON for Serialization

**Wrong**:
```python
json_data = obj.to_json()  # Compressed, loses type info
restored = MyClass()
restored.load(json_data)  # May fail or lose data
```

**Right**:
```python
json_data = obj.json()  # Full format
restored = MyClass.from_json(json_data)  # Proper reconstruction
```

### 5. Substring Assertions

**Wrong**:
```python
assert '<b' not in html  # Catches <body> too!
```

**Right**:
```python
assert '<b>' not in html  # Specific tag
# Or use regex for more control
```

---

## Workflow Summary

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT WORKFLOW                              │
└─────────────────────────────────────────────────────────────────────┘

1. PLAN
   └── Create PHASE_X__brief.md with requirements and design

2. GENERATE FIXTURES (if depending on previous phase)
   ├── Run: python Phase_[X-1]__Test_Data_Generator.py
   └── Copy: fixture__*.json to current phase folder

3. IMPLEMENT
   ├── Create implementation files
   ├── Use subclass pattern for extensions
   └── Create helper utilities as needed

4. TEST
   ├── Write unit tests for each file
   ├── Write integration tests for phase
   └── Ensure all tests pass

5. CREATE GENERATOR (for next phase)
   ├── Create Phase_X__Test_Data_Generator.py
   ├── Generate fixture__*.json files
   └── Test that fixtures are valid

6. DOCUMENT
   └── Create PHASE_X__debrief.md with learnings

7. REPEAT for next phase
```

---

## Benefits of This Approach

| Benefit | Description |
|---------|-------------|
| **Isolation** | Each phase can be developed and tested independently |
| **Reproducibility** | Deterministic fixtures ensure consistent test results |
| **Maintainability** | Subclass pattern keeps core code clean |
| **Debuggability** | JSON fixtures are human-readable |
| **Rollback** | Easy to remove a phase without affecting others |
| **Parallelization** | Multiple phases can be worked on simultaneously |
| **Documentation** | Briefs and debriefs capture decisions and learnings |

---

## Checklist: Phase Complete

- [ ] Brief document exists and is current
- [ ] All implementation files created
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Fixtures generated for next phase
- [ ] Fixtures validated (can be loaded and used)
- [ ] Debrief document captures learnings
- [ ] No imports from previous phase classes (only fixtures)
